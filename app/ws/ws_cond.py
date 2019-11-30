#  Copyright (c) 2019. Partners HealthCare and other members of
#  Forome Association
#
#  Developed by Sergey Trifonov based on contributions by Joel Krier,
#  Michael Bouzinier, Shamil Sunyaev and other members of Division of
#  Genetics, Brigham and Women's Hospital
#
#  Licensed under the Apache License, Version 2.0 (the "License");
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
#
#        http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.
#

from bitarray import bitarray

from app.filter.cond_env import CondEnv
from app.filter.unit import MetaUnit
#===============================================
class WS_CondEnv(CondEnv):
    def __init__(self, ds_h):
        CondEnv.__init__(self, ds_h.getName(), ds_h)
        self.mTotal = 0
        self.mGroups = []

    def getCondKind(self):
        return "ws"

    def addItemGroup(self, grp_size):
        self.mGroups.append((self.mTotal, grp_size))
        self.mTotal += max(1, grp_size)

    def getTotalCount(self):
        return self.mTotal

    def getGroupCount(self):
        return len(self.mGroups)

    def iterGroups(self):
        return iter(self.mGroups)

    def getGroups(self):
        return self.mGroups

    def getGroupPos(self, rec_no):
        return self.mGroups[rec_no]

    def getCondNone(self):
        return WS_None(self)

    def getCondAll(self):
        return WS_All(self)

    def addMetaNumUnit(self, name, rec_func):
        unit_h = WS_MetaNumUnit(name, rec_func)
        self.addReservedUnit(unit_h)
        return unit_h

    def makeNumericCond(self, unit_h, bounds, use_undef = None):
        eval_func = self.numericFilterFunc(bounds[0], bounds[1], use_undef)
        if unit_h.isDetailed():
            def fill_items_f(it_idx):
                return eval_func(unit_h.getItemVal(it_idx))
            fill_groups_f = None
        else:
            def fill_groups_f(rec_no):
                return eval_func(unit_h.getRecVal(rec_no))
            fill_items_f = None
        return WS_Condition(self, "num", unit_h.getName(),
            fill_groups_f = fill_groups_f, fill_items_f = fill_items_f)

    def makeEnumCond(self, unit_h, variants, filter_mode = ""):
        eval_func = self.enumFilterFunc(filter_mode,
            unit_h.getVariantSet().makeIdxSet(variants))
        if unit_h.isDetailed():
            def fill_items_f(it_idx):
                return eval_func(unit_h.getItemVal(it_idx))
            fill_groups_f = None
        else:
            def fill_groups_f(rec_no):
                return eval_func(unit_h.getRecVal(rec_no))
            fill_items_f = None
        return WS_Condition(self, "enum", unit_h.getName(),
            fill_groups_f = fill_groups_f, fill_items_f = fill_items_f)

    @staticmethod
    def numericFilterFunc(bound_min, bound_max, use_undef):
        if bound_min is None:
            if bound_max is None:
                if use_undef:
                    return lambda val: val is None
                assert False
                return lambda val: True
            if use_undef:
                return lambda val: val is None or val <= bound_max
            return lambda val: val is not None and val <= bound_max
        if bound_max is None:
            if use_undef:
                return lambda val: val is None or bound_min <= val
            return lambda val: val is not None and bound_min <= val
        if use_undef:
            return lambda val: val is None or (
                bound_min <= val <= bound_max)
        return lambda val: val is not None and (
            bound_min <= val <= bound_max)

    @staticmethod
    def enumFilterFunc(filter_mode, base_idx_set):
        if filter_mode == "NOT":
            return lambda idx_set: len(idx_set & base_idx_set) == 0
        if filter_mode == "AND":
            all_len = len(base_idx_set)
            return lambda idx_set: len(idx_set & base_idx_set) == all_len
        #if filter_mode == "ONLY":
        #    return lambda idx_set: (len(idx_set) > 0
        #        and len(idx_set - base_idx_set) == 0)
        return lambda idx_set: len(idx_set & base_idx_set) > 0

