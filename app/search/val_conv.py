#import sys
import abc
from collections import Counter

from .val_stat import BoolStat, NumDiapStat, EnumStat
from .variants import VariantSet
#===============================================
class ValueConvertor:
    def __init__(self):
        pass

    def isAtomic(self):
        return True

    @abc.abstractmethod
    def newStat(self):
        return None

    @abc.abstractmethod
    def setup(self, rep_out):
        return None

    @abc.abstractmethod
    def getVarTypeCode(self):
        return None

    @abc.abstractmethod
    def hasDefault(self):
        return None

    @abc.abstractmethod
    def testValues(self, values):
        return None

    @abc.abstractmethod
    def convert(self, values):
        return None


#===============================================
#===============================================
class BoolConvertor(ValueConvertor):
    def __init__(self):
        ValueConvertor.__init__(self)
        self.mStat = BoolStat()

    def newStat(self):
        return BoolStat()

    def setup(self, rep_out):
        self.mStat.report(rep_out)
        return True

    def getVarTypeCode(self):
        return "bool"

    def hasDefault(self):
        return True

    def testValues(self, values):
        if len(values) > 1:
            return False
        val = len(values) > 0 and values[0]
        self.mStat.regValue(val)
        return True

    def convert(self, values):
        return len(values) > 0 and values[0]

#===============================================
class _NumericConvertor(ValueConvertor):
    def __init__(self, num_type, num_name,
            default_value = 0., diap = (0., 1.)):
        ValueConvertor.__init__(self)
        self.mNumType = num_type
        self.mNumName = num_name
        assert (default_value is None or
            num_type(default_value) == default_value)
        self.mDefaultValue = default_value
        if diap is not None:
            self.mMinValue, self.mMaxValue = diap
            assert (self.mDefaultValue is None or
                self.mMinValue <= self.mDefaultValue <= self.mMaxValue)
        else:
            self.mMinValue = None
        self.mStat = NumDiapStat(num_name)
        self.mBadValues = Counter()

    def newStat(self):
        return NumDiapStat(self.mNumName)

    def setup(self, rep_out):
        self.mStat.report(rep_out)
        if len(self.mBadValues) > 0:
            print >> rep_out, "Bad values %d:" % len(self.mBadValues)
            for neg_cnt, val in sorted([(-cnt, val)
                    for val, cnt in self.mBadValues.items()])[:5]:
                print >> rep_out, "\t %s: %d" % (-neg_cnt, val)
            if len(self.mBadValues) > 5:
                print >> rep_out, "\t..."
        return self.mStat.isDefined() and len(self.mBadValues) == 0

    def getVarTypeCode(self):
        ret = self.mNumName
        add_tp = []
        if self.mDefaultValue:
            add_tp.append("=" + str(self.mDefaultValue))
        if self.mMinValue is not None:
            add_tp.append("%s < %s" %
                (str(self.mMinValue), str(self.mMaxValue)))
        if len(add_tp) > 0:
            ret += '(' + ', '.join(add_tp) + ')'
        return ret

    def hasDefault(self):
        return self.mDefaultValue is not None

    def testValues(self, values):
        if len(values) > 1:
            self.mBadValues["<?list?>"] += 1
            self.mStat.regValue(None)
            return False
        try:
            if len(values) == 0:
                val = self.mDefaultValue
            else:
                val = self.mNumType(values[0])
            if val is None:
                self.mStat.regValue(None)
                return True
            if (self.mMinValue is not None and not
                    (self.mMinValue <= val <= self.mMaxValue)):
                self.mBadValues[str(val)] += 1
                return False
            self.mStat.regValue(val)
            return True
        except Exception:
            self.mStat.regValue(None)
            self.mBadValues[str(values)] += 1
            return False

    def convert(self, values):
        if len(values) == 0:
            return self.mDefaultValue
        try:
            val = self.mNumType(values[0])
            if self.mMinValue is None:
                return val
            return min(max(val, self.mMinValue), self.mMaxValue)
        except Exception:
            return None

