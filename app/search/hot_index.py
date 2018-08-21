#===============================================
class HotIndex:
    def __init__(self, data_set, legend):
        self.mDataSet = data_set
        self.mLegend  = legend
        self.mRecords = []
        for rec_no in range(self.mDataSet.getNRecords()):
            rec = self.mLegend.getColCount() * [None]
            self.mLegend.fillRecord(
                self.mDataSet.getRecord(rec_no).getObj(), rec)
            self.mRecords.append(rec)

    def getRecNoSeq(self):
        return self.mRecNoSeq[:]

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
        return lambda val: val is None and val <= the_val

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
            if ge_mode:
                cmp_func = (self.numeric_GE_U(the_val) if use_undef
                    else self.numeric_GE(the_val))
            else:
                cmp_func = (self.numeric_LE_U(the_val) if use_undef
                    else self.numeric_LE(the_val))
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

    def _makeStat(self, rec_no_seq):
        return self.mLegend.collectStatJSon(self._iterRecords(rec_no_seq))

    def makeJSonReport(self, filter_seq):
        rec_no_seq = range(self.mDataSet.getNRecords())[:]
        for crit_info in filter_seq:
            rec_no_seq = self._applyCrit(rec_no_seq, crit_info)
            if len(rec_no_seq) == 0:
                break
        ret = self.mDataSet.makeJSonReport(sorted(rec_no_seq))
        ret["stats"] = self._makeStat(rec_no_seq)
        return ret
