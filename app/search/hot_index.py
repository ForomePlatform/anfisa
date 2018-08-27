#===============================================
class HotIndex:
    def __init__(self, data_set, legend):
        self.mDataSet = data_set
        self.mLegend  = legend
        self.mRecords = []
        for rec_no in range(self.mDataSet.getSize()):
            rec = self.mLegend.getColCount() * [None]
            self.mLegend.fillRecord(
                self.mDataSet.getRecord(rec_no).getObj(), rec)
            self.mRecords.append(rec)

    def updateHotColumns(self):
        for rec_no, rec in enumerate(self.mRecords):
            self.mLegend.updateHotRecordPart(
                self.mDataSet.getRecord(rec_no).getObj(), rec)


    def getRecNoSeq(self):
        return self.mRecNoSeq[:]

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

    def _makeStat(self, rec_no_seq, expert_mode):
        return self.mLegend.collectStatJSon(
            self._iterRecords(rec_no_seq), expert_mode)

    def makeJSonReport(self, filter_seq, random_mode, expert_mode):
        rec_no_seq = range(self.mDataSet.getSize())[:]
        for crit_info in filter_seq:
            rec_no_seq = self._applyCrit(rec_no_seq, crit_info)
            if len(rec_no_seq) == 0:
                break
        ret = self.mDataSet.makeJSonReport(
            sorted(rec_no_seq), random_mode)
        ret["stats"] = self._makeStat(rec_no_seq, expert_mode)
        return ret

    def getRecHotData(self, rec_no, expert_mode):
        return self.mLegend.getUnit("hot").getTabData(
            self.mRecords[rec_no], expert_mode)