#===============================================
class FloatConvertor(_NumericConvertor):
    def __init__(self, default_value = 0., diap = (0., 1.)):
        _NumericConvertor.__init__(self, float, "float", default_value, diap)

class IntConvertor(_NumericConvertor):
    def __init__(self, default_value = 0., diap = (0., 1.)):
        _NumericConvertor.__init__(self, int, "int", default_value, diap)

#===============================================
class EnumConvertor(ValueConvertor):
    def __init__(self, variant_set = None, atomic_mode = False,
            chunker = None, default_value = False, others_value = False):
        ValueConvertor.__init__(self)
        self.mVariantSet = None
        self.mAtomicMode = atomic_mode
        self.mChunker = chunker
        self.mDefaultValue = default_value
        self.mDefaultVariant = {}
        self.mOthersValue = others_value
        self.mOthersVariant = {}
        self.mStat = Counter()
        self.mBadValues = False
        if variant_set is not None:
            self.__initVariants(variant_set)

    def isAtomic(self):
        return self.mAtomicMode

    def newStat(self):
        return EnumStat(self.mVariantSet)

    def __initVariants(self, variant_set):
        self.mVariantSet = variant_set
        if self.mDefaultValue is not False:
            idx = self.mVariantSet.indexOf(self.mDefaultValue)
            if idx is not None:
                self.mDefaultVariant = {idx}
        else:
            self.mDefaultVariant = {}
        if self.mOthersValue is not False:
            idx = self.mVariantSet.indexOf(self.mOthersValue)
            if idx is not None:
                self.mOthersVariant = {idx}
        else:
            self.mOthersVariant = {}

    def setup(self, rep_out):
        if self.mBadValues:
            print >> rep_out, "=NOTE: Has bad values!"
        elif self.mVariantSet is None:
            variants = []
            for name in self.mStat.keys():
                if name is not None:
                    variants.append(name)
            variants.sort()
            if (self.mOthersValue is not False and
                    self.mOthersValue not in variants):
                variants.append(self.mOthersValue)
            if (self.mDefaultValue is not False and
                    self.mDefaultValue not in variants):
                variants.append(self.mDefaultValue)
            self.__initVariants(VariantSet(variants))
        used_names = set()
        if self.mVariantSet is not None:
            print >> rep_out, "=Variants(%d):" % len(self.mVariantSet)
            for name in self.mVariantSet:
                print >> rep_out, "\t%s: %d" % (name, self.mStat[name])
                used_names.add(name)
        if len(set(self.mStat.keys()) - used_names) > 0:
            print >> rep_out, "=Rest:"
            for name in sorted(self.mStat.keys()):
                if name in used_names:
                    continue
                print >> rep_out, "\t%s: %d" % (str(name), self.mStat[name])
        return not self.mBadValues and self.mVariantSet is not None

    def getVarTypeCode(self):
        return "enum"

    def hasDefault(self):
        return len(self.mDefaultVariant) == 0

    def hasOthers(self):
        return self.mOthersValue is not False

    def getVariantSet(self):
        return self.mVariantSet

    def testValues(self, values):
        try:
            if self.mChunker:
                values = self.mChunker.apply(values)
            if self.mAtomicMode and len(values) > 1:
                self.mBadValues["<?list?>"] += 1
                return False
            if len(values) == 0:
                self.mStat[self.mDefaultValue] += 1
                return True
            for val in values:
                self.mStat[val] += 1
            if (self.mVariantSet is not None and
                    self.mOthersValue is not False):
                for val in values:
                    if self.mVariantSet.indexOf(val) is None:
                        return False
            return True
        except Exception:
            self.mStat[repr(values)] += 1
            self.mBadValues = True
            return False

    def _convert(self, values):
        if self.mChunker:
            values = self.mChunker.apply(values)
        if len(values) == 0:
            return self.mDefaultVariant
        ret = self.mVariantSet.makeIdxSet(values)
        if self.mAtomicMode and len(ret) > 1:
            return {min(ret)}
        if len(ret) == 0:
            return self.mOthersVariant
        return ret

    def convert(self, values):
        ret = self._convert(values)
        if self.mAtomicMode:
            return list(ret)[0]
        return ret
