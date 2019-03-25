#import sys
import abc

from app.model.variants import VariantSet
from app.model.a_config import AnfisaConfig
from app.model.condition import ConditionMaker
from .val_stat import NumDiapStat, EnumStat
from .flt_cond import WS_SpecCondition, WS_All, WS_None, WS_EnumCondition
#===============================================
class FilterUnit:
    def __init__(self, index, unit_data, unit_idx):
        self.mIndex = index
        self.mData = unit_data
        self.mUnitIdx = unit_idx
        self.mName = unit_data["name"]
        self.mTitle = unit_data["title"]
        self.mUnitKind = unit_data["kind"]
        self.mResearchOnly = unit_data["research"]
        self.mVGroupTitle = unit_data.get("vgroup")
        self.mRenderMode = unit_data.get("render")
        self.mExtractor = None

    def setup(self):
        pass

    def getIndex(self):
        return self.mIndex

    def getName(self):
        return self.mName

    def getTitle(self):
        return self.mTitle

    def getUnitIdx(self):
        return self.mUnitIdx

    def getVGroupTitle(self):
        return self.mVGroupTitle

    def getUnitKind(self):
        return self.mUnitKind

    def getData(self):
        return self.mData

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

    def getVariants(self):
        variants_info = self.mData.get("variants")
        if variants_info is None:
            return None, True
        return (VariantSet([info[0] for info in variants_info]),
            sum([info[1] for info in variants_info]) == 0)

    def checkResearchBlock(self, research_mode):
        return (not research_mode) and self.mResearchOnly

    @abc.abstractmethod
    def makeStat(self, data_records, repr_context = None):
        return None

    @abc.abstractmethod
    def fillRecord(self, obj, record):
        assert False

#===============================================
class NumericValueUnit(FilterUnit):
    def __init__(self, index, dc_collection,
            unit_data, unit_idx):
        FilterUnit.__init__(self, index, unit_data, unit_idx)
        self.mAtomType = ("float"
            if unit_data["kind"] == "float" else "int")
        self.mScreened = self.getData()["min"] is None
        self.mColumn = dc_collection.makeColumn(self,
            self.getName(), dc_collection.ATOM_DATA_TYPE_FLOAT
            if self.mAtomType == "float" else
            dc_collection.ATOM_DATA_TYPE_INT)
        self.getIndex().getCondEnv().addNumFieldF(
            self.getName(), self.mColumn.recordValue)

    def getAtomType(self):
        return self.mAtomType

    def isScreened(self):
        return self.mScreened

    def makeStat(self, data_records, repr_context = None):
        stat = NumDiapStat(self.mAtomType, self.dumpNames())
        for data_rec in data_records:
            stat.regValue(self.mColumn.recordValue(data_rec))
        return stat.dump()

    def fillRecord(self, inp_data, record):
        value = inp_data.get(self.getName())
        self.mColumn.setValue(record, value)

#===============================================
class StatusUnit(FilterUnit):
    def __init__(self, index, dc_collection, unit_data, unit_idx):
        FilterUnit.__init__(self, index, unit_data, unit_idx)
        self.mVariantSet, self.mScreened = self.getVariants()
        self.mColumn = dc_collection.makeColumn(self,
            self.getName(), dc_collection.ATOM_DATA_TYPE_INT)
        self.getIndex().getCondEnv().addEnumFieldF(
            self.getName(), self.mVariantSet,
            lambda record: {self.mColumn.recordValue(record)})

    def isScreened(self):
        return self.mScreened

    def getVariantSet(self):
        return self.mVariantSet

    def makeStat(self, data_records, repr_context = None):
        stat = EnumStat(self.mVariantSet, self.dumpNames(), "status")
        for data_rec in data_records:
            stat.regValues({self.mColumn.recordValue(data_rec)})
        return stat.dump()

    def fillRecord(self, inp_data, record):
        value = inp_data[self.getName()]
        self.mColumn.setValue(record, self.mVariantSet.indexOf(value))

