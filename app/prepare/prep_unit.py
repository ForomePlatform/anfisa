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

import abc, re
from collections import Counter

from app.config.flt_conv import makeFilterConversion
from forome_tools.path_works import AttrFuncPool
#===============================================
class ValueConvertor:
    sMAX_BAD_COUNT = 3

    def __init__(self, master, name, title, unit_no, vgroup,
            render_mode, tooltip):
        self.mMaster = master
        self.mName   = name
        self.mTitle  = title if title is not None else name
        self.mVGroup = vgroup
        self.mUnitNo = unit_no
        self.mErrorCount = 0
        self.mErrors = []
        self.mRenderMode = render_mode
        self.mToolTip = tooltip
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

    def getTranscriptDescr(self):
        return None

    def getMaster(self):
        return self.mMaster

    def dump(self):
        result = {
            "name": self.mName,
            "title": self.mTitle,
            "no": self.mUnitNo}
        if self.mVGroup is not None:
            result["vgroup"] = self.mVGroup.getTitle()
        if self.mRenderMode is not None:
            result["render"] = self.mRenderMode
        if self.mToolTip:
            result["tooltip"] = self.mToolTip
        if self.mErrorCount > 0:
            result["errors"] = [self.mErrorCount, self.mErrors]
        return result

    @classmethod
    def registerConvertorType(cls, kind, sub_kind, conv_class):
        key = (kind, sub_kind)
        assert key not in cls.sConvertors
        cls.sConvertors[key] = conv_class

#===============================================
class PathValueConvertor(ValueConvertor):
    sMAX_BAD_COUNT = 3

    def __init__(self, master, name, vpath, title, unit_no, vgroup,
            render_mode, tooltip):
        ValueConvertor.__init__(self, master, name, title, unit_no,
            vgroup, render_mode, tooltip)
        self.mPath   = vpath
        self.mPathF  = AttrFuncPool.makeFunc(self.mPath)

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
class _NumericConvertor(PathValueConvertor):
    def __init__(self, master, name, vpath, title, unit_no, vgroup,
            default_value, diap, conversion, render_mode, tooltip):
        PathValueConvertor.__init__(self, master, name, vpath, title, unit_no,
            vgroup, render_mode, tooltip)
        if diap is not None:
            self.mMinBound, self.mMaxBound = diap
        else:
            self.mMinBound = None
        assert default_value is not None
        self.mDefaultValue = default_value
        self.mConversion = conversion
        self.mConvFunc = makeFilterConversion(conversion, self.getMaster())
        self.mMinValue, self.mMaxValue = None, None
        self.mCntDef = 0
        self.mCntUndef = 0

    @abc.abstractmethod
    def convType(self, val):
        return None

    def checkSetup(self):
        assert self.mDefaultValue == self.convType(self.mDefaultValue)
        if self.mMinBound is not None:
            assert self.mMinBound == self.convType(self.mMinBound)
            assert self.mMaxBound == self.convType(self.mMaxBound)
            if self.mDefaultValue is not None:
                assert self.mMinBound <= self.mDefaultValue <= self.mMaxBound

    def convert(self, values, rec_no):
        try:
            if self.mConvFunc is not None and len(values) == 1:
                values = [self.mConvFunc(values[0])]
            if len(values) == 0:
                values = [None]
            if len(values) == 1:
                if values[0] is None:
                    val = self.mDefaultValue
                else:
                    val = self.convType(values[0])
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
        except Exception:
            pass
        if self.mDefaultValue is None:
            self.mCntUndef += 1
        else:
            self.mCntDef += 1
        self.regError(rec_no, values)
        return self.mDefaultValue

    def dump(self):
        ret = PathValueConvertor.dump(self)
        ret["kind"] = "numeric"
        ret["def"] = self.mCntDef
        ret["undef"] = self.mCntUndef
        ret["min"] = self.mMinValue
        ret["max"] = self.mMaxValue
        ret["default"] = self.mDefaultValue
        if self.mMinBound is not None:
            ret["diap"] = [self.mMinBound, self.mMaxBound]
        if self.mConversion is not None:
            ret["conversion"] = self.mConversion
        return ret

