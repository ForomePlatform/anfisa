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

from utils.variants import VariantSet
from app.filter.unit import Unit
from app.model.zygosity import ZygosityComplex
from .val_stat import NumDiapStat, EnumStat
#===============================================
class WS_Unit(Unit):
    def __init__(self, ds_h, unit_data, unit_kind = None):
        Unit.__init__(self, unit_data, unit_kind)
        self.mExtractor = None
        self.mDS = ds_h

    def getDS(self):
        return self.mDS

    def getCondEnv(self):
        return self.mDS.getCondEnv()

    def isAtomic(self):
        return True

    def isDetailed(self):
        return False

    def dumpNames(self):
        ret = {"name": self.mName,
            "vgroup": self.mVGroupTitle}
        if self.mTitle and self.mTitle != self.mName:
            ret["title"] = self.mTitle
        if self.mRenderMode:
            ret["render"] = self.mRenderMode
        return ret

    @abc.abstractmethod
    def getRecVal(self, rec_no):
        return None

    @abc.abstractmethod
    def makeStat(self, condition, repr_context = None):
        return None

    @abc.abstractmethod
    def fillRecord(self, obj, rec_no):
        assert False

#===============================================
class NumericValueUnit(WS_Unit):
    def __init__(self, ds_h, unit_data):
        WS_Unit.__init__(self, ds_h, unit_data,
            "float" if unit_data["kind"] == "float" else "int")
        self._setScreened(self.getDescr()["min"] is None)
        self.mArray = array("d" if unit_data["kind"] == "float" else "q")
        self.getCondEnv().addNumUnit(self)

    def getRecVal(self, rec_no):
        return self.mArray[rec_no]

    def makeStat(self, condition, repr_context = None):
        stat = NumDiapStat()
        for rec_no, _ in condition.iterSelection():
            stat.regValue(self.mArray[rec_no])
        ret = self.prepareStat() + stat.result()
        return ret

    def fillRecord(self, inp_data, rec_no):
        assert len(self.mArray) == rec_no
        self.mArray.append(inp_data.get(self.getName()))

#===============================================
class _EnumUnit(WS_Unit):
    def __init__(self, ds_h, unit_data, unit_kind):
        WS_Unit.__init__(self, ds_h, unit_data, unit_kind)
        variants_info = self.getDescr().get("variants")
        if variants_info is None:
            self._setScreened()
            self.mVariantSet = None
        else:
            self.mVariantSet = VariantSet(
                [info[0] for info in variants_info])
            self._setScreened(
                sum(info[1] for info in variants_info) == 0)
        self.getCondEnv().addEnumUnit(self)

    def getVariantSet(self):
        return self.mVariantSet

    def getVariantList(self):
        return list(iter(self.mVariantSet))

    def makeStat(self, condition, repr_context = None):
        stat = EnumStat(self.mVariantSet)
        for rec_no, _ in condition.iterSelection():
            stat.regValues(self.getRecVal((rec_no)))
        return self.prepareStat() + stat.result()

#===============================================
class StatusUnit(_EnumUnit):
    def __init__(self, ds_h, unit_data):
        _EnumUnit.__init__(self, ds_h, unit_data, "status")
        self.mArray = array('L')

    def getRecVal(self, rec_no):
        return {self.mArray[rec_no]}

    def fillRecord(self, inp_data, rec_no):
        assert len(self.mArray) == rec_no
        value = inp_data[self.getName()]
        self.mArray.append(self.mVariantSet.indexOf(value))

#===============================================
class MultiSetUnit(_EnumUnit):
    def __init__(self, ds_h, unit_data):
        _EnumUnit.__init__(self, ds_h, unit_data, "enum")
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

    def isAtomic(self):
        return False

    def fillRecord(self, inp_data, rec_no):
        values = inp_data.get(self.getName())
        if values:
            idx_set = self.mVariantSet.makeIdxSet(values)
        else:
            idx_set = set()
        for var_no in range(len(self.mArraySeq)):
            self.mArraySeq[var_no].append(var_no in idx_set)

#===============================================
class MultiCompactUnit(_EnumUnit):
    def __init__(self, ds_h, unit_data):
        _EnumUnit.__init__(self, ds_h, unit_data, "enum")
        self.mArray = array('L')
        self.mPackSetDict = dict()
        self.mPackSetSeq  = [set()]

    def getRecVal(self, rec_no):
        return self.mPackSetSeq[self.mArray[rec_no]]

    def isAtomic(self):
        return False

    @staticmethod
    def makePackKey(idx_set):
        return '#'.join(map(str, sorted(idx_set)))

    def fillRecord(self, inp_data, rec_no):
        values = inp_data.get(self.getName())
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
        assert len(self.mArray) == rec_no
        self.mArray.append(idx)

