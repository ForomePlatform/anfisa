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

#import sys
import abc
from array import array
from bitarray import bitarray

from forome_tools.variants import VariantSet
from app.eval.var_unit import (VarUnit, NumUnitSupport, EnumUnitSupport,
    ReservedNumUnit)
from .val_stat import NumDiapStat, EnumStat
#===============================================
class WS_Unit(VarUnit):
    def __init__(self, eval_space, unit_data,
            unit_kind = None, sub_kind = None):
        VarUnit.__init__(self, eval_space, unit_data, unit_kind, sub_kind)
        self.mExtractor = None

    @abc.abstractmethod
    def getRecVal(self, rec_no):
        return None

    @abc.abstractmethod
    def makeStat(self, condition, eval_h):
        return None

    @abc.abstractmethod
    def fillRecord(self, obj, rec_no):
        assert False

#===============================================
class WS_NumericValueUnit(WS_Unit, NumUnitSupport):
    def __init__(self, eval_space, unit_data):
        WS_Unit.__init__(self, eval_space, unit_data, "numeric")
        assert self.getSubKind() in {"float", "int"}, (
            "Bad sub-kind for "  + self.getName())
        self._setScreened(self.getDescr()["min"] is None)
        self.mArray = array("d" if self.getSubKind() == "float" else "q")

    def getRecVal(self, rec_no):
        return self.mArray[rec_no]

    def makeStat(self, condition, eval_h):
        ret_handle = self.prepareStat()
        num_stat = NumDiapStat()
        for rec_no, _ in condition.iterSelection():
            num_stat.regValue(self.mArray[rec_no])
        num_stat.reportResult(ret_handle)
        return ret_handle

    def fillRecord(self, inp_data, rec_no):
        assert len(self.mArray) == rec_no, (
            "Bad record length for "  + self.getName())
        self.mArray.append(inp_data.get(self.getInternalName()))

#===============================================
class WS_EnumUnit(WS_Unit, EnumUnitSupport):
    def __init__(self, eval_space, unit_data, sub_kind = None):
        WS_Unit.__init__(self, eval_space, unit_data, "enum", sub_kind)
        variants_info = self.getDescr().get("variants")
        if variants_info is None:
            self._setScreened()
            self.mVariantSet = None
        else:
            self.mVariantSet = VariantSet(
                [info[0] for info in variants_info])
            self._setScreened(
                sum(info[1] for info in variants_info) == 0)

    def getVariantSet(self):
        return self.mVariantSet

    def getVariantList(self):
        return list(iter(self.mVariantSet))

    def makeStat(self, condition, eval_h):
        ret_handle = self.prepareStat()
        enum_stat = EnumStat(self.mVariantSet)
        for rec_no, _ in condition.iterSelection():
            enum_stat.regValues(self.getRecVal((rec_no)))
        enum_stat.reportResult(ret_handle)
        return ret_handle

#===============================================
class WS_StatusUnit(WS_EnumUnit):
    def __init__(self, eval_space, unit_data):
        WS_EnumUnit.__init__(self, eval_space, unit_data, "status")
        self.mArray = array('L')

    def getRecVal(self, rec_no):
        return {self.mArray[rec_no]}

    def fillRecord(self, inp_data, rec_no):
        assert len(self.mArray) == rec_no, (
            "Bad record length for "  + self.getName())
        value = inp_data[self.getInternalName()]
        self.mArray.append(self.mVariantSet.indexOf(value))

#===============================================
class WS_MultiSetUnit(WS_EnumUnit):
    def __init__(self, eval_space, unit_data):
        WS_EnumUnit.__init__(self, eval_space, unit_data)
        self.mArraySeq = [bitarray()
            for var in iter(self.mVariantSet)]

    def getRecVal(self, rec_no):
        ret = set()
        for var_no in range(len(self.mArraySeq)):
            if self.mArraySeq[var_no][rec_no]:
                ret.add(var_no)
        return ret

    def _setRecBit(self, rec_no, idx, value):
        self.mArraySeq[idx][rec_no] = value

    def fillRecord(self, inp_data, rec_no):
        values = inp_data.get(self.getInternalName())
        if values:
            idx_set = self.mVariantSet.makeIdxSet(values)
        else:
            idx_set = set()
        for var_no in range(len(self.mArraySeq)):
            self.mArraySeq[var_no].append(var_no in idx_set)

#===============================================
class WS_MultiCompactUnit(WS_EnumUnit):
    def __init__(self, eval_space, unit_data):
        WS_EnumUnit.__init__(self, eval_space, unit_data)
        self.mArray = array('L')
        self.mPackSetDict = dict()
        self.mPackSetSeq  = [set()]

    def getRecVal(self, rec_no):
        return self.mPackSetSeq[self.mArray[rec_no]]

    @staticmethod
    def makePackKey(idx_set):
        return '#'.join(map(str, sorted(idx_set)))

    def fillRecord(self, inp_data, rec_no):
        values = inp_data.get(self.getInternalName())
        if values:
            idx_set = self.mVariantSet.makeIdxSet(values)
            key = self.makePackKey(idx_set)
            idx = self.mPackSetDict.get(key)
            if idx is None:
                idx = len(self.mPackSetSeq)
                self.mPackSetDict[key] = idx
                self.mPackSetSeq.append(set(idx_set))
        else:
            idx = 0
        assert len(self.mArray) == rec_no, (
            "Bad record length for "  + self.getName())
        self.mArray.append(idx)