#===============================================
class FloatConvertor(_NumericConvertor):
    def __init__(self, master, name, vpath, title, unit_no, vgroup,
            default_value, diap, conversion, render_mode, tooltip):
        _NumericConvertor.__init__(self,
            master, name, vpath, title, unit_no, vgroup,
            default_value, diap, conversion, render_mode, tooltip)
        self.checkSetup()

    def convType(self, val):
        return float(val)

    def dump(self):
        ret = _NumericConvertor.dump(self)
        ret["sub-kind"] = "float"
        return ret

#===============================================
class IntConvertor(_NumericConvertor):
    def __init__(self, master, name, vpath, title, unit_no, vgroup,
            default_value, diap, conversion, render_mode, tooltip):
        _NumericConvertor.__init__(self,
            master, name, vpath, title, unit_no, vgroup,
            default_value, diap, conversion, render_mode, tooltip)
        self.checkSetup()

    def convType(self, val):
        return int(val)

    def dump(self):
        ret = _NumericConvertor.dump(self)
        ret["sub-kind"] = "int"
        return ret

#===============================================
#===============================================
class EnumConvertor(PathValueConvertor):
    def __init__(self, master, name, vpath, title, unit_no, vgroup,
            sub_kind, variants, accept_other_values, value_map,
            conversion, render_mode, tooltip,
            default_value = None, compact_mode = False,  separators = None):
        PathValueConvertor.__init__(self, master, name, vpath, title, unit_no,
            vgroup, render_mode, tooltip)
        self.mSubKind = sub_kind
        self.mPreVariants = variants
        self.mVariantSet = None
        self.mDefaultValue = default_value
        self.mValueMap = value_map
        self.mDefaultRet = None
        self.mSeparators = separators
        if self.mSeparators:
            self.mSepPatt = re.compile(self.mSeparators)
        self.mCompactMode = compact_mode
        self.mCntUndef = 0
        self.mConversion = conversion
        self.mConvFunc = makeFilterConversion(conversion, self.getMaster())
        assert sub_kind in {"status", "multi"}
        self.mAcceptOtherValues = accept_other_values
        if self.mAcceptOtherValues:
            assert self.mPreVariants is not None
        elif self.mPreVariants is not None:
            self.mVariantSet = set(self.mPreVariants)
            if self.mDefaultValue is not None:
                assert self.mDefaultValue in self.mVariantSet
        self.mVarCount = Counter()
        if self.mDefaultValue is not None:
            assert isinstance(self.mDefaultValue, str)
            if self.mSubKind == "status":
                self.mDefaultRet = self.mDefaultValue
            else:
                self.mDefaultRet = [self.mDefaultValue]
        if self.mPreVariants is not None:
            for var in self.mPreVariants:
                assert isinstance(var, str)

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
                if (self.mVariantSet is not None
                        and val not in self.mVariantSet):
                    is_ok = False
                    continue
                self.mVarCount[val] += 1
                ret.append(val)
        except Exception:
            is_ok = False
        if self.mSubKind == "status" and len(ret) > 1:
            is_ok = False
        if not is_ok:
            self.regError(rec_no, values)
        if len(ret) == 0:
            if self.mDefaultValue is None:
                self.mCntUndef += 1
            else:
                self.mVarCount[self.mDefaultValue] += 1
            return self.mDefaultRet
        if self.mSubKind == "status":
            return ret[0]
        return ret

    def dump(self):
        ret = PathValueConvertor.dump(self)
        ret["kind"] = "enum"
        ret["sub-kind"] = self.mSubKind
        ret["compact"] = self.mCompactMode
        ret["default"] = self.mDefaultValue
        ret["undef"] = self.mCntUndef
        ret["other-values"] = self.mAcceptOtherValues
        if self.mPreVariants is not None:
            ret["pre-variants"] = self.mPreVariants
        if self.mValueMap:
            ret["value-map"] = self.mValueMap
        if self.mConversion:
            ret["conversion"] = self.mConversion
        if self.mSeparators:
            ret["separators"] = self.mSeparators
        variants = []
        used_variants = set()
        if self.mPreVariants:
            for var in self.mPreVariants:
                if var in self.mVarCount:
                    variants.append([var, self.mVarCount[var]])
            used_variants = set(self.mPreVariants)
        for var in sorted(set(self.mVarCount.keys()) - used_variants):
            variants.append([var, self.mVarCount[var]])
        assert all(info[1] > 0 for info in variants)
        ret["variants"] = variants
        return ret