#===============================================
class WS_Condition:
    def __init__(self, cond_env, cond_type, name, bit_arr = None,
            fill_groups_f = None, fill_items_f = None):
        self.mCondEnv = cond_env
        self.mCondType = cond_type
        self.mName = name
        self.mBitArray = bit_arr
        if self.mBitArray is not None:
            assert fill_groups_f is None and fill_items_f is None
        else:
            self.mBitArray = bitarray()
            if fill_items_f is not None:
                assert fill_groups_f is None
                for grp_offset, grp_size in self.getCondEnv().iterGroups():
                    if grp_size == 0:
                        self.mBitArray.append(False)
                    else:
                        self.mBitArray.extend([fill_items_f(grp_offset + j)
                            for j in range(grp_size)])
            else:
                rec_no = 0
                for _, grp_size in self.getCondEnv().iterGroups():
                    val = fill_groups_f(rec_no)
                    rec_no += 1
                    self.mBitArray.extend([val] * (max(1, grp_size)))

    def getCondEnv(self):
        return self.mCondEnv

    def getCondType(self):
        return self.mCondType

    def getCondName(self):
        return self.mName

    def getBitArray(self):
        return self.mBitArray

    def __not__(self):
        assert False

    def __and__(self, other):
        assert False

    def __or__(self, other):
        assert False

    def addOr(self, other):
        assert other is not None and other.getCondType() is not None
        if other.getCondType() == "or":
            return other.addOr(self)
        elif other.getCondType() == "null":
            return self
        elif other.getCondType() == "all":
            return other
        return WS_Or([self, other])

    def addAnd(self, other):
        assert other is not None and other.getCondType() is not None
        if other.getCondType() == "and":
            return other.addAnd(self)
        elif other.getCondType() == "all":
            return self
        elif other.getCondType() == "null":
            return other
        return WS_And([self, other])

    def negative(self):
        return WS_Negation(self)

    def getCondNone(self):
        return WS_None(self)

    def getCondAll(self):
        return WS_All(self)

    def iterSelection(self):
        rec_no = -1
        for grp_offset, grp_size in self.getCondEnv().iterGroups():
            rec_no += 1
            group_val = self.mBitArray[grp_offset:
                grp_offset + max(1, grp_size)]
            if group_val.any():
                yield rec_no, group_val

    def getAllCounts(self):
        count_grp, count_items = 0, 0
        for _, rec_it_map in self.iterSelection():
            count_grp += 1
            count_items += rec_it_map.count()
        return (count_grp, count_items, self.mCondEnv.getTotalCount())

    def getItemCount(self):
        return self.mBitArray.count()

    def recInSelection(self, rec_no):
        grp_offset, grp_size = self.getCondEnv().getGroupPos(rec_no)
        return self.mBitArray[grp_offset:grp_offset + max(1, grp_size)].any()

    sPattTrue = bitarray('1')

    def iterItemIdx(self):
        grp_idx = 0
        groups = self.mCondEnv.getGroups()
        idx_max = len(groups) - 1
        for idx_pos in self.mBitArray.itersearch(self.sPattTrue):
            while (grp_idx < idx_max and idx_pos >= groups[grp_idx + 1][0]):
                grp_idx += 1
            yield grp_idx, idx_pos

#===============================================
class WS_Negation(WS_Condition):
    def __init__(self, base_cond):
        WS_Condition.__init__(self, base_cond.getCondEnv(), "neg",
            "neg/" + base_cond.getCondName(),
            ~base_cond.getBitArray())
        self.mBaseCond = base_cond

    def negative(self):
        return self.mBaseCond

#===============================================
class _WS_Joiner(WS_Condition):
    def __init__(self, kind, items, bit_arr):
        WS_Condition.__init__(self, items[0].getCondEnv(), kind, kind,
            bit_arr = bit_arr)
        self.mItems = items
        assert len(self.mItems) > 0

    def getItems(self):
        return self.mItems

#===============================================
class WS_And(_WS_Joiner):
    def __init__(self, items):
        bit_arr = items[0].getBitArray().copy()
        for it in items[1:]:
            bit_arr &= it.getBitArray()
        _WS_Joiner.__init__(self, "and", items,  bit_arr)

    def addAnd(self, other):
        if other.getCondType() == "null":
            return other
        if other.getCondType() == "all":
            return self
        if other.getCondType() == "and":
            add_items = other.getItems()
        else:
            add_items = [other]
        return WS_And(self.getItems() + add_items)

#===============================================
#===============================================
class WS_Or(_WS_Joiner):
    def __init__(self, items):
        bit_arr = items[0].getBitArray().copy()
        for it in items[1:]:
            bit_arr |= it.getBitArray()
        _WS_Joiner.__init__(self, "or", items,  bit_arr)

    def addOr(self, other):
        if other.getCondType() == "null":
            return self
        if other.getCondType() == "all":
            return other
        if other.getCondType() == "or":
            add_items = other.getItems()
        else:
            add_items = [other]
        return WS_Or(self.getItems() + add_items)

#===============================================
class WS_None(WS_Condition):
    def __init__(self, cond_env):
        bit_arr = bitarray(cond_env.getTotalCount())
        bit_arr.setall(False)
        WS_Condition.__init__(self, cond_env, "null", "null", bit_arr)

    def addAnd(self, other):
        return self

    def addOr(self, other):
        return other

    def negative(self):
        return self.getCondEnv().getCondAll()

    def __call__(self, rec_no):
        return False

#===============================================
class WS_All(WS_Condition):
    def __init__(self, cond_env):
        bit_arr = bitarray(cond_env.getTotalCount())
        bit_arr.setall(True)
        WS_Condition.__init__(self, cond_env, "all", "all", bit_arr)

    def addAnd(self, other):
        return other

    def addOr(self, other):
        return self

    def negative(self):
        return self.getCondEnv().getCondNone()

    def __call__(self, rec_no):
        return True

#===============================================
class WS_MetaNumUnit(MetaUnit):
    def __init__(self, name, rec_func = None):
        MetaUnit.__init__(self, name, "num")
        self.mRecFunc = rec_func

    def getRecVal(self, rec_no):
        return self.mRecFunc(rec_no)

    def getUnitKind(self):
        return self.mUnitKind

    def getName(self):
        return self.mName

    def isDetailed(self):
        return False