#===============================================
class MultiSetUnit(FilterUnit):
    def __init__(self, index, dc_collection, unit_data, unit_idx):
        FilterUnit.__init__(self, index, unit_data, unit_idx)
        self.mVariantSet, self.mScreened = self.getVariants()
        self.mColumns = dc_collection.makeColumnSet(self,
            self.getName(), iter(self.mVariantSet))
        self.getIndex().getCondEnv().addEnumFieldF(
            self.getName(), self.mVariantSet,
            self.mColumns.recordValues)

    def isAtomic(self):
        return False

    def isScreened(self):
        return self.mScreened

    def getVariantSet(self):
        return self.mVariantSet

    def enumColumns(self):
        return enumerate(self.mColumns)

    def makeStat(self, data_records, repr_context = None):
        stat = EnumStat(self.mVariantSet, self.dumpNames(), "enum")
        for data_rec in data_records:
            stat.regValues(self.mColumns.recordValues(data_rec))
        return stat.dump()

    def fillRecord(self, inp_data, record):
        values = inp_data.get(self.getName())
        if values :
            self.mColumns.setValues(record,
                self.mVariantSet.makeIdxSet(values))

#===============================================
class MultiCompactUnit(FilterUnit):
    def __init__(self, index, dc_collection, unit_data, unit_idx):
        FilterUnit.__init__(self, index, unit_data, unit_idx)
        self.mVariantSet, self.mScreened = self.getVariants()
        self.mColumn = dc_collection.makeCompactEnumColumn(
            self, self.getName())
        self.getIndex().getCondEnv().addEnumFieldF(
            self.getName(), self.mVariantSet,
            self.mColumn.recordValues)

    def isAtomic(self):
        return False

    def isScreened(self):
        return self.mScreened

    def getVariantSet(self):
        return self.mVariantSet

    def makeStat(self, data_records, repr_context = None):
        stat = EnumStat(self.mVariantSet, self.dumpNames(), "enum")
        for data_rec in data_records:
            stat.regValues(self.mColumn.recordValues(data_rec))
        return stat.dump()

    def fillRecord(self, inp_data, record):
        values = inp_data.get(self.getName())
        if values :
            self.mColumn.setValues(record,
                self.mVariantSet.makeIdxSet(values))

