#import sys
import abc, logging
from collections import Counter

import val_conv
from app.model.types import Types
from .column import DataPortion, DataColumn
from .extract import DataExtractor, DataGroupExtractor
from .val_stat import EnumStat

#===============================================
class FilterUnit:
    def __init__(self, legend, name, title, research_only):
        self.mLegend = legend
        self.mName = name
        self.mTitle = title
        self.mUnitIdx = self.mLegend._regUnit(self)
        self.mResearchOnly = research_only
        self.mVGroup = self.mLegend._getCurVGroup()
        if self.mVGroup:
            self.mVGroup._regUnit(self)
        self.mExtractor = None

    def _initExtractor(self, extractor):
        self.mExtractor = extractor

    def getLegend(self):
        return self.mLegend

    def getName(self):
        return self.mName

    def getExtractor(self):
        return self.mExtractor

    def getTitle(self):
        return self.mTitle

    def getUnitIdx(self):
        return self.mUnitIdx

    def getVGroup(self):
        return self.mVGroup

    def getNames(self):
        return {
            "name": self.mName,
            "title": self.mTitle,
            "vgroup": self.mVGroup.getTitle() if self.mVGroup else None}

    def checkResearchBlock(self, research_mode):
        return (not research_mode) and self.mResearchOnly

    @abc.abstractmethod
    def getType(self):
        return None

    @abc.abstractmethod
    def collectStatJSon(self, data_records):
        return None

    @abc.abstractmethod
    def ruleValue(self, data_rec):
        return None

    def testValues(self, obj):
        return self.mExtractor.testValues(obj)

    def setup(self, rep_out):
        self.mExtractor.setup(rep_out)

    def fillRecord(self, obj, record):
        self.mExtractor.extract(obj, record)

    def _testValue(self, value, kind, msg, add_crit = True):
        if kind not in Types.detectValTypes(value) or not add_crit:
            logging.fatal("Unit %s: bad %s %s: %r" %
                (self.mName, kind, msg, value))

#===============================================
class _NumericValueUnit(FilterUnit):
    def __init__(self, legend, name, path, title,
            research_only, convertor, atom_type):
        FilterUnit.__init__(self, legend, name, title, research_only)
        self._initExtractor(DataExtractor(self, name, path,
            convertor, DataColumn(self, name, atom_type)))

    def _testSetup(self, default_value, diap, test_type):
        if default_value is not None:
            self._testValue(default_value, test_type, "default value")
        if diap is not None:
            self._testValue(diap[0], test_type, "diap min")
            self._testValue(diap[1], test_type, "diap max",
                diap[0] <= diap[1])

    def recordCondFunc(self, cmp_func):
        col = self.getExtractor().getDataP()
        return lambda data_rec: cmp_func(col.recordValue(data_rec))

    def ruleValue(self, data_rec):
        return self.getExtractor().getDataP().recordValue(data_rec)

    def collectStatJSon(self, data_records):
        col = self.getExtractor().getDataP()
        stat = self.getExtractor().getVConv().newStat()
        for data_rec in data_records:
            stat.regValue(col.recordValue(data_rec))
        return stat.getJSon(self.getNames())

#===============================================
class IntValueUnit(_NumericValueUnit):
    def __init__(self, legend, name, path, title = None,
            default_value = None, diap = None, research_only = False):
        _NumericValueUnit.__init__(self,
            legend, name, path, title, research_only,
            val_conv.IntConvertor(default_value, diap),
            DataPortion.ATOM_DATA_TYPE_INT)
        self._testSetup(default_value, diap, "int")

    def getType(self):
        return "long"

#===============================================
class FloatValueUnit(_NumericValueUnit):
    def __init__(self, legend, name, path, title = None,
            default_value = None, diap = None, research_only = False):
        _NumericValueUnit.__init__(self,
            legend, name, path, title, research_only,
            val_conv.FloatConvertor(default_value, diap),
            DataPortion.ATOM_DATA_TYPE_FLOAT)
        self._testSetup(default_value, diap, "numeric")

    def getType(self):
        return "float"

