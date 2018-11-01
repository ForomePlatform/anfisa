#import sys
import abc, logging
from collections import Counter

import val_conv
from app.model.types import Types
from .column import DataPortion, DataColumn
from .extract import DataExtractor
from .val_stat import EnumStat
from .variants import VariantSet

#===============================================
class FilterUnit:
    def __init__(self, legend, name,
            title = None, research_only = False):
        self.mLegend = legend
        self.mName = name
        self.mTitle = title
        self.mUnitIdx = self.mLegend._regUnit(self)
        self.mResearchOnly = research_only
        self.mVGroup = self.mLegend._getCurVGroup()
        if self.mVGroup:
            self.mVGroup._regUnit(self)

    def getLegend(self):
        return self.mLegend

    def getName(self):
        return self.mName

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
    def iterExtractors(self):
        pass

    @abc.abstractmethod
    def collectStatJSon(self, data_records):
        return None

    @abc.abstractmethod
    def ruleValue(self, data_rec):
        return None

    def testValues(self, obj):
        is_ok = True
        for extr_h in self.iterExtractors():
            is_ok |= extr_h.testValues(obj)
        return is_ok

    def setup(self, rep_out):
        for extr_h in self.iterExtractors():
            extr_h.setup(rep_out)

    def fillRecord(self, obj, record):
        for extr_h in self.iterExtractors():
            extr_h.extract(obj, record)

    def _testValue(self, value, kind, msg, add_crit = True):
        if kind not in Types.detectValTypes(value) or not add_crit:
            logging.fatal("Unit %s: bad %s %s: %r" %
                (self.mName, kind, msg, value))

#===============================================
class IntValueUnit(FilterUnit):
    def __init__(self, legend, name, path, title = None,
            default_value = None, diap = None, research_only = False):
        FilterUnit.__init__(self, legend, name, title, research_only)
        if default_value is not None:
            self._testValue(default_value, "int", "default value")
        if diap is not None:
            self._testValue(diap[0], "int", "diap min")
            self._testValue(diap[1], "int", "diap max", diap[0] <= diap[1])
        self.mExtractor = DataExtractor(self, name, path,
            val_conv.IntConvertor(default_value, diap),
            DataColumn(self, name, DataPortion.ATOM_DATA_TYPE_INT))

    def recordCondFunc(self, cmp_func):
        col = self.mExtractor.getDataP()
        return lambda data_rec: cmp_func(col.recordValue(data_rec))

    def iterExtractors(self):
        yield self.mExtractor

    def ruleValue(self, data_rec):
        return self.mExtractor.getDataP().recordValue(data_rec)

    def collectStatJSon(self, data_records):
        col = self.mExtractor.getDataP()
        stat = self.mExtractor.getVConv().newStat()
        for data_rec in data_records:
            stat.regValue(col.recordValue(data_rec))
        return stat.getJSon(self.getNames())

#===============================================
class FloatValueUnit(FilterUnit):
    def __init__(self, legend, name, path, title = None,
            default_value = None, diap = None, research_only = False):
        FilterUnit.__init__(self, legend, name, title, research_only)
        if default_value is not None:
            self._testValue(default_value, "numeric", "default value")
        if diap is not None:
            self._testValue(diap[0], "numeric", "diap min")
            self._testValue(diap[1], "numeric", "diap max", diap[0] <= diap[1])
        self.mExtractor = DataExtractor(self, name, path,
            val_conv.FloatConvertor(default_value, diap),
            DataColumn(self, name, DataPortion.ATOM_DATA_TYPE_FLOAT))

    def recordCondFunc(self, cmp_func):
        col = self.mExtractor.getDataP()
        return lambda data_rec: cmp_func(col.recordValue(data_rec))

    def iterExtractors(self):
        yield self.mExtractor

    def ruleValue(self, data_rec):
        return self.mExtractor.getDataP().recordValue(data_rec)

    def collectStatJSon(self, data_records):
        col = self.mExtractor.getDataP()
        stat = self.mExtractor.getVConv().newStat()
        for data_rec in data_records:
            stat.regValue(col.recordValue(data_rec))
        return stat.getJSon(self.getNames())

