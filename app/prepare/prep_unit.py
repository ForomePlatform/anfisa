#  Copyright (c) 2019. Partners HealthCare and other mnembers of
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

import abc
import re
import logging
from collections import Counter

from app.config.flt_conv import makeFilterConversion
from forome_tools.path_works import AttrFuncPool
#===============================================
class ValueConvertor:
    sMAX_BAD_COUNT = 3

    def __init__(self, master, name, unit_no, vgroup, dim_name):
        self.mMaster = master
        self.mName = name
        self.mVGroup = vgroup
        self.mUnitNo = unit_no
        self.mDimName = dim_name
        self.mErrorCount = 0
        self.mErrors = []
        if self.mVGroup is not None:
            self.mVGroup.addUnit(self)

    def getName(self):
        return self.mName

    def getErrorCount(self):
        return self.mErrorCount

    def regError(self, rec_no, values):
        self.mErrorCount += 1
        if len(self.mErrors) < self.sMAX_BAD_COUNT:
            self.mErrors.append([rec_no, values])

    def getTranscriptName(self):
        return None

    def getMaster(self):
        return self.mMaster

    def isTranscriptID(self):
        return False

    def dump(self):
        result = {
            "name": self.mName,
            "no": self.mUnitNo}
        if self.mVGroup is not None:
            result["vgroup"] = self.mVGroup.getTitle()
        if self.mDimName is not None:
            result["dim-name"] = self.mDimName
        if self.mErrorCount > 0:
            result["errors"] = [self.mErrorCount, self.mErrors]
        return result

    @classmethod
    def registerConvertorType(cls, kind, sub_kind, conv_class):
        key = (kind, sub_kind)
        assert key not in cls.sConvertors, (
            "Convertor type duplication: " + key)
        cls.sConvertors[key] = conv_class

#===============================================
class PathValueConvertor(ValueConvertor):
    sMAX_BAD_COUNT = 3

    def __init__(self, master, name, vpath, unit_no, vgroup, dim_name):
        ValueConvertor.__init__(self, master, name, unit_no, vgroup, dim_name)
        self.mPath = vpath
        self.mPathF = AttrFuncPool.makeFunc(self.mPath)

    @abc.abstractmethod
    def convert(self, values, rec_no):
        return None

    def process(self, rec_no, rec_data, result):
        val = self.convert(self.mPathF(rec_data), rec_no)
        if val is not None:
            result[self.getName()] = val

    def dump(self):
        ret = ValueConvertor.dump(self)
        ret["path"] = self.mPath
        return ret

#===============================================
class _NumericStatCollector:
    def __init__(self, default_value, diap, calm_mode):
        self.mDefaultValue = default_value
        if diap is not None:
            self.mMinBound, self.mMaxBound = diap
        else:
            self.mMinBound = None
        self.mMinValue, self.mMaxValue = None, None
        self.mCntDef = 0
        self.mCntUndef = 0
        self.mCalmMode = calm_mode

    def getDefault(self):
        return self.mDefaultValue

    def _checkConvVal(self, msg, val):
        conv_val = self.convType(val)
        assert val == conv_val, (
            f"Missing value for {self.getName()}/{msg}: {val}/{conv_val}")

    def checkDiap(self):
        if self.mDefaultValue is not None:
            self._checkConvVal("default", self.mDefaultValue)
        if self.mMinBound is not None:
            self._checkConvVal("min", self.mMinBound)
            self._checkConvVal("max", self.mMaxBound)
            if self.mDefaultValue is not None:
                assert (self.mMinBound <= self.mDefaultValue
                        <= self.mMaxBound), (
                    f"Default/bound conflict for {self.getName()}: "
                    f"{self.mMinBound} <= {self.mDefaultValue} "
                    f"<= {self.mMaxBound}")

    def regVal(self, val):
        if val is None:
            val = self.mDefaultValue
        else:
            val = self.convType(val)
        if val is None:
            self.mCntUndef += 1
            return None
        if (self.mMinBound is None
                or self.mMinBound <= val <= self.mMaxBound):
            self.mCntDef += 1
            if self.mMinValue is None or val < self.mMinValue:
                self.mMinValue = val
            if self.mMaxValue is None or val > self.mMaxValue:
                self.mMaxValue = val
            return val
        return False

    def regErrVal(self):
        if self.mDefaultValue is not None:
            self.mCntDef += 1
        else:
            self.mCntUndef += 1
        return self.mDefaultValue

    def statResult(self):
        ret = {
            "kind": "numeric",
            "default": self.mDefaultValue}
        if not self.mCalmMode:
            ret["def"] = self.mCntDef
            ret["undef"] = self.mCntUndef
            ret["min"] = self.mMinValue
            ret["max"] = self.mMaxValue
        if self.mMinBound is not None:
            ret["diap"] = [self.mMinBound, self.mMaxBound]
        return ret

