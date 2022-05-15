#  Copyright (c) 2019. Partners HealthCare and other members of
#  Forome Association
#
#  Developed by Sergey Trifonov based on contributions by Joel Krier,
#  Michael Bouzinier, Shamil Sunyaev and other members of Division of
#  Genetics, Brigham and Women's Hospital
#
#  Licensed under the Apache License, Version 2.0 (the "License");
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
#
#        http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.
#

import re, sys, logging
from collections import Counter

from app.config.a_config import AnfisaConfig
from forome_tools.path_works import AttrFuncPool
#===============================================
class TransformPreparator_WS:
    def __init__(self, flt_schema, sol_broker, hard_check):
        self.mHardCheck = hard_check
        self.mConvertors = []
        self.mTotalItemCount = 0
        self.mTransPathBaseF = AttrFuncPool.makeFunc(
            AnfisaConfig.configOption("transcript.path.base"))
        self.mUnitStatSeq = []
        panels_convertors = []
        for unit_descr in flt_schema:
            kind, sub_kind = unit_descr["kind"], unit_descr["sub-kind"]
            if kind == "numeric":
                if sub_kind.startswith("transcript-"):
                    self.mConvertors.append(TrNumConvertor(unit_descr))
                else:
                    self.mUnitStatSeq.append(NumUnitStatH(unit_descr))
            elif kind == "enum":
                if sub_kind in ("transcript-status", "transcript-variety"):
                    self.mConvertors.append(
                        TrStatusConvertor(unit_descr))
                elif sub_kind == "transcript-multiset":
                    self.mConvertors.append(
                        TrMultisetConvertor(unit_descr))
                elif sub_kind == "transcript-panels":
                    panels_convertors.append(
                        TrPanelsConvertor(sol_broker, unit_descr))
                else:
                    self.mUnitStatSeq.append(EnumUnitStatH(unit_descr))
            else:
                assert False, "Bad unit kind:" + unit_descr["kind"]
        self.mConvertors += panels_convertors

    def isEmpty(self):
        return len(self.mConvertors) == 0 and len(self.mUnitStatSeq) == 0

    def doRec(self, rec_no, rec_data, flt_data, pre_data):
        tr_seq_seq = self.mTransPathBaseF(rec_data)
        assert len(tr_seq_seq) <= 1
        if len(tr_seq_seq) == 1:
            tr_seq = tr_seq_seq[0]
        else:
            tr_seq = []
        for conv_h in self.mConvertors:
            conv_h.doRec(tr_seq, flt_data)
        for stat_h in self.mUnitStatSeq:
            stat_h.doRec(flt_data)
        flt_data["$1"] = len(tr_seq)
        self.mTotalItemCount += len(tr_seq)

    def finishUp(self):
        is_ok = True
        for conv_h in self.mConvertors:
            is_ok &= conv_h.finishUp(self.mHardCheck)
        assert is_ok
        for stat_h in self.mUnitStatSeq:
            stat_h.finishUp()
        return self.mTotalItemCount

#===============================================
class TrNumConvertor:
    sPattVar = re.compile(r'^\$\{(\w+)\}$')

    def __init__(self, unit_descr):
        self.mDescr = unit_descr
        self.mName = unit_descr["name"]
        self.mTransName = unit_descr["tr-name"]
        self.mDefaultValue = unit_descr["default"]
        self.mMin, self.mMax = None, None
        self.mCntDef = 0

    def doRec(self, tr_seq, f_data):
        if len(tr_seq) == 0:
            return
        res = []
        for tr_obj in tr_seq:
            val = tr_obj.get(self.mTransName)
            if val is None:
                val = self.mDefaultValue
            self.mCntDef += 1
            if self.mCntDef == 1:
                self.mMin = self.mMax = val
            else:
                if val < self.mMin:
                    self.mMin = val
                elif val > self.mMax:
                    self.mMax = val
            res.append(val)
        f_data[self.mName] = res

    def isTranscriptID(self):
        return False

    def finishUp(self, hard_check):
        self.mDescr["min"] = self.mMin
        self.mDescr["max"] = self.mMax
        self.mDescr["def"] = self.mCntDef
        self.mDescr["undef"] = 0
        return True

