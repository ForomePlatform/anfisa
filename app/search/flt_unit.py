#import sys
import abc
from array import array
from bitarray import bitarray

from app.config.a_config import AnfisaConfig
from utils.variants import VariantSet
from app.filter.condition import ConditionMaker
from app.filter.unit import Unit
from .val_stat import NumDiapStat, EnumStat
from .flt_cond import WS_SpecCondition, WS_EnumCondition

#===============================================
class FilterUnit(Unit):
    def __init__(self, index, unit_data, unit_kind = None):
        Unit.__init__(self, unit_data, unit_kind)
        self.mIndex = index
        self.mExtractor = None

    def getIndex(self):
        return self.mIndex

    def isAtomic(self):
        return True

    def dumpNames(self):
        ret = {"name": self.mName,
            "vgroup": self.mVGroupTitle}
        if self.mTitle and self.mTitle != self.mName:
            ret["title"] = self.mTitle
        if self.mRenderMode:
            ret["render"] = self.mRenderMode
        return ret

    def getRecFunc(self):
        return self.getRecVal

    @abc.abstractmethod
    def getRecVal(self, rec_no):
        return None

    @abc.abstractmethod
    def makeStat(self, rec_no_seq, repr_context = None):
        return None

    @abc.abstractmethod
    def fillRecord(self, obj, rec_no):
        assert False

    def evalStat(self, condition):
        return self.mIndex.evalStat(self, condition)

#===============================================
class NumericValueUnit(FilterUnit):
    def __init__(self, index, unit_data):
        FilterUnit.__init__(self, index, unit_data,
            "float" if unit_data["kind"] == "float" else "int")
        self._setScreened(self.getDescr()["min"] is None)
        self.mArray = array("d" if unit_data["kind"] == "float" else "q")
        self.getIndex().getCondEnv().addNumUnit(self)

    def getRecVal(self, rec_no):
        return self.mArray[rec_no]

    def makeStat(self, rec_no_seq, repr_context = None):
        stat = NumDiapStat()
        for rec_no in rec_no_seq:
            stat.regValue(self.mArray[rec_no])
        ret = self.prepareStat() + stat.result()
        return ret

    def fillRecord(self, inp_data, rec_no):
        assert len(self.mArray) == rec_no
        self.mArray.append(inp_data.get(self.getName()))

#===============================================
class _EnumUnit(FilterUnit):
    def __init__(self, index, unit_data, unit_kind):
        FilterUnit.__init__(self, index, unit_data, unit_kind)
        variants_info = self.getDescr().get("variants")
        if variants_info is None:
            self._setScreened()
            self.mVariantSet = None
        else:
            self.mVariantSet = VariantSet(
                [info[0] for info in variants_info])
            self._setScreened(
                sum([info[1] for info in variants_info]) == 0)
        self.getIndex().getCondEnv().addEnumUnit(self)

    def getVariantSet(self):
        return self.mVariantSet

    def makeStat(self, rec_no_seq, repr_context = None):
        stat = EnumStat(self.mVariantSet)
        rec_func = self.getRecFunc()
        for rec_no in rec_no_seq:
            stat.regValues(rec_func((rec_no)))
        return self.prepareStat() + stat.result()

#===============================================
class StatusUnit(_EnumUnit):
    def __init__(self, index, unit_data):
        _EnumUnit.__init__(self, index, unit_data, "status")
        self.mArray = array('L')

    def getRecVal(self, rec_no):
        return {self.mArray[rec_no]}

    def fillRecord(self, inp_data, rec_no):
        assert len(self.mArray) == rec_no
        value = inp_data[self.getName()]
        self.mArray.append(self.mVariantSet.indexOf(value))

