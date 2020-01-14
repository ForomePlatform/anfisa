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

from app.eval.eval_space import (EvalSpace, Eval_Condition,
    CondSupport_None, CondSupport_All)
from app.eval.condition import ConditionMaker, ZYG_BOUNDS_VAL
from .ws_unit import WS_ReservedNumUnit

#===============================================
class WS_EvalSpace(EvalSpace):
    def __init__(self, ds_h, rec_rand_f):
        EvalSpace.__init__(self, ds_h)
        self.mTotal = 0
        self.mGroups = []
        self.mZygRUnits = []

        self.mRandRUnit = WS_ReservedNumUnit(
            self, "_rand", rec_rand_f)
        self._addReservedUnit(self.mRandRUnit)

    def _addZygUnit(self, zyg_name, zyg_func):
        r_unit_h = WS_ReservedNumUnit(self, zyg_name, zyg_func)
        self.mZygRUnits.append(r_unit_h)
        self._addReservedUnit(r_unit_h)

    def getCondKind(self):
        return "ws"

    def getZygUnit(self, idx):
        return self.mZygRUnits[idx]

    def iterZygUnits(self):
        return iter(self.mZygRUnits)

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

    def makeNumericCond(self, unit_h, min_val = None, min_eq = True,
            max_val = None, max_eq = True,  zyg_bounds = None):
        if min_val is not None or max_val is not None:
            assert zyg_bounds is None
        else:
            min_val, min_eq, max_val, max_eq = ZYG_BOUNDS_VAL[zyg_bounds]
        return WS_CondNumeric.create(unit_h, min_val, min_eq, max_val, max_eq)

    def makeEnumCond(self, unit_h, variants, filter_mode = ""):
        return WS_CondEnum.create(unit_h, variants, filter_mode)

    @staticmethod
    def numericFilterFunc(min_val, min_eq, max_val, max_eq):
        if min_val is not None:
            if min_eq:
                def min_func(val):
                    return min_val <= val
            else:
                def min_func(val):
                    return min_val < val
        else:
            min_func = None
        if max_val is None:
            return min_func
        if max_eq:
            def max_func(val):
                return val <= max_val
        else:
            def max_func(val):
                return val < max_val
        if min_func is None:
            return max_func
        return lambda val: min_func(val) and max_func(val)

    @staticmethod
    def enumFilterFunc(filter_mode, base_idx_set):
        if filter_mode == "NOT":
            return lambda idx_set: len(idx_set & base_idx_set) == 0
        if filter_mode == "AND":
            all_len = len(base_idx_set)
            return lambda idx_set: len(idx_set & base_idx_set) == all_len
        return lambda idx_set: len(idx_set & base_idx_set) > 0

    def reportCounts(self, condition):
        count, count_items, total_items = condition.getAllCounts()
        return {
            "count": count,
            "transcripts": [count_items, total_items]}

    def evalRecSeq(self, condition, expect_count = None):
        return [rec_no
            for rec_no, rec_it_map in condition.iterSelection()]

    def evalTotalCount(self, condition):
        if condition is None:
            return self.getDS().getTotal()
        return condition.getAllCounts()[0]

    def evalDetailedTotalCount(self, condition):
        if condition is None:
            return self.mTotal
        return condition.getItemCount()

#===============================================
class WS_Condition(Eval_Condition):
    def __init__(self, eval_space, cond_type, bit_arr = None,
            fill_groups_f = None, fill_items_f = None, detailed = None):
        Eval_Condition.__init__(self, eval_space, cond_type)
        self.mBitArray = bit_arr
        self.mDetailed = detailed
        if self.mBitArray is not None:
            assert fill_groups_f is None and fill_items_f is None
            assert detailed is not None
        else:
            self.mBitArray = bitarray()
            if fill_items_f is not None:
                assert fill_groups_f is None and detailed is not False
                for grp_offset, grp_size in self.getEvalSpace().iterGroups():
                    if grp_size == 0:
                        self.mBitArray.append(False)
                    else:
                        self.mBitArray.extend([fill_items_f(grp_offset + j)
                            for j in range(grp_size)])
                self.mDetailed = True
            else:
                rec_no = 0
                for _, grp_size in self.getEvalSpace().iterGroups():
                    val = fill_groups_f(rec_no)
                    rec_no += 1
                    self.mBitArray.extend([val] * (max(1, grp_size)))
                if not self.mDetailed:
                    self.mDetailed = False

    def getBitArray(self):
        return self.mBitArray

    def isDetailed(self):
        return self.mDetailed

    def _makeOr(self, other):
        return WS_Or([self, other])

    def _makeAnd(self, other):
        return WS_And([self, other])

    def negative(self):
        return WS_Negation(self)

    def getCondNone(self):
        return WS_None(self)

    def getCondAll(self):
        return WS_All(self)

    def iterSelection(self):
        rec_no = -1
        for grp_offset, grp_size in self.getEvalSpace().iterGroups():
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
        return (count_grp, count_items, self.getEvalSpace().getTotalCount())

    def getItemCount(self):
        return self.mBitArray.count()

    def recInSelection(self, rec_no):
        grp_offset, grp_size = self.getEvalSpace().getGroupPos(rec_no)
        return self.mBitArray[grp_offset:grp_offset + max(1, grp_size)].any()

    sPattTrue = bitarray('1')

    def iterItemIdx(self):
        grp_idx = 0
        groups = self.getEvalSpace().getGroups()
        idx_max = len(groups) - 1
        for idx_pos in self.mBitArray.itersearch(self.sPattTrue):
            while (grp_idx < idx_max and idx_pos >= groups[grp_idx + 1][0]):
                grp_idx += 1
            yield grp_idx, idx_pos

