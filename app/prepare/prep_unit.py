import abc, re, sys
from collections import Counter

from utils.path_works import AttrFuncPool
from app.config.solutions import Solutions
#===============================================
class ValueConvertor:
    sMAX_BAD_COUNT = 3

    def __init__(self, name, title, unit_no, vgroup,
            render_mode, research_only):
        self.mName   = name
        self.mTitle  = title if title is not None else name
        self.mVGroup = vgroup
        self.mUnitNo = unit_no
        self.mRsrOnly  = research_only
        self.mErrorCount = 0
        self.mErrors = []
        self.mRenderMode = render_mode
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

    def dump(self):
        result = {
            "name": self.mName,
            "title": self.mTitle,
            "no": self.mUnitNo,
            "research": self.mRsrOnly}
        if self.mVGroup is not None:
            result["vgroup"] = self.mVGroup.getTitle()
        if self.mRenderMode is not None:
            result["render"] = self.mRenderMode
        if self.mErrorCount > 0:
            result["errors"] = [self.mErrorCount, self.mErrors]
        return result

#===============================================
class PathValueConvertor(ValueConvertor):
    sMAX_BAD_COUNT = 3

    def __init__(self, name, path, title, unit_no, vgroup,
            render_mode, research_only):
        ValueConvertor.__init__(self,
            name, title, unit_no, vgroup, render_mode, research_only)
        self.mPath   = path
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
    def __init__(self, name, path, title, unit_no, vgroup,
            render_mode, research_only, default_value = None, diap = None):
        PathValueConvertor.__init__(self, name,
            path, title, unit_no, vgroup, render_mode, research_only)
        if diap is not None:
            self.mMinBound, self.mMaxBound = diap
        else:
            self.mMinBound = None
        assert default_value is not None
        self.mDefaultValue = default_value
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
            if len(values) == 0:
                if self.mDefaultValue is None:
                    self.mCntUndef += 1
                else:
                    self.mCntDef += 1
                return self.mDefaultValue
            if len(values) == 1:
                val = self.convType(values[0])
                if (self.mMinBound is None or
                        self.mMinBound <= val <= self.mMaxBound):
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
        ret["def"] = self.mCntDef
        ret["undef"] = self.mCntUndef
        ret["min"] = self.mMinValue
        ret["max"] = self.mMaxValue
        ret["default"] = self.mDefaultValue
        if self.mMinBound is not None:
            ret["diap"] = [self.mMinBound, self.mMaxBound]
        return ret

#===============================================
class FloatConvertor(_NumericConvertor):
    def __init__(self, name, path, title, unit_no, vgroup, render_mode,
            research_only, default_value = None, diap = None):
        _NumericConvertor.__init__(self, name, path, title,
            unit_no, vgroup, render_mode, research_only, default_value, diap)
        self.checkSetup()

    def convType(self, val):
        return float(val)

    def dump(self):
        ret = _NumericConvertor.dump(self)
        ret["kind"] = "float"
        return ret

#===============================================
class IntConvertor(_NumericConvertor):
    def __init__(self, name, path, title, unit_no, vgroup, render_mode,
            research_only, default_value = None, diap = None):
        _NumericConvertor.__init__(self, name, path, title,
            unit_no, vgroup, render_mode, research_only, default_value, diap)
        self.checkSetup()

    def convType(self, val):
        return int(val)

    def dump(self):
        ret = _NumericConvertor.dump(self)
        ret["kind"] = "long"
        return ret

#===============================================
#===============================================
class EnumConvertor(PathValueConvertor):
    def __init__(self, name, path, title, unit_no, vgroup,
            render_mode, research_only,
            atomic_mode, variants = None, default_value = None,
            separators = None, compact_mode = False,
            accept_other_values = False):
        PathValueConvertor.__init__(self, name, path, title, unit_no,
            vgroup, render_mode, research_only)
        self.mAtomicMode = atomic_mode
        self.mPreVariants = variants
        self.mVariantSet = None
        self.mDefaultValue = default_value
        self.mDefaultRet = None
        self.mSeparators = re.compile(separators) if separators else None
        self.mCompactMode = compact_mode
        self.mCntUndef = 0
        if accept_other_values:
            assert self.mPreVariants is not None
        elif self.mPreVariants is not None:
            self.mVariantSet = set(self.mPreVariants)
            if self.mDefaultValue is not None:
                assert self.mDefaultValue in self.mVariantSet
        self.mVarCount = Counter()
        if self.mDefaultValue is not None:
            assert isinstance(self.mDefaultValue, basestring)
            if not self.mAtomicMode:
                self.mDefaultRet = [self.mDefaultValue]
            else:
                self.mDefaultRet = self.mDefaultValue
        if self.mPreVariants is not None:
            for var in self.mPreVariants:
                assert isinstance(var, basestring)

    def isAtomic(self):
        return self.mAtomicMode

    def convert(self, values, rec_no):
        ret = []
        try:
            mod_values = values
            if self.mSeparators:
                mod_values = []
                for val in values:
                    for v in re.split(self.mSeparators, val):
                        if v:
                            mod_values.append(v)
            is_ok = True
            mod_values = map(unicode, mod_values)
            for val in set(mod_values):
                if (self.mVariantSet is not None and
                        val not in self.mVariantSet):
                    is_ok = False
                    continue
                self.mVarCount[val] += 1
                ret.append(val)
        except Exception:
            is_ok = False
        if self.mAtomicMode and len(ret) > 1:
            is_ok = False
        if not is_ok:
            self.regError(rec_no, values)
        if len(ret) == 0:
            if self.mDefaultValue is None:
                self.mCntUndef += 1
            else:
                self.mVarCount[self.mDefaultValue] += 1
            return self.mDefaultRet
        if self.mAtomicMode:
            return ret[0]
        return ret

    def dump(self):
        ret = PathValueConvertor.dump(self)
        ret["kind"] = "enum"
        ret["atomic"] = self.mAtomicMode
        ret["compact"] = self.mCompactMode
        ret["default"] = self.mDefaultValue
        ret["undef"] = self.mCntUndef

        variants = []
        used_variants = set()
        if self.mPreVariants:
            for var in self.mPreVariants:
                if var in self.mVarCount:
                    variants.append([var, self.mVarCount[var]])
            used_variants = set(self.mPreVariants)
        for var in sorted(set(self.mVarCount.keys()) - used_variants):
            variants.append([var, self.mVarCount[var]])
        assert all([info[1] > 0 for info in variants])
        ret["variants"] = variants
        return ret