#===============================================
class ZygosityComplexUnit(FilterUnit):
    def __init__(self, index, dc_collection, unit_data, unit_idx):
        FilterUnit.__init__(self, index, unit_data, unit_idx)

        self.mScreened = (self.getIndex().getWS().getApp().
            hasRunOption("no-custom"))
        self.mFamilyInfo = self.getIndex().getWS().getFamilyInfo()
        assert ("size" not in unit_data or
            unit_data["size"] == len(self.mFamilyInfo))
        self.mIsOK = (self.mFamilyInfo is not None and
            len(self.mFamilyInfo) > 1)
        if not self.mIsOK:
            return
        self.mColumns = [dc_collection.makeColumn(self,
            "%s_%d" % (self.getName(), idx), dc_collection.ATOM_DATA_TYPE_INT)
            for idx, member_name in enumerate(self.mFamilyInfo.getMembers())]
        self.mConfig = unit_data.get("config", dict())
        self.mXCondition = None
        labels = AnfisaConfig.configOption("zygosity.cases")
        self.mVariantSet = VariantSet([labels[key]
            for key in ("homo_recess", "x_linked", "dominant", "compens")])
        self.getIndex().getCondEnv().addSpecialParse(
            self.getName(), self.parseZCondition)

    def setup(self):
        self.mXCondition = self.getIndex().getCondEnv().parse(
            self.mConfig.get("x_cond",
            ConditionMaker.condEnum("Chromosome", ["chrX"])))

    def isAtomic(self):
        return False

    def isScreened(self):
        return self.mScreened

    def isOK(self):
        return self.mIsOK

    def fillRecord(self, inp_data, record):
        for col_h in self.mColumns:
            col_h.setValue(record, inp_data.get(col_h.getName()))

    def _makeCrit(self, idx, min_v, max_v = None):
        column = self.mColumns[idx]
        if min_v is not None:
            return lambda record: column.recordValue(record) >= min_v
        return lambda record: column.recordValue(record) <= max_v

    @staticmethod
    def _joinAnd(seq):
        return lambda record: all([f(record) for f in seq])

    def condZHomoRecess(self, problem_group):
        seq = []
        for idx in range(len(self.mFamilyInfo)):
            if idx in problem_group:
                seq.append(self._makeCrit(idx, 2, None))
            else:
                seq.append(self._makeCrit(idx, None, 1))
        return WS_SpecCondition("ZHomoRecess", self._joinAnd(seq))

    def _condZDominant(self, problem_group):
        seq = []
        for idx in range(len(self.mFamilyInfo)):
            if idx in problem_group:
                seq.append(self._makeCrit(idx, 1, None))
            else:
                seq.append(self._makeCrit(idx, None, 0))
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
                seq.append(self._makeCrit(idx, None, 0))
            else:
                seq.append(self._makeCrit(idx, 1, None))
        return WS_SpecCondition("ZCompens", self._joinAnd(seq))

    def _buildCritSeq(self, p_group):
        return [
            self.condZHomoRecess(p_group),
            self.condZXLinked(p_group),
            self.condZDominant(p_group),
            self.conditionZCompens(p_group)]

    def makeStat(self, data_records, repr_context = None):
        info = self.dumpNames()
        info["family"] = self.mFamilyInfo.getTitles()
        info["affected"] = self.mFamilyInfo.getAffectedGroup()

        if repr_context is None or "problem_group" not in repr_context:
            p_group = self.mFamilyInfo.getAffectedGroup()
        else:
            p_group = {m_idx if 0 <= m_idx < len(self.mFamilyInfo)
                else None for m_idx in repr_context["problem_group"]}
            if None in p_group:
                p_group.remove(None)
        if len(p_group) == 0:
            return ["zygosity", info, sorted(p_group), None]

        stat = EnumStat(self.mVariantSet, info, "zygosity")
        crit_seq = self._buildCritSeq(p_group)
        for data_rec in data_records:
            idx_set = set()
            for idx, crit in enumerate(crit_seq):
                if crit(data_rec):
                    idx_set.add(idx)
            stat.regValues(idx_set)
        return ["zygosity", info, sorted(p_group), stat.dump()[-1]]

    @staticmethod
    def _getIdxSet(crit_seq, record):
        ret = set()
        for idx, crit in enumerate(crit_seq):
            if crit(record):
                ret.add(idx)
        return ret

    def parseZCondition(self, cond_info):
        assert cond_info[0] == "zygosity"
        unit_name, p_group, filter_mode, variants = cond_info[1:]

        if not self.mIsOK or not p_group:
            if filter_mode == "NOT":
                return WS_All()
            return WS_None()
        assert unit_name == self.getName()
        assert len(variants) > 0

        base_idx_set = self.mVariantSet.makeIdxSet(variants)
        filter_func = WS_EnumCondition.enumFilterFunc(
            filter_mode, base_idx_set)
        crit_seq = self._buildCritSeq(p_group)
        return WS_SpecCondition("zygosity", lambda record:
            filter_func(self._getIdxSet(crit_seq, record)))

#===============================================
def loadWSFilterUnit(index, dc_collection, unit_data, unit_idx):
    kind = unit_data["kind"]
    if kind == "zygosity":
        ret = ZygosityComplexUnit(index, dc_collection, unit_data, unit_idx)
        return ret if ret.isOK() else None
    if kind in ("long", "float"):
       return NumericValueUnit(index, dc_collection, unit_data, unit_idx)
    assert kind in ("enum", "presence")
    if kind == "enum" and unit_data["atomic"]:
        return StatusUnit(index, dc_collection, unit_data, unit_idx)
    if kind == "enum" and unit_data["compact"]:
        return MultiCompactUnit(index, dc_collection, unit_data, unit_idx)
    return MultiSetUnit(index, dc_collection, unit_data, unit_idx)