#===============================================
class _NumericConvertor(PathValueConvertor, _NumericStatCollector):
    def __init__(self, master, name, vpath, unit_no, vgroup,
            default_value, diap, conversion):
        PathValueConvertor.__init__(self,
            master, name, vpath, unit_no, vgroup, None)
        _NumericStatCollector.__init__(self, default_value, diap, False)
        assert default_value is not None, (
            f"For {name} numeric unit: no default value")
        self.mConversion = conversion
        self.mConvFunc = makeFilterConversion(conversion, self.getMaster())

    def checkSetup(self):
        self.checkDiap()

    def convert(self, values, rec_no):
        try:
            if self.mConvFunc is not None and len(values) == 1:
                values = [self.mConvFunc(values[0])]
            if len(values) == 0:
                values = [None]
            if len(values) == 1:
                val = self.regVal(values[0])
                if val is not False:
                    return val
        except Exception:
            pass

        val = self.regErrVal()
        self.regError(rec_no, values)
        return val

    def dump(self):
        ret = PathValueConvertor.dump(self)
        ret.update(self.statResult())
        if self.mConversion is not None:
            ret["conversion"] = self.mConversion
        return ret

#===============================================
class FloatConvertor(_NumericConvertor):
    def __init__(self, master, name, vpath, unit_no, vgroup,
            default_value, diap, conversion):
        _NumericConvertor.__init__(self,
            master, name, vpath, unit_no, vgroup,
            default_value, diap, conversion)
        self.checkSetup()

    @staticmethod
    def convType(val):
        return float(val)

    def dump(self):
        ret = _NumericConvertor.dump(self)
        ret["sub-kind"] = "float"
        return ret

#===============================================
class IntConvertor(_NumericConvertor):
    def __init__(self, master, name, vpath, unit_no, vgroup,
            default_value, diap, conversion):
        _NumericConvertor.__init__(self,
            master, name, vpath, unit_no, vgroup,
            default_value, diap, conversion)
        self.checkSetup()

    @staticmethod
    def convType(val):
        return int(val)

    def dump(self):
        ret = _NumericConvertor.dump(self)
        ret["sub-kind"] = "int"
        return ret

#===============================================
#===============================================
class _EnumStatCollector:
    def __init__(self, default_value, pre_variants, calm_mode):
        self.mVarCount = Counter()
        self.mCntUndef = 0
        self.mDefaultValue = default_value
        self.mPreVariants = pre_variants
        self.mVariants = None
        self.mCalmMode = calm_mode
        if self.mPreVariants is not None:
            self.mVariants = set(pre_variants)
            if self.mDefaultValue is not None:
                assert self.mDefaultValue in self.mVariants, (
                    "For " + self.getName() + " default "
                    + str(self.mDefaultValue)
                    + "is not in preset variants:")
            for var in pre_variants:
                assert isinstance(var, str), (
                    "For " + self.getName()
                    + " variant value is not str: " + repr(var))
        if self.mDefaultValue is not None:
            assert isinstance(self.mDefaultValue, str), (
                "For " + self.getName()
                + " default value is not str: " + repr(self.mDefaultValue))

    def getDefault(self):
        return self.mDefaultValue

    def regVal(self, val):
        if (self.mVariants is not None
                and val not in self.mVariants):
            return False
        self.mVarCount[val] += 1
        return val

    def regErrVal(self):
        if self.mDefaultValue is None:
            self.mCntUndef += 1
        else:
            self.mVarCount[self.mDefaultValue] += 1
        return self.mDefaultValue

    def statResult(self):
        ret = {
            "kind": "enum",
            "default": self.mDefaultValue,
            "undef": self.mCntUndef}
        if self.mPreVariants is not None:
            ret["pre-variants"] = self.mPreVariants
        if self.mCalmMode:
            return ret
        variants = []
        if self.mPreVariants:
            for var in self.mPreVariants:
                variants.append([var, self.mVarCount[var]])
            used_variants = set(self.mPreVariants)
        else:
            used_variants = {self.mDefaultValue}
        for var in sorted(set(self.mVarCount.keys()) - used_variants):
            variants.append([var, self.mVarCount[var]])
        if not self.mPreVariants and self.mDefaultValue is not None:
            variants.append([self.mDefaultValue,
                             self.mVarCount[self.mDefaultValue]])
        ret["variants"] = variants
        return ret