#===============================================
class WS_CondNumeric(WS_Condition):
    @classmethod
    def create(cls, unit_h, min_val, min_eq, max_val, max_eq):
        eval_func = WS_EvalSpace.numericFilterFunc(
            min_val, min_eq, max_val, max_eq)
        if unit_h.isDetailed():
            def fill_items_f(it_idx):
                return eval_func(unit_h.getItemVal(it_idx))
            fill_groups_f = None
        else:
            def fill_groups_f(rec_no):
                return eval_func(unit_h.getRecVal(rec_no))
            fill_items_f = None
        return cls(unit_h.getEvalSpace(), fill_groups_f, fill_items_f,
            (unit_h.getName(), min_val, min_eq, max_val, max_eq))

    def __init__(self, eval_space, fill_groups_f, fill_items_f, data):
        WS_Condition.__init__(self, eval_space, "numeric",
            fill_groups_f = fill_groups_f, fill_items_f = fill_items_f)
        self.mData = data

    def toJSon(self):
        return ConditionMaker.condNum(*self.mData)

#===============================================
class WS_CondEnum(WS_Condition):
    @classmethod
    def create(cls, unit_h, variants, filter_mode):
        eval_func = WS_EvalSpace.enumFilterFunc(filter_mode,
            unit_h.getVariantSet().makeIdxSet(variants))
        if unit_h.isDetailed():
            def fill_items_f(it_idx):
                return eval_func(unit_h.getItemVal(it_idx))
            fill_groups_f = None
        else:
            def fill_groups_f(rec_no):
                return eval_func(unit_h.getRecVal(rec_no))
            fill_items_f = None
        return cls(unit_h.getEvalSpace(), fill_groups_f, fill_items_f,
            (unit_h.getName(), variants, filter_mode))

    def __init__(self, eval_space, fill_groups_f, fill_items_f, data):
        WS_Condition.__init__(self, eval_space, "numeric",
            fill_groups_f = fill_groups_f, fill_items_f = fill_items_f)
        self.mData = data

    def toJSon(self):
        return ConditionMaker.condEnum(*self.mData)

#===============================================
class WS_Negation(WS_Condition):
    def __init__(self, base_cond):
        WS_Condition.__init__(self, base_cond.getEvalSpace(), "neg",
            ~base_cond.getBitArray(), detailed = base_cond.isDetailed())
        self.mBaseCond = base_cond

    def toJSon(self):
        return ConditionMaker.condNot(self.mBaseCond.toJSon())

    def negative(self):
        return self.mBaseCond

#===============================================
class _WS_Joiner(WS_Condition):
    def __init__(self, kind, items, bit_arr, detailed):
        WS_Condition.__init__(self, items[0].getEvalSpace(), kind,
            bit_arr = bit_arr, detailed = detailed)
        self.mItems = items
        assert len(self.mItems) > 0

    def getItems(self):
        return self.mItems

#===============================================
class WS_And(_WS_Joiner):
    def __init__(self, items):
        bit_arr = items[0].getBitArray().copy()
        detailed = items[0].isDetailed()
        for it in items[1:]:
            bit_arr &= it.getBitArray()
            detailed |= it.isDetailed()
        _WS_Joiner.__init__(self, "and", items,  bit_arr, detailed)

    def toJSon(self):
        return ConditionMaker.joinAnd(
            [it.toJSon() for it in self.getItems()])

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
        detailed = items[0].isDetailed()
        for it in items[1:]:
            bit_arr |= it.getBitArray()
            detailed |= it.isDetailed()
        _WS_Joiner.__init__(self, "or", items,  bit_arr, detailed)

    def toJSon(self):
        return ConditionMaker.joinOr(
            [it.toJSon() for it in self.getItems()])

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
class WS_None(WS_Condition, CondSupport_None):
    def __init__(self, eval_space):
        bit_arr = bitarray(eval_space.getTotalCount())
        bit_arr.setall(False)
        WS_Condition.__init__(self, eval_space, "null",
            bit_arr, detailed = False)

    def __call__(self, rec_no):
        return False

#===============================================
class WS_All(WS_Condition, CondSupport_All):
    def __init__(self, eval_space):
        bit_arr = bitarray(eval_space.getTotalCount())
        bit_arr.setall(True)
        WS_Condition.__init__(self, eval_space, "all",
            bit_arr, detailed = False)

    def __call__(self, rec_no):
        return True