#===============================================
class StatusUnit(FilterUnit):
    def __init__(self, legend, name, path, variants = None,
            title = None, default_value = False,
            research_only = False, accept_wrong_values = False):
        FilterUnit.__init__(self, legend, name, title, research_only)
        self._initExtractor(DataExtractor(self, name, path,
            val_conv.EnumConvertor(variants,
            atomic_mode = True, default_value = default_value,
            others_value = accept_wrong_values),
            DataColumn(self, name, DataPortion.ATOM_DATA_TYPE_INT)))
        if default_value not in (None, False):
            self._testValue(default_value, "string", "default value")

    def getType(self):
        return "status"

    def recordCondFunc(self, enum_func, variants):
        col = self.getExtractor().getDataP()
        idx_set = self.getExtractor().getVariantSet().makeIdxSet(
            variants)
        check_func = enum_func(idx_set)
        return lambda data_rec: check_func({col.recordValue(data_rec)})

    def ruleValue(self, data_rec):
        idx = self.getExtractor().getDataP().recordValue(data_rec)
        return self.getExtractor().getVariantSet().getValue(idx)

    def collectStatJSon(self, data_records):
        col = self.getExtractor().getDataP()
        stat = self.getExtractor().getVConv().newStat()
        for data_rec in data_records:
            stat.regValues([col.recordValue(data_rec)])
        return stat.getJSon(self.getNames(), enum_type = "status")

#===============================================
class BoolSetUnit(FilterUnit):
    def __init__(self, legend, name, variants, title = None,
            enum_type = "presence", research_only = False):
        FilterUnit.__init__(self, legend, name, title, research_only)
        self.mColumns = [DataColumn(self, "%s__%s" % (name, variant),
            DataPortion.ATOM_DATA_TYPE_BOOL) for variant in variants]
        self.mEnumType = enum_type
        self._initExtractor(DataGroupExtractor(variants))

    def getType(self):
        return "bool-set"

    def enumColumns(self):
        return enumerate(self.mColumns)

    def _recordValues(self, data_rec):
        ret = set()
        for idx, col in enumerate(self.mColumns):
            if col.recordValue(data_rec):
                ret.add(idx)
        return ret

    def ruleValue(self, data_rec):
        idxs = self._recordValues(data_rec)
        return self.getExtractor().getVariantSet().makeValueSet(idxs)

    def recordCondFunc(self, enum_func, variants):
        check_func = enum_func(self.getExtractor().
            getVariantSet().makeIdxSet(variants))
        return lambda data_rec: check_func(self._recordValues(data_rec))

    def collectStatJSon(self, data_records):
        stat = EnumStat(self.getExtractor().getVariantSet())
        for data_rec in data_records:
            for var_no, col in enumerate(self.mColumns):
                if col.recordValue(data_rec):
                    stat.regValues([var_no])
        return stat.getJSon(self.getNames(), enum_type = self.mEnumType)

#===============================================
class PresenceUnit(BoolSetUnit):
    def __init__(self, legend, name, var_info_seq,
            title = None, research_only = False):
        BoolSetUnit.__init__(self, legend, name,
            [it_name for it_name, it_path in var_info_seq],
            title, research_only = research_only)
        for idx, col in self.enumColumns():
            it_name, it_path = var_info_seq[idx]
            self.getExtractor()._add(DataExtractor(self,
                it_name, it_path, val_conv.BoolConvertor(), col))

#===============================================
class MultiStatusUnit(FilterUnit):
    def __init__(self, legend, name, path, variants = None,
            title = None, chunker = None, compact_mode = False,
            default_value = False, others_value = False,
            research_only = False):
        FilterUnit.__init__(self, legend, name, title, research_only)
        self._initExtractor(DataExtractor(self, name, path,
            val_conv.EnumConvertor(variants,
                chunker = chunker, default_value = default_value,
                others_value = others_value),
            compact_mode = compact_mode))
        if default_value not in (None, False):
            self._testValue(default_value, "string", "default value")

    def getType(self):
        return "multi-set"

    def recordCondFunc(self, enum_func, variants):
        datap = self.getExtractor().getDataP()
        check_func = enum_func(self.getExtractor().
            getVariantSet().makeIdxSet(variants))
        if datap.isAtomic():
            return lambda data_rec: check_func(
                set(datap.getSetByIdx(datap.recordValue(data_rec))))
        return lambda data_rec: check_func(datap.recordValues(data_rec))

    def ruleValue(self, data_rec):
        col = self.getExtractor().getDataP()
        if col.isAtomic():
            idx_set = col.getSetByIdx(col.recordValue(data_rec))
        else:
            idx_set = col.recordValues(data_rec)
        return self.getExtractor().getVariantSet().makeValueSet(
            idx_set)

    def collectStatJSon(self, data_records):
        col = self.getExtractor().getDataP()
        stat = self.getExtractor().getVConv().newStat()
        if col.isAtomic():
            counts = Counter()
            for data_rec in data_records:
                counts[col.recordValue(data_rec)] += 1
            for var_idx, cnt in counts.items():
                stat.regValues(col.getSetByIdx(var_idx), cnt)
        else:
            for data_rec in data_records:
                stat.regValues(col.recordValues(data_rec))
        return stat.getJSon(self.getNames())