#===============================================
class PresenceConvertor(ValueConvertor):
    def __init__(self, master, name, title, unit_no, vgroup,
            path_info_seq, render_mode, tooltip):
        ValueConvertor.__init__(self, master, name, title, unit_no,
            vgroup, render_mode, tooltip)
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
            if self.mVarCount[var] > 0:
                variants.append([var, self.mVarCount[var], it_path])
        ret["variants"] = variants
        return ret

#===============================================
class PanelConvertor(ValueConvertor):
    def __init__(self, master, name, title, unit_no, vgroup,
            unit_base, panel_type, view_path, render_mode, tooltip):
        ValueConvertor.__init__(self, master, name, title, unit_no, vgroup,
            render_mode, tooltip)
        self.mBaseUnitName = unit_base.getName()
        self.mPanelType = panel_type
        self.mPanelSets = {
            pname: set(self.getMaster().getPanelVariants(pname))
            for pname in self.getMaster().getPanelNames(self.mPanelType)}
        assert len(self.mPanelSets) > 0, (
            "No data for panel type " + panel_type)
        self.mCntUndef = 0
        self.mVarCount = Counter()
        self.mViewPath = view_path
        self.mViewPathSeq = None
        if self.mViewPath is not None:
            assert self.mViewPath.startswith('/')
            self.mViewPathSeq = self.mViewPath.split('/')[1:]

    def process(self, rec_no, rec_data, result):
        pitems = result.get(self.mBaseUnitName)
        res_val = []
        if pitems:
            pitems = set(pitems)
            for pname, pset in self.mPanelSets.items():
                if len(pitems & pset) > 0:
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
class TranscriptNumConvertor(ValueConvertor):
    def __init__(self, master, name, title, unit_no, vgroup,
            sub_kind, trans_name, default_value,
            render_mode, tooltip):
        ValueConvertor.__init__(self, master, name, title, unit_no, vgroup,
            render_mode, tooltip)
        prefix, _, postfix = sub_kind.partition('-')
        assert prefix == "transcript" and postfix in ("int", "float")
        self.mDescr = ValueConvertor.dump(self)
        self.mDescr["kind"] = "numeric"
        self.mDescr["sub-kind"] = sub_kind
        self.mDescr["tr-name"] = trans_name
        self.mDescr["default"] = default_value
        assert default_value is not None

    def process(self, rec_no, rec_data, result):
        pass

    def dump(self):
        return self.mDescr

    def getTranscriptDescr(self):
        return self.mDescr

#===============================================
class TranscriptEnumConvertor(ValueConvertor):
    def __init__(self, master, name, title, unit_no, vgroup,
            sub_kind, trans_name, variants, default_value,
            render_mode, tooltip, bool_check_value = False):
        ValueConvertor.__init__(self, master, name, title, unit_no, vgroup,
            render_mode, tooltip)
        assert sub_kind.startswith("transcript-")
        self.mDescr = ValueConvertor.dump(self)
        self.mDescr["kind"] = "enum"
        self.mDescr["sub-kind"] = sub_kind
        self.mDescr["bool-check"] = bool_check_value
        if trans_name is None:
            assert sub_kind == "transcript-panels"
            assert default_value is None
            return
        self.mDescr["tr-name"] = trans_name
        self.mDescr["pre-variants"] = variants
        if default_value is not None:
            self.mDescr["default"] = default_value
            if variants is not None:
                assert default_value in variants

    def process(self, rec_no, rec_data, result):
        pass

    def dump(self):
        return self.mDescr

    def getTranscriptDescr(self):
        return self.mDescr

    def getTranscriptName(self):
        return self.mDescr["tr-name"]

