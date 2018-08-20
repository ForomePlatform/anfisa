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

    def _applyCrit(self, rec_no_seq, crit_info):
        if crit_info[0] == "numeric":
            unit_name, lt_mode, the_val, use_undef = crit_info[1:]
            col = self.mLegend.getUnit(unit_name).getColumn()
            flt_rec_no_seq = []
            for rec_no in rec_no_seq:
                val = col.recordValue(self.mRecords[rec_no])
                if val is None:
                    if not use_undef:
                        continue
                elif lt_mode:
                    if val > the_val:
                        continue
                else:
                    if val < the_val:
                        continue
                flt_rec_no_seq.append(rec_no)
            return flt_rec_no_seq
        return rec_no_seq

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