#===============================================
class EnumConvertor(PathValueConvertor, _EnumStatCollector):
    def __init__(self, master, name, vpath, unit_no, vgroup, dim_name,
            sub_kind, variants = None, value_map = None, conversion = None,
            default_value = None, compact_mode = False,  separators = None):
        PathValueConvertor.__init__(self, master, name, vpath,
            unit_no, vgroup, dim_name)
        _EnumStatCollector.__init__(self, default_value, variants, False)
        self.mSubKind = sub_kind
        self.mValueMap = value_map
        self.mSeparators = separators
        if self.mSeparators:
            self.mSepPatt = re.compile(self.mSeparators)
        self.mCompactMode = compact_mode
        self.mConversion = conversion
        self.mConvFunc = makeFilterConversion(conversion, self.getMaster())
        assert sub_kind in {"status", "multi"}, "Missed sub_kind:" + sub_kind
        self.mDefaultRet = self.getDefault()
        if self.mSubKind != "status" and self.mDefaultRet is not None:
            self.mDefaultRet = [self.mDefaultRet]

    def convert(self, values, rec_no):
        ret = []
        try:
            mod_values = values
            if self.mConvFunc is not None:
                mod_values = self.mConvFunc(values)
            if self.mSeparators:
                mod_values = []
                for val in values:
                    for v in re.split(self.mSepPatt, val):
                        if v:
                            mod_values.append(v)
            is_ok = True
            mod_values = map(str, mod_values)
            if self.mValueMap is not None:
                mod_values = list(mod_values)
                for idx, variant in enumerate(mod_values):
                    if variant in self.mValueMap:
                        mod_values[idx] = self.mValueMap[variant]

            for val in set(mod_values):
                if self.regVal(val):
                    ret.append(val)
                else:
                    is_ok = False
        except Exception:
            is_ok = False
        if self.mSubKind == "status" and len(ret) > 1:
            is_ok = False
        if not is_ok:
            self.regError(rec_no, values)
        if len(ret) == 0:
            self.regErrVal()
            return self.mDefaultRet
        if self.mSubKind == "status":
            return ret[0]
        return ret

    def dump(self):
        ret = PathValueConvertor.dump(self)
        ret.update(self.statResult())
        ret["sub-kind"] = self.mSubKind
        ret["compact"] = self.mCompactMode
        if self.mValueMap:
            ret["value-map"] = self.mValueMap
        if self.mConversion:
            ret["conversion"] = self.mConversion
        if self.mSeparators:
            ret["separators"] = self.mSeparators
        return ret

#===============================================
class VarietyConvertor(EnumConvertor):
    def __init__(self, master, name, unit_no, vgroup,
            variety_name, panel_name, vpath, panel_type, separator='|'):
        EnumConvertor.__init__(self, master, name, vpath,
            unit_no, vgroup, None, "status")
        self.mVarietyName = variety_name
        self.mPanelName = panel_name
        self.mPanelType = panel_type
        self.mSeparator = separator

    def convert(self, values, rec_no):
        try:
            value = self.mSeparator.join(sorted(map(str, values)))
            self.regVal(value)
            return value
        except Exception:
            self.regErrVal()
            self.regError(rec_no, values)
        return None

    def dump(self):
        ret = EnumConvertor.dump(self)
        ret["mean"] = "pre-variety"
        ret["variety-name"] = self.mVarietyName
        ret["panel-name"] = self.mPanelName
        ret["panel-type"] = self.mPanelType
        ret["separator"] = self.mSeparator
        return ret

#===============================================
class PresenceConvertor(ValueConvertor):
    def __init__(self, master, name, unit_no, vgroup, path_info_seq):
        ValueConvertor.__init__(self, master, name, unit_no, vgroup, None)
        self.mPathInfoSeq = path_info_seq
        self.mPathFunctions = [(it_name, AttrFuncPool.makeFunc(it_path))
            for it_name, it_path in self.mPathInfoSeq]
        self.mVarCount = Counter()

    def process(self, rec_no, rec_data, result):
        res_val = []
        is_ok = True
        for var, path_f in self.mPathFunctions:
            values = path_f(rec_data)
            try:
                if values and len(values) > 0 and values[0]:
                    res_val.append(var)
                    self.mVarCount[var] += 1
            except Exception:
                if is_ok:
                    self.regError(rec_no, [var, values])
                is_ok = False
        if res_val is not None:
            result[self.getName()] = res_val

    def dump(self):
        ret = ValueConvertor.dump(self)
        ret["kind"] = "enum"
        ret["sub-kind"] = "multi"
        ret["mean"] = "presence"
        variants = []
        for var, it_path in self.mPathInfoSeq:
            variants.append([var, self.mVarCount[var], it_path])
        ret["variants"] = variants
        return ret

