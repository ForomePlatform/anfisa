#import sys
import abc

from app.model.variants import VariantSet
from .val_stat import NumDiapStat, EnumStat
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
        self.mExtractor = None

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
        return {
            "name": self.mName,
            "title": self.mTitle,
            "vgroup": self.mVGroupTitle}

    def getVariants(self):
        variants_info = self.mData.get("variants")
        if variants_info is None:
            return None
        return [info[0] for info in variants_info]

    def checkResearchBlock(self, research_mode):
        return (not research_mode) and self.mResearchOnly

    @abc.abstractmethod
    def collectStatJSon(self, data_records):
        return None

    @abc.abstractmethod
    def fillRecord(self, obj, record):
        assert False

#===============================================
class NumericValueUnit(FilterUnit):
    def __init__(self, index, dc_collection,
            unit_data, unit_idx, atom_type):
        FilterUnit.__init__(self, index, unit_data, unit_idx)
        self.mAtomType = atom_type
        self.mColumn = dc_collection.makeColumn(self,
            self.getName(), dc_collection.ATOM_DATA_TYPE_FLOAT
            if atom_type == "float" else dc_collection.ATOM_DATA_TYPE_INT)

    def getAtomType(self):
        return self.mAtomType

    def recordCondFunc(self, cond_func):
        return lambda data_rec: cond_func(
            self.mColumn.recordValue(data_rec))

    def collectStatJSon(self, data_records):
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
        self.mVariantSet = VariantSet(self.getVariants())
        self.mColumn = dc_collection.makeColumn(self,
            self.getName(), dc_collection.ATOM_DATA_TYPE_INT)

    def getVariantSet(self):
        return self.mVariantSet

    def recordCondFunc(self, cond_func):
        return lambda data_rec: cond_func(
            {self.mColumn.recordValue(data_rec)})

    def collectStatJSon(self, data_records):
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
        self.mVariantSet = VariantSet(self.getVariants())
        self.mColumns = dc_collection.makeColumnSet(self,
            self.getName(), iter(self.mVariantSet))

    def isAtomic(self):
        return False

    def getVariantSet(self):
        return self.mVariantSet

    def enumColumns(self):
        return enumerate(self.mColumns)

    def recordCondFunc(self, cond_func):
        return lambda data_rec: cond_func(
            self.mColumns.recordValues(data_rec))

    def collectStatJSon(self, data_records):
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
        self.mVariantSet = VariantSet(self.getVariants())
        self.mColumn = dc_collection.makeCompactEnumColumn(
            self, self.getName())

    def isAtomic(self):
        return False

    def getVariantSet(self):
        return self.mVariantSet

    def recordCondFunc(self, cond_func):
        return lambda data_rec: cond_func(
            self.mColumn.recordValues(data_rec))

    def collectStatJSon(self, data_records):
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
def loadWSFilterUnit(index, dc_collection, unit_data, unit_idx):
    kind = unit_data["kind"]
    if kind == "zygosity":
        return None
    if kind in ("long", "float"):
       return NumericValueUnit(index, dc_collection,
            unit_data, unit_idx, "float" if kind == "float" else "int")
    assert kind in ("enum", "presence")
    if kind == "enum" and unit_data["atomic"]:
        return StatusUnit(index, dc_collection, unit_data, unit_idx)
    if kind == "enum" and unit_data["compact"]:
        return MultiCompactUnit(index, dc_collection, unit_data, unit_idx)
    return MultiSetUnit(index, dc_collection, unit_data, unit_idx)