#===============================================
class TrEnumConvertor:
    sPattVar = re.compile(r'^\$\{(\w+)\}$')

    def __init__(self, unit_descr):
        self.mDescr = unit_descr
        self.mName = unit_descr["name"]
        self.mTransName = unit_descr["tr-name"]
        self.mDefaultValue = unit_descr.get("default")
        self.mPreVariants = unit_descr["pre-variants"]
        self.mVarCount = Counter()
        self.mBadCount = Counter()
        self.mPreVarSet = None
        if self.mPreVariants is not None:
            self.mPreVarSet = set(self.mPreVariants)

    def _checkBooleanVariants(self):
        if self.mPreVariants is None:
            self.mPreVariants = ["True", "False"]
            self.mPreVarSet = set(self.mPreVariants)

    def isTranscriptID(self):
        return False

    def finishUp(self, hard_check):
        if len(self.mBadCount) > 0:
            err_msg = ("Form transcript field %s with wrong values %s" %
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
        else:
            if self.mDefaultValue in self.mVarCount:
                default_count = self.mVarCount[self.mDefaultValue]
                del self.mVarCount[self.mDefaultValue]
            else:
                default_count = 0
        for var in sorted(set(self.mVarCount.keys()) - used_variants):
            variants.append([var, self.mVarCount[var]])
        if default_count is not None:
            variants.append([self.mDefaultValue, default_count])
        self.mDescr["variants"] = variants
        return True

#===============================================
class TrStatusConvertor(TrEnumConvertor):
    sPattVar = re.compile(r'^\$\{(\w+)\}$')

    def __init__(self, unit_descr):
        TrEnumConvertor.__init__(self, unit_descr)
        self.mBoolCheckValue = unit_descr["bool-check"]
        self.mBoolVUnit = None
        if self.mBoolCheckValue:
            self._checkBooleanVariants()
        if (self.mBoolCheckValue is not None
                and '$' in self.mBoolCheckValue):
            q = self.sPattVar.match(self.mBoolCheckValue)
            assert q is not None, (
                "Bad transcript instruction " + self.mBoolCheckValue)
            self.mBoolVUnit = q.group(1)
        self.mIdMode = unit_descr.get("tr-id-mode")

    def isTranscriptID(self):
        return self.mIdMode

    def doRec(self, tr_seq, f_data):
        if len(tr_seq) == 0:
            self.mVarCount[self.mDefaultValue] += 1
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
                    assert len(val) == 1, (
                        "Tr-Unit " + self.mName + " val= " + repr(val))
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
class TrMultisetConvertor(TrEnumConvertor):
    sPattVar = re.compile(r'^\$\{(\w+)\}$')

    def __init__(self, unit_descr):
        TrEnumConvertor.__init__(self, unit_descr)

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

#===============================================
class TrPanelsConvertor:
    def __init__(self, sol_broker, unit_descr):
        self.mDescr = unit_descr
        self.mName = unit_descr["name"]
        self.mBaseName = unit_descr["panel-base"]
        self.mPanelType = unit_descr["panel-type"]
        self.mViewName = unit_descr.get("view-name")
        self.mPanelSets = {pname: set(names)
            for pname, names in sol_broker.iterPanels(self.mPanelType)}
        self.mVarCount = Counter()

    def isTranscriptID(self):
        return False

    def doRec(self, tr_seq, f_data):
        res = []
        for tr_obj in tr_seq:
            res_val = []
            item = tr_obj.get(self.mBaseName)
            if item:
                for pname, pset in self.mPanelSets.items():
                    if item in pset:
                        res_val.append(pname)
                        self.mVarCount[pname] += 1
                res_val.sort()
            res.append(res_val)
            if self.mViewName:
                tr_obj[self.mViewName] = res_val
        f_data[self.mName] = res

    def finishUp(self, hard_check):
        variants = []
        for var in sorted(self.mVarCount.keys()):
            variants.append([var, self.mVarCount[var]])
        self.mDescr["variants"] = variants
        return True

#===============================================
#===============================================
class NumUnitStatH:
    def __init__(self, unit_descr):
        self.mDescr = unit_descr
        self.mName = unit_descr["name"]
        self.mMin, self.mMax = None, None
        self.mCntDef = 0
        self.mCntUndef = 0

    def doRec(self, f_data):
        val = f_data.get(self.mName)
        if val is None:
            self.mCntUndef += 1
            return
        self.mCntDef += 1
        if self.mCntDef == 1:
            self.mMin = self.mMax = val
        else:
            if val < self.mMin:
                self.mMin = val
            elif val > self.mMax:
                self.mMax = val

    def finishUp(self):
        self.mDescr["min"] = self.mMin
        self.mDescr["max"] = self.mMax
        self.mDescr["def"] = self.mCntDef
        self.mDescr["undef"] = self.mCntUndef

#===============================================
class EnumUnitStatH:
    def __init__(self, unit_descr):
        self.mDescr = unit_descr
        self.mName = unit_descr["name"]
        self.mAtomicMode = (unit_descr["sub-kind"] == "status")
        self.mCounts = Counter()

    def doRec(self, f_data):
        val = f_data.get(self.mName)
        if self.mAtomicMode:
            self.mCounts[val] += 1
        elif val:
            for name in val:
                self.mCounts[name] += 1

    def finishUp(self):
        variants = []
        for info in self.mDescr["variants"]:
            name = info[0]
            cnt = self.mCounts[name]
            if cnt > 0:
                rec = info[:]
                rec[1] = cnt
                variants.append(rec)
        self.mDescr["variants"] = variants

#===============================================
class TransformPreparator_XL:
    def __init__(self, druid_adm):
        self.mDruidAdm = druid_adm
        self.mTotalItemCount = 0

    def isEmpty(self):
        return False

    def doRec(self, rec_no, rec_data, flt_data, pre_data):
        self.mTotalItemCount += 1
        flt_data.update(self.mDruidAdm.internalFltData(rec_no, pre_data))

    def finishUp(self):
        return self.mTotalItemCount
