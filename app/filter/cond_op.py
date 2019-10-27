from utils.log_err import logException
from .code_works import reprFilterCondition
#===============================================
class CondOpEnv:
    def __init__(self, cond_env, comp_data = None,
            cond_seq = None, name = None):
        self.mCondEnv = cond_env
        self.mCompData = (comp_data
            if comp_data is not None else dict())
        self.mName = name
        self.mCompChanged = False
        self.mOperativeUnitSeq = []
        self.mSeq = []
        self.mBadIdxs = []
        self.mCondSeq = cond_seq
        if cond_seq is not None:
            self.parseSeq(cond_seq)
        self.mResult = self.mCondEnv.joinAnd(self.mSeq)

    def getCondEnv(self):
        return self.mCondEnv

    def getCondSeq(self):
        return self.mCondSeq

    def getResult(self):
        return self.mResult

    def getName(self):
        return self.mName

    def report(self, ret_handle):
        #if self.mCompData:
        #    ret_handle["compiled"] = self.mCompData
        if self.mBadIdxs:
            ret_handle["bad-idxs"] = self.mBadIdxs
        names = []
        for op_unit in self.mCondEnv.iterOpUnits():
            if op_unit.getName() not in self.mCompData:
                names.append(op_unit.getName())
        if names:
            ret_handle["avail-import"] = names

    def getActiveOperativeUnits(self, instr_no = None):
        ret = []
        for unit_instr_no, unit_h, cond_data in self.mOperativeUnitSeq:
            if instr_no is None or instr_no >= unit_instr_no:
                ret.append((unit_h, cond_data))
        return ret

    def parse(self, cond_data):
        return self.mCondEnv.parse(cond_data, self.mCompData)

    def importUnit(self, instr_no, unit_name, actual_condition):
        _, unit_h = self.mCondEnv.detectUnit(unit_name, "operational")
        assert unit_h is not None
        if unit_h.getName() in self.mCompData:
            unit_comp_data = self.mCompData[unit_h.getName()]
        else:
            unit_comp_data = unit_h.prepareImport(actual_condition)
            self.mCompData[unit_h.getName()] = unit_comp_data
        self.mCompChanged = True
        self.mOperativeUnitSeq.append([instr_no, unit_h, unit_comp_data])
        return True

    def parseSeq(self, cond_seq):
        imp_op_units = set()
        for cond_data in cond_seq:
            if cond_data[0] == "import":
                imp_op_units.add(cond_data[1])
        for op_unit_name in (set(self.mCompData.keys()) - imp_op_units):
            del self.mCompData[op_unit_name]
        used_op_units = set()
        for idx, cond_data in enumerate(cond_seq):
            if cond_data[0] == "import":
                op_unit_name = cond_data[1]
                if op_unit_name in used_op_units:
                    self.mBadIdxs.append(idx)
                else:
                    self.importUnit(idx, op_unit_name,
                        self.mCondEnv.joinAnd(self.mSeq))
                    used_op_units.add(op_unit_name)
                continue
            try:
                cond = self.parse(cond_data)
                self.mSeq.append(cond)
            except Exception:
                logException("Bad instruction: %r, ds=%s" % 
                    (cond_data, self.mCondEnv.getDSName()))
                self.mBadIdxs.append(idx)

    def getPresentation(self):
        return [reprFilterCondition(instr) for instr in self.mCondSeq]

    def getCondAll(self):
        return self.mCondEnv.getCondAll()

    def getCondNone(self):
        return self.mCondEnv.getCondNone()