#===============================================
class PanelConvertor(ValueConvertor):
    def __init__(self, master, name, unit_no, vgroup, dim_name,
            base_unit_name, panel_type, view_path):
        ValueConvertor.__init__(self, master, name, unit_no, vgroup, dim_name)
        self.mBaseUnitName = base_unit_name
        self.mPanelType = panel_type
        p_key = "panel." + panel_type
        self.mPanelSets = {p_it["name"]: p_it["data"]
            for p_it in self.getMaster().iterStdItems(p_key)}
        assert len(self.mPanelSets) > 0, (
            "No data for panel type " + panel_type)
        self.mCntUndef = 0
        self.mVarCount = Counter()
        self.mViewPath = view_path
        self.mViewPathSeq = None
        if self.mViewPath is not None:
            assert self.mViewPath.startswith('/'), (
                "No leading / in view path: " + self.mViewPath)
            self.mViewPathSeq = self.mViewPath.split('/')[1:]

    def process(self, rec_no, rec_data, result):
        pitems = result.get(self.mBaseUnitName)
        res_val = []
        if pitems:
            pitems = set(pitems)
            for pname, pset in self.mPanelSets.items():
                if len(pitems & set(pset)) > 0:
                    res_val.append(pname)
                    self.mVarCount[pname] += 1
            if res_val:
                res_val.sort()
                if self.mViewPathSeq is not None:
                    data = rec_data
                    for nm in self.mViewPathSeq[:-1]:
                        data = data[nm]
                    data[self.mViewPathSeq[-1]] = res_val
        result[self.getName()] = res_val

    def dump(self):
        ret = ValueConvertor.dump(self)
        ret["kind"] = "enum"
        ret["sub-kind"] = "multi"
        ret["default"] = None
        ret["mean"] = "panel"
        ret["panel-base"] = self.mBaseUnitName
        ret["panel-type"] = self.mPanelType
        ret["undef"] = self.mCntUndef
        if self.mViewPath is not None:
            ret["view-path"] = self.mViewPath
        variants = []
        for var in sorted(self.mVarCount.keys()):
            variants.append([var, self.mVarCount[var]])
        ret["variants"] = variants
        return ret

#===============================================
class TranscriptNumConvertor(ValueConvertor, _NumericStatCollector):
    def __init__(self, master, name, unit_no, vgroup,
            sub_kind, trans_name, default_value):
        ValueConvertor.__init__(self, master, name, unit_no, vgroup, None)
        _NumericStatCollector.__init__(self, default_value, None,
            self.getMaster().getDSKind() != "ws")
        prefix, _, postfix = sub_kind.partition('-')
        assert prefix == "transcript" and postfix in ("int", "float"), (
            f"Unexpected prefix/postfix: {prefix}/{postfix}")
        self.mSubKind = sub_kind
        self.mConvF = int if postfix == "int" else float
        self.mTransName = trans_name
        self.mIsOK = True

    def getTranscriptName(self):
        return self.mTransName

    def convType(self, val):
        return self.mConvF(val)

    def process(self, rec_no, rec_data, result):
        assert False

    def isOK(self):
        return self.mIsOK

    def regError(self, value):
        if self.mIsOK:
            logging.error(
                f"For numeric tr-unit {self.getName()} bad value: {value}")
            self.mIsOK = False
        return self.regErrVal()

    def processOne(self, value):
        val = self.regVal(value)
        if val is False:
            return self.regError(value)
        return val

    def processEmpty(self):
        pass

    def dump(self):
        ret = ValueConvertor.dump(self)
        ret.update(self.statResult())
        ret["sub-kind"] = self.mSubKind
        ret["tr-name"] = self.mTransName
        return ret

