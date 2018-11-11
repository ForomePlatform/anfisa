import json
from app.model.types import Types
#===============================================
class ValueTypeCounter:
    sMAX_BAD_COUNT = 3

    def __init__(self, name, is_seq = None,
            required_type = None, with_seq = True, state = "ok"):
        self.mName = name
        self.mState = state
        self.mCounts = [0] * 9
        self.mDetType = None
        if is_seq:
            self.mReqTypeStr = "list"
            if required_type:
                self.mReqTypeStr += "[%s]" % required_type
            self.mReqType = self.sTypes.index("list")
        else:
            self.mReqTypeStr = str(required_type)
            self.mReqType = self.sTypes.index(required_type)
        if with_seq:
            self.mSeqCounter = ValueTypeCounter(self.mName + "[]",
                False, required_type, False)
        else:
            self.mSeqCounter = None
        if self.mReqType > 0:
            self.mBadValues = []

    sTypes = [None, "null", "list", "dict", "empty", "link", "string",
        "int", "numeric"]
    # and "undef", "json"

    def getCount(self):
        return self.mCounts[0]

    def getName(self):
        return self.mName

    def getState(self):
        return self.mState

    def regValue(self, value):
        if value is None:
            return
        kind_idxs = Types._detectValTypes(value)
        if len(kind_idxs) == 1 and kind_idxs[0] == 2:
            if self.mSeqCounter is not None:
                for v in value:
                    self.mSeqCounter.regValue(v)
        self.mCounts[0] += 1
        for idx in kind_idxs:
            self.mCounts[idx] += 1
        if self.mReqType > 0 and self.mReqType not in kind_idxs:
            if len(self.mBadValues) < self.sMAX_BAD_COUNT:
                self.mBadValues.append(value)

    def _detectType(self):
        if self.mCounts[0] == 0:
            return "undef"
        for idx in range(1, 8):
            if self.mCounts[idx] == self.mCounts[0]:
               return self.sTypes[idx]
        return "json"

    def detectType(self):
        if self.mDetType is None:
            self.mDetType = self._detectType()
        return self.mDetType

    def getBadValues(self):
        return self.mBadValues

    def repJSon(self):
        tp = self.detectType()
        count = str(self.mCounts[0])
        if tp == "list":
            sub_tp = self.mSeqCounter.detectType()
            tp = "list(%s)" % sub_tp
            count = str(self.mSeqCounter.getCount()) + '/' + count
        ret = {"tp": tp, "state": self.mState,
            "counts": count, "req": self.mReqTypeStr}
        if self.mReqType > 0 and len(self.mBadValues) > 0:
            seq = []
            for bad_val in self.mBadValues:
                v_rep = json.dumps(bad_val)
                if len(v_rep) > 15:
                    v_rep = v_rep[:12] + '...'
                seq.append(v_rep)
            ret["bad_samples"] = ', '.join(seq)
        return ret

    def report(self, output, rep_level):
        if rep_level < 2 and self.mName.startswith('_'):
            return
        rep = self.repJSon()
        ret = ["[%s]" % rep["state"], self.mName,
            rep["counts"], rep["tp"], rep["req"]]
        if "bad_samples" in rep:
            ret.append("BAD: " + rep["bad_samples"])
        print >> output, "\t".join(ret)

#===============================================