#===============================================
class WS_TranscriptNumericValueUnit(WS_Unit, NumUnitSupport):
    def __init__(self, eval_space, unit_data):
        WS_Unit.__init__(self, eval_space, unit_data, "numeric")
        assert self.getSubKind() in {"transcript-float", "transcript-int"}, (
            "Bad sub-kind for "  + self.getName())
        self._setScreened(self.getDescr()["min"] is None)
        self.mArray = array("d" if self.getSubKind() == "float" else "q")
        self.mDefaultValue = self.getDescr()["default"]

    def isDetailed(self):
        return True

    def getItemVal(self, item_idx):
        return self.mArray[item_idx]

    def makeStat(self, condition, eval_h):
        ret_handle = self.prepareStat()
        num_stat = NumDiapStat(True)
        for group_no, it_idx in condition.iterItemIdx():
            num_stat.regValue([self.mArray[it_idx]], group_no)
        num_stat.reportResult(ret_handle)
        ret_handle["detailed"] = True
        return ret_handle

    def fillRecord(self, inp_data, rec_no):
        values = inp_data.get(self.getInternalName())
        if values:
            self.mArray.extend(values)
        else:
            self.mArray.append(self.mDefaultValue)

#===============================================
class WS_TranscriptStatusUnit(WS_Unit, EnumUnitSupport):
    def __init__(self, eval_space, unit_data):
        WS_Unit.__init__(self, eval_space, unit_data,
            "enum", "transcript-status")
        variants_info = self.getDescr().get("variants")
        self.mVariantSet = VariantSet(
            [info[0] for info in variants_info])
        self.mDefaultValue = self.mVariantSet.indexOf(
            self.getDescr()["default"])
        assert self.mDefaultValue is not None, (
            "No default falue for "  + self.getName())
        self._setScreened(
            sum(info[1] for info in variants_info) == 0)
        self.mArray = array('L')

    def isDetailed(self):
        return True

    def getVariantSet(self):
        return self.mVariantSet

    def getItemVal(self, item_idx):
        return {self.mArray[item_idx]}

    def fillRecord(self, inp_data, rec_no):
        values = inp_data.get(self.getInternalName())
        if not values:
            self.mArray.append(self.mDefaultValue)
        else:
            self.mArray.extend([self.mVariantSet.indexOf(value)
                for value in values])

    def makeStat(self, condition, eval_h):
        ret_handle = self.prepareStat()
        enum_stat = EnumStat(self.mVariantSet, detailed = True)
        for group_no, it_idx in condition.iterItemIdx():
            enum_stat.regValues([self.mArray[it_idx]], group_no = group_no)
        enum_stat.reportResult(ret_handle)
        ret_handle["detailed"] = True
        return ret_handle

#===============================================
class WS_TranscriptMultisetUnit(WS_Unit, EnumUnitSupport):
    def __init__(self, eval_space, unit_data):
        WS_Unit.__init__(self, eval_space, unit_data,
            "enum", unit_data["sub-kind"])
        variants_info = self.getDescr().get("variants")
        self.mVariantSet = VariantSet(
            [info[0] for info in variants_info])
        self._setScreened(
            sum(info[1] for info in variants_info) == 0)
        self.mArray = array('L')
        self.mPackSetDict = dict()
        self.mPackSetSeq  = [set()]

    def isDetailed(self):
        return True

    def getVariantSet(self):
        return self.mVariantSet

    def getItemVal(self, item_idx):
        return self.mPackSetSeq[self.mArray[item_idx]]

    def _fillOne(self, values):
        if values:
            idx_set = self.mVariantSet.makeIdxSet(values)
            key = WS_MultiCompactUnit.makePackKey(idx_set)
            idx = self.mPackSetDict.get(key)
            if idx is None:
                idx = len(self.mPackSetSeq)
                self.mPackSetDict[key] = idx
                self.mPackSetSeq.append(set(idx_set))
        else:
            idx = 0
        self.mArray.append(idx)

    def fillRecord(self, inp_data, rec_no):
        seq = inp_data.get(self.getInternalName())
        if not seq:
            self.mArray.append(0)
        else:
            for values in seq:
                self._fillOne(values)

    def makeStat(self, condition, eval_h):
        ret_handle = self.prepareStat()
        enum_stat = EnumStat(self.mVariantSet, detailed = True)
        for group_no, it_idx in condition.iterItemIdx():
            enum_stat.regValues(self.mPackSetSeq[self.mArray[it_idx]],
                group_no = group_no)
        enum_stat.reportResult(ret_handle)
        ret_handle["detailed"] = True
        return ret_handle

#===============================================
def loadWS_Unit(eval_space, unit_data):
    kind = unit_data["kind"]
    if kind == "numeric":
        if unit_data["sub-kind"].startswith("transcript-"):
            return WS_TranscriptNumericValueUnit(eval_space, unit_data)
        return WS_NumericValueUnit(eval_space, unit_data)
    assert kind == "enum", "Bad kind: " + kind + " for " + unit_data["name"]
    if unit_data["sub-kind"] == "transcript-status":
        return WS_TranscriptStatusUnit(eval_space, unit_data)
    if unit_data["sub-kind"] == "transcript-multiset":
        return WS_TranscriptMultisetUnit(eval_space, unit_data)
    if unit_data["sub-kind"] == "transcript-panels":
        return WS_TranscriptMultisetUnit(eval_space, unit_data)
    if unit_data["sub-kind"] == "status":
        return WS_StatusUnit(eval_space, unit_data)
    if kind == "enum" and unit_data.get("compact"):
        return WS_MultiCompactUnit(eval_space, unit_data)
    return WS_MultiSetUnit(eval_space, unit_data)

#===============================================
class WS_ReservedNumUnit(ReservedNumUnit):
    def __init__(self, eval_space, name, rec_func, sub_kind = "int"):
        ReservedNumUnit.__init__(self, eval_space, name, sub_kind)
        self.mRecFunc = rec_func

    def getRecVal(self, rec_no):
        return self.mRecFunc(rec_no)

    def isDetailed(self):
        return False