#===============================================
class StatusUnit(FilterUnit):
    def __init__(self, legend, name, path, variants = None,
            title = None, default_value = False,
            research_only = False, accept_wrong_values = False):
        FilterUnit.__init__(self, legend, name, title, research_only)
        if default_value not in (None, False):
            self._testValue(default_value, "string", "default value")
        self.mExtractor = DataExtractor(self, name, path,
            val_conv.EnumConvertor(VariantSet.create(variants),
                atomic_mode = True, default_value = default_value,
                others_value = accept_wrong_values),
            DataColumn(self, name, DataPortion.ATOM_DATA_TYPE_INT))

    def iterExtractors(self):
        yield self.mExtractor

    def getVariantSet(self):
        return self.mExtractor.getVConv().getVariantSet()

    def recordCondFunc(self, enum_func, variants):
        col = self.mExtractor.getDataP()
        idx_set = self.mExtractor.getVConv().getVariantSet().makeIdxSet(
            variants)
        check_func = enum_func(idx_set)
        return lambda data_rec: check_func({col.recordValue(data_rec)})

    def ruleValue(self, data_rec):
        idx = self.mExtractor.getDataP().recordValue(data_rec)
        return self.mExtractor.getVConv().getVariantSet().getValue(idx)

    def collectStatJSon(self, data_records):
        col = self.mExtractor.getDataP()
        stat = self.mExtractor.getVConv().newStat()
        for data_rec in data_records:
            stat.regValues([col.recordValue(data_rec)])
        return stat.getJSon(self.getNames(), enum_type = "status")

#===============================================
class BoolSetUnit(FilterUnit):
    def __init__(self, legend, name, variants, title = None,
            enum_type = "presence", research_only = False):
        FilterUnit.__init__(self, legend, name, title, research_only)
        self.mColumns = [DataColumn(self, "%s.%s" % (name, variant),
            DataPortion.ATOM_DATA_TYPE_BOOL) for variant in variants]
        self.mEnumType = enum_type
        self.mVariantSet = VariantSet(variants)

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
        return self.mVariantSet.makeValueSet(idxs)

    def recordCondFunc(self, enum_func, variants):
        check_func = enum_func(self.mVariantSet.makeIdxSet(variants))
        return lambda data_rec: check_func(self._recordValues(data_rec))

    def collectStatJSon(self, data_records):
        stat = EnumStat(self.mVariantSet)
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
        self.mExtractors = []
        for idx, col in self.enumColumns():
            it_name, it_path = var_info_seq[idx]
            self.mExtractors.append(DataExtractor(self, it_name,
                it_path, val_conv.BoolConvertor(), col))

    def iterExtractors(self):
        return iter(self.mExtractors)

#===============================================
class MultiStatusUnit(FilterUnit):
    def __init__(self, legend, name, path, variants = None,
            title = None, chunker = None, compact_mode = False,
            default_value = False, others_value = False,
            research_only = False):
        FilterUnit.__init__(self, legend, name, title, research_only)
        if default_value not in (None, False):
            self._testValue(default_value, "string", "default value")
        self.mExtractors = [DataExtractor(self, name, path,
            val_conv.EnumConvertor(VariantSet.create(variants),
                chunker = chunker, default_value = default_value,
                others_value = others_value),
            compact_mode = compact_mode)]

    def iterExtractors(self):
        return iter(self.mExtractors)

    def getVariantSet(self):
        return self.mExtractors[0].getVConv().getVariantSet()

    def recordCondFunc(self, enum_func, variants):
        datap = self.mExtractors[0].getDataP()
        check_func = enum_func(self.mExtractors[0].getVConv().
            getVariantSet().makeIdxSet(variants))
        if datap.isAtomic():
            return lambda data_rec: check_func(
                set(datap.getSetByIdx(datap.recordValue(data_rec))))
        return lambda data_rec: check_func(datap.recordValues(data_rec))

    def ruleValue(self, data_rec):
        col = self.mExtractors[0].getDataP()
        if col.isAtomic():
            idx_set = col.getSetByIdx(col.recordValue(data_rec))
        else:
            idx_set = col.recordValues(data_rec)
        return self.mExtractors[0].getVConv().getVariantSet().makeValueSet(
            idx_set)

    def collectStatJSon(self, data_records):
        col = self.mExtractors[0].getDataP()
        stat = self.mExtractors[0].getVConv().newStat()
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