#===============================================
class _TranscriptEnumConvertor(ValueConvertor, _EnumStatCollector):
    def __init__(self, master, name, unit_no, vgroup, dim_name,
            sub_kind, trans_name, variants, default_value,
            bool_check_value=None, transcript_id_mode=False):
        ValueConvertor.__init__(self, master, name, unit_no, vgroup, dim_name)
        _EnumStatCollector.__init__(self, default_value, variants,
            self.getMaster().getDSKind() != "ws")
        assert sub_kind.startswith("transcript-"), (
            "Expected leading transcript- in sub_kind: " + sub_kind)
        assert not transcript_id_mode or sub_kind == "transcript-status", (
            "Transcript ID unit has not status subtype:" + name)
        self.mSubKind = sub_kind
        self.mTransName = trans_name
        if self.mTransName is None:
            assert self.mSubKind == "transcript-panels", (
                "Unexpected sub_kind: " + self.mSubKind)
            assert default_value is None, (
                "Default value is set: " + repr(default_value))

    def getTranscriptName(self):
        return self.mTransName

    def process(self, rec_no, rec_data, result):
        assert False

    def dump(self):
        ret = ValueConvertor.dump(self)
        ret.update(self.statResult())
        ret["sub-kind"] = self.mSubKind
        ret["tr-name"] = self.mTransName
        return ret

#===============================================
class TranscriptStatusConvertor(_TranscriptEnumConvertor):
    def __init__(self, master, name, unit_no, vgroup, dim_name,
            sub_kind, trans_name, variants, default_value,
            bool_check_value = None, transcript_id_mode = False):
        _TranscriptEnumConvertor.__init__(self, master, name, unit_no,
            vgroup, dim_name, sub_kind,
            trans_name, variants, default_value)
        self.mTransName = trans_name
        self.mTrIdMode = transcript_id_mode
        self.mBoolCheckValue = bool_check_value
        self.mIsOK = True

    def getTranscriptName(self):
        return self.mTransName

    def process(self, rec_no, rec_data, result):
        assert False

    def isTranscriptID(self):
        return self.mTrIdMode

    def isOK(self):
        return self.mIsOK

    def regError(self, value):
        if self.mIsOK:
            logging.error(
                f"For status tr-unit {self.getName()} bad value: {value}")
            self.mIsOK = False
        return self.regErrVal()

    def processOne(self, value):
        if not isinstance(value, list):
            value = str(value)
        else:
            assert len(value) == 1, (
                "Tr-Unit " + self.getName() + " not a list of lenght 1: "
                + repr(value))
            value = str(value[0])
        if self.mBoolCheckValue is not None:
            value = "True" if self.mBoolCheckValue == value else "False"
        val = self.regVal(value)
        if val is False:
            return self.regError(value)
        return val

    def processEmpty(self):
        if self.getDefault() is not None:
            self.regVal(self.getDefault())

    def dump(self):
        ret = _TranscriptEnumConvertor.dump(self)
        ret["tr-id-mode"] = self.mTrIdMode
        ret["bool-check"] = self.mBoolCheckValue
        return ret

#===============================================
class TranscriptMultiConvertor(_TranscriptEnumConvertor):
    def __init__(self, master, name, unit_no, vgroup, dim_name,
            sub_kind, trans_name, variants, default_value):
        _TranscriptEnumConvertor.__init__(self, master, name, unit_no,
            vgroup, dim_name, sub_kind, trans_name, variants, default_value)
        self.mIsOK = True

    def getTranscriptName(self):
        return self.mTransName

    def process(self, rec_no, rec_data, result):
        assert False

    def isOK(self):
        return self.mIsOK

    def regError(self, value):
        if self.mIsOK:
            logging.error(f"For multi tr-unit {self.getName()} bad value:"
                + repr(value))
            self.mIsOK = False

    def processOne(self, value):
        values = set()
        if value:
            for val in value:
                res_val = self.regVal(val)
                if res_val is False:
                    self.regError(value)
                else:
                    values.add(res_val)
        return sorted(values)

    def processEmpty(self):
        pass

#===============================================
# Reserved
class TranscriptPanelsConvertor(TranscriptMultiConvertor):
    def __init__(self, master, name, unit_no, vgroup, dim_name,
            base_tr_name, panel_type, view_name):
        p_key = "panel." + panel_type
        panel_sets = {p_it["name"]: p_it["data"]
            for p_it in master.iterStdItems(p_key)}
        TranscriptMultiConvertor.__init__(self, master, name,
            unit_no, vgroup, dim_name, "transcript-panels",
            base_tr_name, sorted(panel_sets.keys()), None)
        self.mPanelType = panel_type
        self.mViewName = view_name
        self.mPanelSets = panel_sets
        assert len(self.mPanelSets) > 0, (
            "No data for panel type " + self.mPanelType)

    def processOne(self, value):
        res = []
        if value:
            for pname, pset in self.mPanelSets.items():
                if value in pset:
                    res.append(self.regVal(pname))
            res.sort()
            assert False not in res
        return res

    def dump(self):
        ret = TranscriptMultiConvertor.dump(self)
        del ret["tr-name"]
        ret["panel-base"] = self.getTranscriptName()
        ret["panel-type"] = self.mPanelType
        if self.mViewName:
            ret["view-name"] = self.mViewName
        return ret

