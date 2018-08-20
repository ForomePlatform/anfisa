#import sys
import abc
from collections import Counter

import val_conv
from .column import DataPortion, DataColumn
from .extract import DataExtractor
from .val_stat import EnumStat

#===============================================
class FilterUnit:
    def __init__(self, legend, name, title = None):
        self.mLegend = legend
        self.mName = name
        self.mTitle = title if title else name
        self.mUnitIdx = self.mLegend._regUnit(self)

    def getLegend(self):
        return self.mLegend

    def getName(self):
        return self.mName

    def getTitle(self):
        return self.mTitle

    def getUnitIdx(self):
        return self.mUnitIdx

    @abc.abstractmethod
    def iterExtractors(self):
        pass

    @abc.abstractmethod
    def collectStatJSon(self, data_records):
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

#===============================================
class IntValueUnit(FilterUnit):
    def __init__(self, legend, name, path,
            title = None, default_value = None, diap = None):
        FilterUnit.__init__(self, legend, name, title)
        self.mExtractor = DataExtractor(self, name, path,
            val_conv.IntConvertor(default_value, diap),
            DataColumn(self, name, DataPortion.ATOM_DATA_TYPE_INT))

    def getColumn(self):
        return self.mExtractor.getDataP()

    def iterExtractors(self):
        yield self.mExtractor

    def collectStatJSon(self, data_records):
        col = self.mExtractor.getDataP()
        stat = self.mExtractor.getVConv().newStat()
        for data_rec in data_records:
            stat.regValue(col.recordValue(data_rec))
        return stat.getJSon(self.getName())

#===============================================
class FloatValueUnit(FilterUnit):
    def __init__(self, legend, name, path,
            title = None, default_value = None, diap = None):
        FilterUnit.__init__(self, legend, name, title)
        self.mExtractor = DataExtractor(self, name, path,
            val_conv.FloatConvertor(default_value, diap),
            DataColumn(self, name, DataPortion.ATOM_DATA_TYPE_FLOAT))

    def getColumn(self):
        return self.mExtractor.getDataP()

    def iterExtractors(self):
        yield self.mExtractor

    def collectStatJSon(self, data_records):
        col = self.mExtractor.getDataP()
        stat = self.mExtractor.getVConv().newStat()
        for data_rec in data_records:
            stat.regValue(col.recordValue(data_rec))
        return stat.getJSon(self.getName())

#===============================================
class StatusUnit(FilterUnit):
    def __init__(self, legend, name, path,
            variants = None, title = None, default_value = False):
        FilterUnit.__init__(self, legend, name, title)
        self.mExtractor = DataExtractor(self, name, path,
            val_conv.EnumConvertor(variants, atomic_mode = True,
                default_value = default_value),
            DataColumn(self, name, DataPortion.ATOM_DATA_TYPE_INT))

    def iterExtractors(self):
        yield self.mExtractor

    def collectStatJSon(self, data_records):
        col = self.mExtractor.getDataP()
        stat = self.mExtractor.getVConv().newStat()
        for data_rec in data_records:
            stat.regValues([col.recordValue(data_rec)])
        return stat.getJSon(self.getName(), enum_type = "status")

#===============================================
class PresenceUnit(FilterUnit):
    def __init__(self, legend, name, var_info_seq, title = None):
        FilterUnit.__init__(self, legend, name, title)
        self.mExtractors = []
        for it_name, it_path in var_info_seq:
            full_name = "%s.%s" % (name, it_name)
            self.mExtractors.append(DataExtractor(self, full_name,
                it_path, val_conv.BoolConvertor(),
                DataColumn(self, full_name, DataPortion.ATOM_DATA_TYPE_BOOL)))

    def iterExtractors(self):
        return iter(self.mExtractors)

    def collectStatJSon(self, data_records):
        variants = []
        col_seq = []
        for extr in self.mExtractors:
            variants.append(extr.getName())
            col_seq.append(extr.getDataP())
        stat = EnumStat(variants)
        for data_rec in data_records:
            for var_no, col in enumerate(col_seq):
                if col.recordValue(data_rec):
                    stat.regValues([var_no])
        return stat.getJSon(self.getName(), enum_type = "presence")

#===============================================
class MultiStatusUnit(FilterUnit):
    def __init__(self, legend, name, path, variants = None,
            title = None, chunker = None, compact_mode = False,
            default_value = False, others_value = False):
        FilterUnit.__init__(self, legend, name, title)
        self.mExtractors = [DataExtractor(self, name, path,
            val_conv.EnumConvertor(variants, chunker = chunker,
                default_value = default_value, others_value = others_value),
            compact_mode = compact_mode)]

    def iterExtractors(self):
        return iter(self.mExtractors)

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
        return stat.getJSon(self.getName())