#===============================================
class TranscriptPanelsConvertor(TranscriptEnumConvertor):
    def __init__(self, master, name, title, unit_no, vgroup,
            unit_base, panel_type, view_name,
            render_mode, tooltip):
        TranscriptEnumConvertor.__init__(self,
            master, name, title, unit_no, vgroup,
            "transcript-panels", None, None, None,
            render_mode, tooltip)
        self.mDescr["panel-base"] = unit_base.getTranscriptName()
        self.mDescr["panel-type"] = panel_type
        if view_name:
            self.mDescr["view-name"] = view_name
        panel_names = list(self.getMaster().getPanelNames(panel_type))
        assert len(panel_names) > 0, (
            "No data for panel type " + panel_type)

#===============================================
#===============================================
class _DummyUnitHandler:
    def __init__(self, name):
        self.mName = name

    def getName(self):
        return self.mName

    def getTranscriptName(self):
        return self.mName

#===============================================
def loadConvertorInstance(info, vgroup, filter_set):
    if info.get("vgroup") is None:
        assert vgroup is None
    else:
        assert vgroup.getTitle() == info["vgroup"]
    kind = info["kind"]

    if kind == "numeric":
        if info["sub-kind"].startswith("transcript-"):
            return TranscriptNumConvertor(filter_set, info["name"],
                info["title"], info["no"], vgroup,
                info["sub-kind"], info["tr-name"], info.get("default"),
                info.get("render"), info.get("tooltip"))
        if info["sub-kind"] == "float":
            return FloatConvertor(filter_set, info["name"], info["path"],
                info["title"], info["no"], vgroup,
                info.get("default"), None,
                info.get("conversion"),
                info.get("render"), info.get("tooltip"))
        if info["sub-kind"] == "int":
            return IntConvertor(filter_set, info["name"], info["path"],
                info["title"], info["no"], vgroup,
                info.get("default"), None,
                info.get("conversion"),
                info.get("render"), info.get("tooltip"))
        assert False, "Bad numeric unit: %s" % info["sub-kind"]
        return None

    if kind == "enum":
        if info["sub-kind"] == "transcript-panels":
            return TranscriptPanelsConvertor(filter_set, info["name"],
                info["title"], info["no"], vgroup,
                _DummyUnitHandler(info["panel-base"]),
                info["panel-type"], info.get("view-name"),
                info.get("render"), info.get("tooltip"))
        if info["sub-kind"].startswith("transcript-"):
            return TranscriptEnumConvertor(filter_set, info["name"],
                info["title"], info["no"], vgroup,
                info["sub-kind"], info["tr-name"], info["pre-variants"],
                info.get("default"),
                info.get("render"), info.get("tooltip"), info["bool-check"])
        if info.get("mean") == "presence":
            path_info_seq = [(var, it_path)
                for var, _, it_path in info["variants"]]
            return PresenceConvertor(filter_set, info["name"],
                info["title"], info["no"], vgroup, path_info_seq,
                info.get("render"), info.get("tooltip"))
        if info.get("mean") == "panel":
            return PanelConvertor(filter_set, info["name"],
                info["title"], info["no"], vgroup,
                _DummyUnitHandler(info["panel-base"]), info["panel-type"],
                info.get("view-path"),
                info.get("render"), info.get("tooltip"))
        return EnumConvertor(filter_set, info["name"], info["path"],
            info["title"], info["no"], vgroup,
            info["sub-kind"], info.get("pre-variants"),
            info["other-values"], info.get("value-map"),
            info.get("conversion"), info.get("render"), info.get("tooltip"),
            default_value = info.get("default"),
            compact_mode = info["compact"],
            separators = info.get("separators"))

    assert False, "Bad unit %s kind %s" % (info["name"], info["kind"])
    return None
