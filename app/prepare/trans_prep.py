import re, sys, logging
from collections import Counter

from app.config.a_config import AnfisaConfig
from utils.path_works import AttrFuncPool
#===============================================
class TranscriptPreparator:
    def __init__(self, flt_schema, hard_check):
        self.mHardCheck = hard_check
        self.mConvertors = []
        self.mTotalItemCount = 0
        for unit_descr in flt_schema:
            if not unit_descr["kind"].startswith("transcript-"):
                continue
            if unit_descr["kind"] == "transcript-status":
                self.mConvertors.append(TrStatusConvertor(unit_descr))
            else:
                assert False
        self.mTransPathBaseF = None
        if len(self.mConvertors) > 0:
            self.mTransPathBaseF = AttrFuncPool.makeFunc(
                AnfisaConfig.configOption("transcript.path.base"))

    def isEmpty(self):
        return len(self.mConvertors) == 0

    def doRec(self, rec_data, flt_data):
        tr_seq_seq = self.mTransPathBaseF(rec_data)
        assert len(tr_seq_seq) <= 1
        if len(tr_seq_seq) == 1:
            tr_seq = tr_seq_seq[0]
        else:
            tr_seq = []
        for conv_h in self.mConvertors:
            conv_h.doRec(tr_seq, flt_data)
        flt_data["$1"] = len(tr_seq)
        self.mTotalItemCount += len(tr_seq)

    def finishUp(self):
        is_ok = True
        for conv_h in self.mConvertors:
            is_ok &= conv_h.finishUp(self.mHardCheck)
        assert is_ok
        return self.mTotalItemCount

#===============================================
class TrStatusConvertor:
    sPattVar = re.compile('^\$\{(\w+)\}$')

    def __init__(self, unit_descr):
        self.mDescr = unit_descr
        self.mName = unit_descr["name"]
        self.mTransName = unit_descr["tr_name"]
        self.mDefaultValue = unit_descr["default"]
        self.mPreVariants = unit_descr["pre_variants"]
        self.mMapping =  unit_descr["mapping"]
        self.mMapComp = None
        self.mVarCount = Counter()
        self.mBadCount = Counter()
        self.mPreVarSet = None
        if self.mPreVariants is not None:
            self.mPreVarSet = set(self.mPreVariants)
        if (self.mMapping is not None and
                any([isinstance(key, str) and '$' in key
                for key in self.mMapping.keys()])):
            self.mMapComp = []
            for key, value in self.mMapping.items():
                if isinstance(key, str):
                    q = self.sPattVar.match(key)
                    if q is not None:
                        self.mMapComp.append((None, q.group(1), value))
                        continue
                    assert '$' not in key, "Bad transcript instruction " + key
                self.mMapComp.append((key, None, value))

    def doRec(self, tr_seq, f_data):
        if len(tr_seq) == 0:
            return

        if self.mMapComp is not None:
            mapping = dict()
            for key, var, value in self.mMapComp:
                if var is not None:
                    mapping[f_data[var]] = value
                else:
                    mapping[key] = value
        else:
            mapping = self.mMapping
        res = []
        for tr_obj in tr_seq:
            val = tr_obj.get(self.mTransName)
            if isinstance(val, list):
                #assert len(val) == 1, (self.mName +
                #    ": expected single elem array: " + repr(val))
                val = val[0]
            if mapping is not None:
                val = mapping.get(val, self.mDefaultValue)
            elif val is None:
                val = self.mDefaultValue
            val = str(val)
            if self.mPreVarSet is not None and val not in self.mPreVarSet:
                self.mBadCount[val] += 1
                val = self.mDefaultValue
            self.mVarCount[val] += 1
            res.append(val)
        f_data[self.mName] = res

    def finishUp(self, hard_check):
        if len(self.mBadCount) > 0:
            err_msg =("Form transcript field %s with wrong values %s" %
                    (self.mName, repr(self.mBadCount)))
            if hard_check:
                print(err_msg, file = sys.stderr)
                return False
            logging.error(err_msg)
        variants = []
        used_variants = set()
        if self.mPreVariants is not None:
            for var in self.mPreVariants:
                if var in self.mVarCount:
                    variants.append([var, self.mVarCount[var]])
            used_variants = set(self.mPreVariants)
        for var in sorted(set(self.mVarCount.keys()) - used_variants):
            variants.append([var, self.mVarCount[var]])
        self.mDescr["variants"] = variants
        return True