#===============================================
class TranscriptVarietyConvertor(TranscriptStatusConvertor):
    def __init__(self, master, name, unit_no, vgroup,
            trans_name, panel_type, panel_name, default_value):
        TranscriptStatusConvertor.__init__(self, master, name, unit_no,
            vgroup, None, "transcript-variety", trans_name,
            None, default_value)
        self.mPanelName = panel_name
        self.mPanelType = panel_type

    def dump(self):
        ret = TranscriptStatusConvertor.dump(self)
        ret["mean"] = "variety"
        ret["panel-name"] = self.mPanelName
        ret["panel-type"] = self.mPanelType
        return ret

#===============================================
#===============================================
def loadConvertorInstance(info, vgroup, filter_set):
    if info.get("vgroup") is None:
        assert vgroup is None, "!No vgroup here: " + vgroup.getTitle()
    else:
        assert vgroup.getTitle() == info["vgroup"], (
            "Title vgroup conflict: " + vgroup.getTitle() + " vs. "
            + info["vgroup"])
    kind = info["kind"]

    if kind == "numeric":
        if info["sub-kind"].startswith("transcript-"):
            return TranscriptNumConvertor(
                filter_set, info["name"], info["no"], vgroup,
                info["sub-kind"], info["tr-name"], info.get("default"))
        if info["sub-kind"] == "float":
            return FloatConvertor(filter_set, info["name"], info["path"],
                info["no"], vgroup, info.get("default"), None,
                info.get("conversion"))
        if info["sub-kind"] == "int":
            return IntConvertor(filter_set, info["name"], info["path"],
                info["no"], vgroup, info.get("default"), None,
                info.get("conversion"))
        assert False, f'Bad numeric unit: {info["sub-kind"]}'
        return None

    if kind == "enum":
        assert info.get("mean") != "panel" or "panel-name" not in info
        if info["sub-kind"] == "transcript-variety":
            return TranscriptVarietyConvertor(filter_set, info["name"],
                info["no"], vgroup, info["tr-name"],
                info["panel-type"], info["panel-name"], info.get("default"))
        assert info.get("mean") != "variety"
        if info["sub-kind"] == "transcript-panels":
            return TranscriptPanelsConvertor(
                filter_set, info["name"], info["no"], vgroup,
                info.get("dim-name"), info["panel-base"],
                info["panel-type"], info.get("view-name"))
        if info["sub-kind"] == "transcript-status":
            return TranscriptStatusConvertor(filter_set, info["name"],
                info["no"], vgroup, info.get("dim-name"), info["sub-kind"],
                info["tr-name"], info.get("pre-variants"),
                info.get("default"), info["bool-check"],
                info.get("tr-id-mode"))
        if info["sub-kind"] == "transcript-multiset":
            return TranscriptMultiConvertor(filter_set, info["name"],
                info["no"], vgroup, info.get("dim-name"),
                info["sub-kind"], info["tr-name"],
                info.get("pre-variants"), info.get("default"))
        if info.get("mean") == "presence":
            path_info_seq = [(var, it_path)
                for var, _, it_path in info["variants"]]
            return PresenceConvertor(filter_set, info["name"],
                info["no"], vgroup, path_info_seq)
        if info.get("mean") == "panel":
            return PanelConvertor(filter_set, info["name"], info["no"],
                vgroup, info.get("dim-name"), info["panel-base"],
                info["panel-type"], info.get("view-path"))
        if info.get("mean") == "pre-variety":
            return VarietyConvertor(filter_set, info["name"], info["no"],
                vgroup, info["variety-name"], info["panel-name"],
                info["path"], info["panel-type"], info["separator"])

        return EnumConvertor(filter_set, info["name"], info["path"],
            info["no"], vgroup, info.get("dim-name"), info["sub-kind"],
            info.get("pre-variants"), info.get("value-map"),
            info.get("conversion"), default_value = info.get("default"),
            compact_mode = info.get("compact", False),
            separators = info.get("separators"))

    assert False, f'Bad unit={info["name"]} kind={info["kind"]}'
    return None