#===============================================
class ZygosityComplexUnit(WS_Unit, ZygosityComplex):
    def __init__(self, ds_h, unit_data):
        WS_Unit.__init__(self, ds_h, unit_data, "zygosity")
        ZygosityComplex.__init__(self,
            ds_h.getFamilyInfo(), unit_data)
        self.mArrayFam = []
        fam_units = []
        for idx, fam_name in enumerate(self.iterFamNames()):
            self.mArrayFam.append(array('b'))
            fam_units.append(
                self.getCondEnv().addMetaNumUnit(
                    fam_name, self.getFamRecFunc(idx)))
        self.setupSubUnits(fam_units)
        self.getCondEnv().addSpecialUnit(self)

    def getFamRecFunc(self, idx):
        return lambda rec_no: self.mArrayFam[idx][rec_no]

    def setup(self):
        self.setupXCond()

    def getRecVal(self, idx):
        assert False
        return None

    def isAtomic(self):
        return False

    def isOK(self):
        return self.mIsOK

    def fillRecord(self, inp_data, rec_no):
        for idx, fam_name in enumerate(self.iterFamNames()):
            self.mArrayFam[idx].append(inp_data.get(fam_name))

    def makeStat(self, condition, repr_context = None):
        return ZygosityComplex.makeStat(self, self.getDS(),
            condition, repr_context)

#===============================================
class TranscriptStatusUnit(WS_Unit):
    def __init__(self, ds_h, unit_data):
        WS_Unit.__init__(self, ds_h, unit_data, "transcript-status")
        variants_info = self.getDescr().get("variants")
        self.mVariantSet = VariantSet(
            [info[0] for info in variants_info])
        self.mDefaultValue = self.mVariantSet.indexOf(
            self.getDescr()["default"])
        self._setScreened(
            sum(info[1] for info in variants_info) == 0)
        self.mArray = array('L')
        self.getCondEnv().addEnumUnit(self)

    def isDetailed(self):
        return True

    def getVariantSet(self):
        return self.mVariantSet

    def getItemVal(self, item_idx):
        return {self.mArray[item_idx]}

    def fillRecord(self, inp_data, rec_no):
        values = inp_data.get(self.getName())
        if not values:
            self.mArray.append(self.mDefaultValue)
        else:
            self.mArray.extend([self.mVariantSet.indexOf(value)
                for value in values])

    def makeStat(self, condition, repr_context = None):
        stat = EnumStat(self.mVariantSet, detailed = True)
        for group_no, it_idx in condition.iterItemIdx():
            stat.regValues([self.mArray[it_idx]], group_no = group_no)
        ret = self.prepareStat()
        ret[1]["detailed"] = True
        return ret + stat.result()

#===============================================
class TranscriptMultisetUnit(WS_Unit):
    def __init__(self, ds_h, unit_data):
        WS_Unit.__init__(self, ds_h, unit_data, "transcript-multiset")
        variants_info = self.getDescr().get("variants")
        self.mVariantSet = VariantSet(
            [info[0] for info in variants_info])
        self._setScreened(
            sum(info[1] for info in variants_info) == 0)
        self.mArray = array('L')
        self.getCondEnv().addEnumUnit(self)
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
            key = MultiCompactUnit.makePackKey(idx_set)
            idx = self.mPackSetDict.get(key)
            if idx is None:
                idx = len(self.mPackSetSeq)
                self.mPackSetDict[key] = idx
                self.mPackSetSeq.append(set(idx_set))
        else:
            idx = 0
        self.mArray.append(idx)

    def fillRecord(self, inp_data, rec_no):
        seq = inp_data.get(self.getName())
        if not seq:
            self.mArray.append(0)
        else:
            for values in seq:
                self._fillOne(values)

    def makeStat(self, condition, repr_context = None):
        stat = EnumStat(self.mVariantSet, detailed = True)
        for group_no, it_idx in condition.iterItemIdx():
            stat.regValues(self.mPackSetSeq[self.mArray[it_idx]],
                group_no = group_no)
        ret = self.prepareStat()
        ret[1]["detailed"] = True
        return ret + stat.result()

#===============================================
def loadWS_Unit(ds_h, unit_data):
    kind = unit_data["kind"]
    if kind == "zygosity":
        ret = ZygosityComplexUnit(ds_h, unit_data)
        return ret if ret.isOK() else None
    if kind == "transcript-status":
        return TranscriptStatusUnit(ds_h, unit_data)
    if kind == "transcript-multiset":
        return TranscriptMultisetUnit(ds_h, unit_data)
    if kind in ("long", "float"):
        return NumericValueUnit(ds_h, unit_data)
    assert kind in ("enum", "presence")
    if kind == "enum" and unit_data["atomic"]:
        return StatusUnit(ds_h, unit_data)
    if kind == "enum" and unit_data["compact"]:
        return MultiCompactUnit(ds_h, unit_data)
    return MultiSetUnit(ds_h, unit_data)
