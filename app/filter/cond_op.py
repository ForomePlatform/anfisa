from .condition import ConditionMaker
#===============================================
class CondOpEnv:
    def __init__(self, cond_env, comp_data = None, cond_seq = None):
        self.mCondEnv = cond_env
        self.mCompData = (comp_data
            if comp_data is not None else dict())
        self.mCompChanged = False
        self.mOperativeUnitSeq = []
        self.mSeq = []
        self.mBadIdxs = []
        self.mCondSeq = cond_seq
        if cond_seq is not None:
            self.parseSeq(cond_seq)

    def getCondEnv(self):
        return self.mCondEnv

    def getCondSeq(self):
        return self.mCondSeq

    def getResult(self):
        return self.mCondEnv.joinAnd(self.mSeq)

    def report(self, ret_handle, with_comp = True):
        if with_comp and self.mCompChanged:
            ret_handle["compiled"] = self.mCompData
        if self.mBadIdxs:
            ret_handle["bad_idxs"] = self.mBadIdxs
        names = []
        for nm in self.mCondEnv.getOperativeNames():
            if nm not in self.mCompData:
                names.append(nm)
        if names:
            ret_handle["avail_import"] = names

    def getActiveOperativeUnits(self, instr_no = None):
        ret = []
        for unit_no, unit_h, cond_data in self.mOperativeUnitSeq:
            if instr_no is not None and instr_no < unit_no:
                break
            ret.append((unit_h, cond_data))
        return ret

    def parse(self, cond_data):
        return self.mCondEnv.parse(cond_data, self.mCompData)

    def importUnit(self, instr_no, unit_name,
            actual_cond_data, keep_actual = True):
        _, unit_h = self.mCondEnv.detectUnit(unit_name, "operational")
        assert unit_h is not None
        if unit_h.getName() in self.mCompData:
            unit_comp_data = self.mCompData[unit_h.getName()]
        else:
            unit_comp_data = unit_h.compile(actual_cond_data, keep_actual)
        self.mCompData[unit_h.getName()] = unit_comp_data
        self.mCompChanged = True
        self.mOperativeUnitSeq.append([instr_no, unit_h, unit_comp_data])
        return True

    def parseSeq(self, cond_seq):
        actual_cond_data = []
        for idx, cond_data in enumerate(cond_seq):
            try:
                if cond_data[0] == "import":
                    cond_data = self.importUnit(idx, cond_data[1],
                        ConditionMaker.joinAnd(actual_cond_data), False)
                else:
                    cond = self.parse(cond_data)
                    self.mSeq.append(cond)
                actual_cond_data.append(cond_data)
            except Exception:
                self.mBadIdxs.append(idx)

    def getCondAll(self):
        return self.mCondEnv.getCondAll()

    def getCondNone(self):
        return self.mCondEnv.getCondNone()
