#===============================================
class HotIndex:
    def __init__(self, data_set, legend):
        self.mDataSet = data_set
        self.mLegend  = legend
        self.mRecords = []
        self.mFilterCache = dict()
        for rec_no in range(self.mDataSet.getSize()):
            rec = self.mLegend.getColCount() * [None]
            self.mLegend.fillRecord(
                self.mDataSet.getRecord(rec_no).getObj(), rec)
            self.mRecords.append(rec)

    def updateHotEnv(self):
        for rec_no, rec in enumerate(self.mRecords):
            self.mLegend.updateHotRecordPart(
                self.mDataSet.getRecord(rec_no).getObj(), rec)
        to_update = []
        for filter_name, filter_info in self.mFilterCache.items():
            if any([crit_info[1] == "hot"
                    for crit_info in  filter_info[0]]):
                to_update.append(filter_name)
        for filter_name in to_update:
            self.cacheFilter(filter_name,
                self.mFilterCache[filter_name][0])

    def getLegend(self):
        return self.mLegend

    @staticmethod
    def not_NONE(val):
        return val is not None

    @staticmethod
    def numeric_LE(the_val):
        return lambda val: val is not None and val >= the_val

    @staticmethod
    def numeric_GE(the_val):
        return lambda val: val is not None and val <= the_val

    @staticmethod
    def numeric_LE_U(the_val):
        return lambda val: val is None or val >= the_val

    @staticmethod
    def numeric_GE_U(the_val):
        return lambda val: val is None or val <= the_val

    @staticmethod
    def enum_OR(base_idx_set):
        return lambda idx_set: len(idx_set & base_idx_set) > 0

    @staticmethod
    def enum_AND(base_idx_set):
        all_len = len(base_idx_set)
        return lambda idx_set: len(idx_set & base_idx_set) == all_len

    @staticmethod
    def enum_NOT(base_idx_set):
        return lambda idx_set: len(idx_set & base_idx_set) == 0

    @staticmethod
    def enum_ONLY(base_idx_set):
        return lambda idx_set: (len(idx_set) > 0 and
            len(idx_set - base_idx_set) == 0)

    def _applyCrit(self, rec_no_seq, crit_info):
        if crit_info[0] == "numeric":
            unit_name, ge_mode, the_val, use_undef = crit_info[1:]
            if ge_mode > 0:
                cmp_func = (self.numeric_GE_U(the_val) if use_undef
                    else self.numeric_GE(the_val))
            elif ge_mode == 0:
                cmp_func = (self.numeric_LE_U(the_val) if use_undef
                    else self.numeric_LE(the_val))
            elif use_undef is False:
                cmp_func = self.not_NONE
            crit_f = self.mLegend.getUnit(unit_name).recordCritFunc(
                cmp_func)
        elif crit_info[0] == "enum":
            unit_name, filter_mode, variants = crit_info[1:]
            if filter_mode == "AND":
                enum_func = self.enum_AND
            elif filter_mode == "ONLY":
                enum_func = self.enum_ONLY
            elif filter_mode == "NOT":
                enum_func = self.enum_NOT
            else:
                enum_func = self.enum_OR
            crit_f = self.mLegend.getUnit(unit_name).recordCritFunc(
                enum_func, variants)
        else:
            assert False
        flt_rec_no_seq = []
        for rec_no in rec_no_seq:
            if crit_f(self.mRecords[rec_no]):
                flt_rec_no_seq.append(rec_no)
        return flt_rec_no_seq

    def _iterRecords(self, rec_no_seq):
        return [self.mRecords[rec_no]
            for rec_no in rec_no_seq]

    def cacheFilter(self, filter_name, filter_seq):
        rec_no_seq = range(self.mDataSet.getSize())[:]
        for crit_info in filter_seq:
            rec_no_seq = self._applyCrit(rec_no_seq, crit_info)
            if len(rec_no_seq) == 0:
                break
        self.mFilterCache[filter_name] = (filter_seq, rec_no_seq);

    def dropFilter(self, filter_name):
        if filter_name in self.mFilterCache:
            del self.mFilterCache[filter_name]

    def getFilterList(self):
        ret = []
        for filter_name in self.mFilterCache.keys():
            if not filter_name.startswith('_'):
                ret.append(filter_name)
        return sorted(ret)

    def makeStatReport(self, filter_name, expert_mode,
            filter_seq = None):
        if filter_seq is not None:
            self.cacheFilter(filter_name, filter_seq)
        all_filters = self.getFilterList()
        report = {
            "stat-list": self.mLegend.collectStatJSon(self._iterRecords(
                self.getRecNoSeq(filter_name)), expert_mode),
            "all-filters": all_filters,
            "filter": filter_name}
        if (filter_name in all_filters):
            report["criteria"] = self.mFilterCache[filter_name][0]
        return report

    def getRecNoSeq(self, filter_name = None):
        if filter_name in self.mFilterCache:
            return self.mFilterCache[filter_name][1]
        return range(self.mDataSet.getSize())[:]

    def getRecFilters(self, rec_no):
        ret = []
        for filter_name, flt_info in self.mFilterCache.items():
            if (not filter_name.startswith('_') and
                    rec_no in flt_info[1]):
                ret.append(filter_name)
        return sorted(ret)
