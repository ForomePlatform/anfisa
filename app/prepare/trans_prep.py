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
        self.mTransPathBaseF = AttrFuncPool.makeFunc(
            AnfisaConfig.configOption("transcript.path.base"))
        for unit_descr in flt_schema:
            if not unit_descr["kind"].startswith("transcript-"):
                continue
            if unit_descr["kind"] == "transcript-status":
                self.mConvertors.append(TrStatusConvertor(unit_descr))
            elif unit_descr["kind"] == "transcript-multiset":
                self.mConvertors.append(TrMultisetConvertor(unit_descr))
            else:
                assert False, "Bad kind:" + unit_descr["kind"]

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
class TrConvertor:
    sPattVar = re.compile('^\$\{(\w+)\}$')

    def __init__(self, unit_descr):
        self.mDescr = unit_descr
        self.mName = unit_descr["name"]
        self.mTransName = unit_descr["tr_name"]
        self.mDefaultValue = unit_descr.get("default")
        self.mPreVariants = unit_descr["pre_variants"]
        self.mVarCount = Counter()
        self.mBadCount = Counter()
        self.mPreVarSet = None
        if self.mPreVariants is not None:
            self.mPreVarSet = set(self.mPreVariants)

    def _checkBooleanVariants(self):
        if self.mPreVariants is None:
            self.mPreVariants = ["True", "False"]
            self.mPreVarSet = set(self.mPreVariants)

    def finishUp(self, hard_check):
        if len(self.mBadCount) > 0:
            err_msg =("Form transcript field %s with wrong values %s" %
                    (self.mName, repr(self.mBadCount)))
            if hard_check:
                print(err_msg, file = sys.stderr)
                return False
            logging.error(err_msg)
        variants = []
        default_count = None
        used_variants = set()
        if self.mPreVariants is not None:
            for var in self.mPreVariants:
                if var in self.mVarCount:
                    variants.append([var, self.mVarCount[var]])
            used_variants = set(self.mPreVariants)
        elif self.mDefaultValue in self.mVarCount:
            default_count = self.mVarCount[self.mDefaultValue]
            del self.mVarCount[self.mDefaultValue]
        for var in sorted(set(self.mVarCount.keys()) - used_variants):
            variants.append([var, self.mVarCount[var]])
        if default_count is not None:
            variants.append([self.mDefaultValue, default_count])
        self.mDescr["variants"] = variants
        return True

#===============================================
class TrStatusConvertor(TrConvertor):
    sPattVar = re.compile('^\$\{(\w+)\}$')

    def __init__(self, unit_descr):
        TrConvertor.__init__(self, unit_descr)
        self.mBoolCheckValue =  unit_descr["bool_check"]
        self.mBoolVUnit = None
        if self.mBoolCheckValue:
            self._checkBooleanVariants()
        if (self.mBoolCheckValue is not None and
                '$' in self.mBoolCheckValue):
            q = self.sPattVar.match(self.mBoolCheckValue)
            assert q is not None, (
                "Bad transcript instruction " + self.mBoolCheckValue)
            self.mBoolVUnit = q.group(1)

    def doRec(self, tr_seq, f_data):
        if len(tr_seq) == 0:
            return

        if self.mBoolVUnit is None:
            bool_check_value = self.mBoolCheckValue
        else:
            bool_check_value = f_data.get(self.mBoolVUnit)

        res = []
        for tr_obj in tr_seq:
            val = tr_obj.get(self.mTransName)
            if isinstance(val, list):
                if bool_check_value is not None:
                    val = "True" if bool_check_value in val else "False"
                else:
                    assert len(val) == 1, "Tr-Unit %s val=%r" % (
                        self.mName, val)
                    val = val[0]
            else:
                val = str(val)
                if bool_check_value is not None:
                    val = "True" if bool_check_value in val else "False"

            if self.mPreVarSet is not None and val not in self.mPreVarSet:
                self.mBadCount[val] += 1
                val = self.mDefaultValue
            self.mVarCount[val] += 1
            res.append(val)
        if len(res) == 0:
            self.mVarCount[self.mDefaultValue] += 1
        f_data[self.mName] = res

#===============================================
class TrMultisetConvertor(TrConvertor):
    sPattVar = re.compile('^\$\{(\w+)\}$')

    def __init__(self, unit_descr):
        TrConvertor.__init__(self, unit_descr)

    def doRec(self, tr_seq, f_data):
        if len(tr_seq) == 0:
            return
        res = []
        for tr_obj in tr_seq:
            values = tr_obj.get(self.mTransName)
            if not values:
                values = []
            if self.mPreVarSet is not None:
                res_values = set()
                for val in values:
                    if val in self.mPreVarSet:
                        res_values.add(val)
                    else:
                        self.mBadCount[val] += 1
                        res_values.add(self.mDefaultValue)
                res_values = sorted(res_values)
            else:
                res_values = sorted(set(values))
            for val in res_values:
                self.mVarCount[val] += 1
            res.append(res_values)
        f_data[self.mName] = res