#===============================================
class PresenceConvertor(ValueConvertor):
    def __init__(self, name, title, unit_no, vgroup,
            render_mode, research_only, path_info_seq):
        ValueConvertor.__init__(self,
            name, title, unit_no, vgroup, render_mode, research_only)
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
        ret["kind"] = "presence"
        variants = []
        for var, it_path in self.mPathInfoSeq:
            if self.mVarCount[var] > 0:
                variants.append([var, self.mVarCount[var], it_path])
        ret["variants"] = variants
        return ret

#===============================================
class ZygosityConvertor(ValueConvertor):
    def __init__(self, name, path, title, unit_no, vgroup,
            render_mode, research_only, config, master):
        ValueConvertor.__init__(self, name, title, unit_no, vgroup,
            render_mode, research_only)
        self.mPath   = path
        self.mPathF  = AttrFuncPool.makeFunc(self.mPath)
        self.mConfig = config
        self.mMaster = master
        self.mFamilyMembers = None

    def process(self, rec_no, rec_data, result):
        if self.mFamilyMembers is None:
            if self.mMaster.getFamilyInfo() is None:
                print >> sys.stderr, "No dataset metadata with samples info"
                assert False
            self.mFamilyMembers = self.mMaster.getFamilyInfo().getMembers()
        if len(self.mFamilyMembers) < 2:
            return
        zig_distr_seq = self.mPathF(rec_data)
        assert len(zig_distr_seq) == 1
        zig_distr = zig_distr_seq[0]
        assert len(zig_distr.keys()) == len(self.mFamilyMembers)
        for idx, member in enumerate(self.mFamilyMembers):
            result["%s_%d" % (self.getName(), idx)] = zig_distr[member]

    def dump(self):
        ret = ValueConvertor.dump(self)
        ret["kind"] = "zygosity"
        ret["path"] = self.mPath
        if self.mConfig is not None:
            ret["config"] = self.mConfig
        ret["size"] = (len(self.mFamilyMembers)
                if self.mFamilyMembers is not None else 0)
        return ret

#===============================================
class PanelConvertor(ValueConvertor):
    def __init__(self, name, title, unit_no, vgroup,
            render_mode, research_only, unit_base, view_path = None):
        ValueConvertor.__init__(self, name, title, unit_no, vgroup,
            render_mode, research_only)
        self.mBaseUnitName = unit_base.getName()
        self.mPanelSets = {
            pname: set(Solutions.getPanel(self.mBaseUnitName, pname))
            for pname in Solutions.getPanelNames(self.mBaseUnitName)}
        self.mCntUndef = 0
        self.mVarCount = Counter()
        self.mViewPath = None
        if view_path is not None:
            assert view_path.startswith('/')
            self.mViewPath = view_path.split('/')[1:]

    def process(self, rec_no, rec_data, result):
        pitems = result.get(self.mBaseUnitName)
        if pitems:
            pitems = set(pitems)
            res_val = []
            for pname, pset in self.mPanelSets.items():
                if len(pitems & pset) > 0:
                    res_val.append(pname)
                    self.mVarCount[pname] += 1
            if res_val:
                res_val.sort()
                result[self.getName()] = res_val
                if self.mViewPath:
                    data = rec_data
                    for nm in self.mViewPath[:-1]:
                        data = data[nm]
                    data[self.mViewPath[-1]] = res_val

    def dump(self):
        ret = ValueConvertor.dump(self)
        ret["kind"] = "enum"
        ret["atomic"] = False
        ret["compact"] = False
        ret["default"] = None
        ret["undef"] = self.mCntUndef
        variants = []
        for var in sorted(self.mVarCount.keys()):
            variants.append([var, self.mVarCount[var]])
        ret["variants"] = variants
        return ret
