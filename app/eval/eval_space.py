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
import abc, json
from hashlib import md5

from .condition import ConditionMaker
from .variety import VarietyUnit
#===============================================
class EvalSpace:
    def __init__(self, ds_h):
        self.mDS = ds_h
        self.mUnits = []
        self.mUnitDict = dict()
        self.mFunctions = []

    def getDS(self):
        return self.mDS

    def getName(self):
        return self.mDS.getName()

    def heavyMode(self):
        return False

    @abc.abstractmethod
    def getZygUnit(self, idx):
        assert False

    @abc.abstractmethod
    def iterZygUnits(self):
        assert False

    def iterFunctions(self):
        return iter(self.mFunctions)

    def _addUnit(self, unit_h, force_it = False):
        if unit_h.getMean() == "pre-variety":
            self._addReservedUnit(unit_h)
            variety_h = VarietyUnit(unit_h)
            self._addUnit(variety_h)
            return

        self.mUnits.append(unit_h)
        assert force_it or unit_h.getName() not in self.mUnitDict, (
            "Duplicate unit name: " + unit_h.getName())
        self.mUnitDict[unit_h.getName()] = unit_h

        if unit_h.getMean() == "variety":
            self._addUnit(unit_h.getPanelUnit())

    def _insertUnit(self, unit_h,
            before = None, after = None, insert_idx = None):
        assert unit_h.getName() not in self.mUnitDict, (
            "Duplicate unit name: " + unit_h.getName())
        if insert_idx is None:
            last_vgroup_idx = None, None
            for idx, u_h in enumerate(self.mUnits):
                if before is not None and u_h.getName() == before:
                    insert_idx = idx
                    break
                if after is not None and u_h.getName() == after:
                    insert_idx = idx + 1
                    break
                if u_h.getVGroup() == unit_h.getVGroup():
                    last_vgroup_idx = idx
        if insert_idx is None:
            if last_vgroup_idx is not None:
                insert_idx = last_vgroup_idx + 1
            else:
                insert_idx = len(self.mUnits)
        self.mUnits.insert(insert_idx, unit_h)
        self.mUnitDict[unit_h.getName()] = unit_h

    def _addReservedUnit(self, meta_unit_h):
        assert meta_unit_h.getName() not in self.mUnitDict, (
            "Duplicate meta unit name: " + meta_unit_h.getName())
        self.mUnitDict[meta_unit_h.getName()] = meta_unit_h

    def _addFunction(self, unit_h):
        assert unit_h.getName() not in self.mUnitDict, (
            "Duplicate function unit name: " + unit_h.getName())
        self.mUnitDict[unit_h.getName()] = unit_h
        self.mFunctions.append(unit_h)

    def getUnit(self, unit_name):
        return self.mUnitDict.get(unit_name)

    def iterUnits(self):
        return iter(self.mUnits)

    def joinAnd(self, seq):
        ret = self.getCondAll()
        for cond in seq:
            ret = ret.addAnd(cond)
        return ret

    def joinOr(self, seq):
        ret = self.getCondNone()
        for cond in seq:
            ret = ret.addOr(cond)
        return ret

    def getUsedDimValues(self, eval_h, dim_name):
        ret = set()
        for unit_h in self.mUnits:
            if unit_h.getDimName() == dim_name:
                ret |= eval_h.getUsedEnumValues(unit_h.getName())
        return ret

#===============================================
class Eval_Condition:
    def __init__(self, eval_space, cond_type, name = None):
        self.mEvalSpace = eval_space
        self.mCondType = cond_type
        self.mName = name
        self.mPreForm = None

    def setPreForm(self, pre_data):
        self.mPreForm = pre_data

    def getEvalSpace(self):
        return self.mEvalSpace

    def getCondType(self):
        return self.mCondType

    def getPreForm(self):
        return self.mPreForm

    def __not__(self):
        assert False

    def __and__(self, other):
        assert False

    def __or__(self, other):
        assert False

    def isPositive(self):
        return True

    @abc.abstractmethod
    def _makeOr(self, other):
        return None

    @abc.abstractmethod
    def _makeAnd(self, other):
        return None

    def addOr(self, other):
        assert other is not None and other.getCondType() is not None
        if self.mCondType == "all":
            return self
        elif self.mCondType == "null":
            return other
        if other.getCondType() == "null":
            return self
        elif other.getCondType() == "all":
            return other
        elif other.getCondType() == "or" and self.mCondType != "or":
            return other.addOr(self)
        return self._makeOr(other)

    def addAnd(self, other):
        assert other is not None and other.getCondType() is not None
        if self.mCondType == "all":
            return other
        elif self.mCondType == "null":
            return self
        if other.getCondType() == "all":
            return self
        elif other.getCondType() == "null":
            return other
        elif other.getCondType() == "and" and self.mCondType != "and":
            return other.addAnd(self)
        return self._makeAnd(other)

    @abc.abstractmethod
    def toJSon(self):
        return None

    @abc.abstractmethod
    def negative(self):
        return None

    @abc.abstractmethod
    def getCondNone(self):
        return None

    @abc.abstractmethod
    def getCondAll(self):
        return None

    def hashCode(self):
        json_repr = self.toJSon()
        hash_h = md5(bytes(json.dumps(json_repr, sort_keys = True),
            encoding="utf-8"))
        return hash_h.hexdigest()

    def visit(self, visitor):
        visitor.lookAt(self)

#===============================================
class CondSupport_None:

    def toJSon(self):
        return ConditionMaker.condNone()

    def addAnd(self, other):
        return self

    def addOr(self, other):
        return other

    def negative(self):
        return self.getEvalSpace().getCondAll()

#===============================================
class CondSupport_All:

    def toJSon(self):
        return ConditionMaker.condAll()

    def addAnd(self, other):
        return other

    def addOr(self, other):
        return self

    def negative(self):
        return self.getEvalSpace().getCondNone()