#===============================================
class MultiSetUnit(_EnumUnit):
    def __init__(self, index, unit_data):
        _EnumUnit.__init__(self, index, unit_data, "enum")
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
    def __init__(self, index, unit_data):
        _EnumUnit.__init__(self, index, unit_data, "enum")
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
        if values :
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
class ZygosityComplexUnit(FilterUnit):
    def __init__(self, index, unit_data):
        FilterUnit.__init__(self, index, unit_data, "zygosity")

        self._setScreened(self.getIndex().getWS().getApp().
            hasRunOption("no-custom"))
        self.mFamilyInfo = self.getIndex().getWS().getFamilyInfo()
        assert ("size" not in unit_data or
            unit_data["size"] == len(self.mFamilyInfo))
        self.mIsOK = (self.mFamilyInfo is not None and
            len(self.mFamilyInfo) > 1)
        if not self.mIsOK:
            return
        self.mArrayFam = []
        self.mNameFam = []
        for idx, member_name in enumerate(self.mFamilyInfo.getMembers()):
            self.mArrayFam.append(array('b'))
            self.mNameFam.append("%s_%d" % (self.getName(), idx))
            self.getIndex().getCondEnv().addReservedName(
                self.mNameFam[-1], self.getFamRecFunc(idx))
        self.mConfig = unit_data.get("config", dict())
        self.mXCondition = None
        labels = AnfisaConfig.configOption("zygosity.cases")
        self.mVariantSet = VariantSet([labels[key]
            for key in ("homo_recess", "x_linked", "dominant", "compens")])
        self.getIndex().getCondEnv().addSpecialUnit(self)

    def getFamRecFunc(self, idx):
        return lambda rec_no: self.mArrayFam[idx][rec_no]

    def setup(self):
        self.mXCondition = self.getIndex().getCondEnv().parse(
            self.mConfig.get("x_cond",
            ConditionMaker.condEnum("Chromosome", ["chrX"])))

    def getRecFunc(self):
        assert False
        return None

    def getRecVal(self, idx):
        assert False
        return None

    def isAtomic(self):
        return False

    def isOK(self):
        return self.mIsOK

    def fillRecord(self, inp_data, rec_no):
        for col_name, arr in zip(self.mNameFam, self.mArrayFam):
            arr.append(inp_data.get(col_name))

    def _makeCrit(self, idx, min_v, max_v = None):
        arr = self.mArrayFam[idx]
        assert min_v is not None
        if max_v is None:
            return lambda rec_no: min_v <= arr[rec_no]
        return lambda rec_no: min_v <= arr[rec_no] <= max_v

    @staticmethod
    def _joinAnd(seq):
        return lambda record: all([f(record) for f in seq])

    def condZHomoRecess(self, problem_group):
        seq = []
        for idx in range(len(self.mFamilyInfo)):
            if idx in problem_group:
                seq.append(self._makeCrit(idx, 2, None))
            else:
                seq.append(self._makeCrit(idx, 0, 1))
        return WS_SpecCondition("ZHomoRecess", self._joinAnd(seq))

    def _condZDominant(self, problem_group):
        seq = []
        for idx in range(len(self.mFamilyInfo)):
            if idx in problem_group:
                seq.append(self._makeCrit(idx, 1, None))
            else:
                seq.append(self._makeCrit(idx, 0, 0))
        return WS_SpecCondition("ZDominant", self._joinAnd(seq))

    def condZDominant(self, problem_group):
        return self.mXCondition.negative().addAnd(
            self._condZDominant(problem_group))

    def condZXLinked(self, problem_group):
        return self.mXCondition.addAnd(
            self._condZDominant(problem_group))

    def conditionZCompens(self, problem_group):
        seq = []
        for idx in range(len(self.mFamilyInfo)):
            if idx in problem_group:
                seq.append(self._makeCrit(idx, 0, 0))
            else:
                seq.append(self._makeCrit(idx, 1, None))
        return WS_SpecCondition("ZCompens", self._joinAnd(seq))

    def _buildCritSeq(self, p_group):
        return [
            self.condZHomoRecess(p_group),
            self.condZXLinked(p_group),
            self.condZDominant(p_group),
            self.conditionZCompens(p_group)]

    def makeStat(self, rec_no_seq, repr_context = None):
        ret = self.prepareStat()
        ret[1]["family"] = self.mFamilyInfo.getTitles()
        ret[1]["affected"] = self.mFamilyInfo.getAffectedGroup()

        if repr_context is None or "problem_group" not in repr_context:
            p_group = self.mFamilyInfo.getAffectedGroup()
        else:
            p_group = {m_idx if 0 <= m_idx < len(self.mFamilyInfo)
                else None for m_idx in repr_context["problem_group"]}
            if None in p_group:
                p_group.remove(None)
        ret.append(list(p_group))
        if len(p_group) == 0:
            return ret + [None]

        stat = EnumStat(self.mVariantSet)
        crit_seq = self._buildCritSeq(p_group)
        for rec_no in rec_no_seq:
            idx_set = set()
            for idx, crit in enumerate(crit_seq):
                if crit(rec_no):
                    idx_set.add(idx)
            stat.regValues(idx_set)
        return ret + stat.result()

    @staticmethod
    def _getIdxSet(crit_seq, record):
        ret = set()
        for idx, crit in enumerate(crit_seq):
            if crit(record):
                ret.add(idx)
        return ret

    def parseCondition(self, cond_info):
        assert cond_info[0] == "zygosity"
        unit_name, p_group, filter_mode, variants = cond_info[1:]

        if p_group is None:
            p_group = self.mFamilyInfo.getAffectedGroup()

        if not self.mIsOK or not p_group:
            if filter_mode == "NOT":
                return self.getIndex().getCondEnv().getCondAll()
            return self.getIndex().getCondEnv().getCondNone()
        assert unit_name == self.getName()
        assert len(variants) > 0

        base_idx_set = self.mVariantSet.makeIdxSet(variants)
        filter_func = WS_EnumCondition.enumFilterFunc(
            filter_mode, base_idx_set)
        crit_seq = self._buildCritSeq(p_group)
        return WS_SpecCondition("zygosity", lambda record:
            filter_func(self._getIdxSet(crit_seq, record)))

#===============================================
def loadWSFilterUnit(index, unit_data):
    kind = unit_data["kind"]
    if kind == "zygosity":
        ret = ZygosityComplexUnit(index, unit_data)
        return ret if ret.isOK() else None
    if kind in ("long", "float"):
       return NumericValueUnit(index, unit_data)
    assert kind in ("enum", "presence")
    if kind == "enum" and unit_data["atomic"]:
        return StatusUnit(index, unit_data)
    if kind == "enum" and unit_data["compact"]:
        return MultiCompactUnit(index, unit_data)
    return MultiSetUnit(index, unit_data)
