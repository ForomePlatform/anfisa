#import sys
import abc
from collections import Counter
#===============================================
class ValueConvertor:
    def __init__(self):
        pass

    def isAtomic(self):
        return True

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
        self.mStat = Counter()

    def setup(self, rep_out):
        print >> rep_out, (
            "True: %d, False: %d" % (self.mStat[True], self.mStat[False]))
        return True

    def getVarTypeCode(self):
        return "bool"

    def hasDefault(self):
        return True

    def testValues(self, values):
        if len(values) > 1:
            return False
        val = len(values) > 0 and values[0]
        self.mStat[val] += 1
        return True

    def convert(self, values):
        return {len(values) > 0 and values[0]}


#===============================================
class _NumericConvertor(ValueConvertor):
    def __init__(self, num_type, num_name,
            default_value = 0., diap = (0., 1.)):
        ValueConvertor.__init__(self)
        self.mNumType = num_type
        self.mNumName = num_name
        self.mDefaultValue = default_value
        if diap is not None:
            self.mMinValue, self.mMaxValue = diap
            assert (self.mDefaultValue is None or
                self.mMinValue <= self.mDefaultValue <= self.mMaxValue)
        else:
            self.mMinValue = None
        self.mStat = [None, None, 0]
        self.mBadValues = Counter()

    def setup(self, rep_out):
        print >> rep_out, "Min: %s, Max: %s" % (
            str(self.mStat[0]), str(self.mStat[1]))
        if self.mStat[2] > 0:
            print >> rep_out, "Undef: %d" % self.mStat[2]
        if len(self.mBadValues) > 0:
            print >> rep_out, "Bad values %d:" % len(self.mBadValues)
            for neg_cnt, val in sorted([(-cnt, val)
                    for val, cnt in self.mBadValues.items()])[:5]:
                print >> rep_out, "\t %s: %d" % (-neg_cnt, val)
            if len(self.mBadValues) > 5:
                print >> rep_out, "\t..."
        return self.mStat[0] is not None and len(self.mBadValues) == 0

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
            return False
        try:
            if len(values) == 0:
                val = self.mDefaultValue
            else:
                val = self.mNumType(values[0])
            if val is None:
                self.mStat[2] += 1
                return True
            if (self.mMinValue is not None and not
                    (self.mMinValue <= val <= self.mMaxValue)):
                self.mBadValues[str(val)] +=1
                return False
            if self.mStat[0] is None:
                self.mStat[0] = self.mStat[1] = val
            else:
                self.mStat[0] = min(self.mStat[0], val)
                self.mStat[1] = max(self.mStat[0], val)
            return True
        except Exception:
            self.mBadValues[str(values)] += 1
            return False

    def convert(self, values):
        if len(values) == 0:
            return self.mDefaultValue
        return {self.mNumType(values[0])}

#===============================================
class FloatConvertor(_NumericConvertor):
    def __init__(self, default_value = 0., diap = (0., 1.)):
        _NumericConvertor.__init__(self, float, "float", default_value, diap)

class IntConvertor(_NumericConvertor):
    def __init__(self, default_value = 0., diap = (0., 1.)):
        _NumericConvertor.__init__(self, int, "int", default_value, diap)

#===============================================
class EnumConvertor(ValueConvertor):
    def __init__(self, variants = None, atomic_mode = False, chunker = None,
            default_value = False, others_value = False):
        ValueConvertor.__init__(self)
        self.mVariantNames = None
        self.mVariantDict = None
        self.mAtomicMode = atomic_mode
        self.mChunker = chunker
        self.mDefaultValue = default_value
        self.mDefaultVariant = None
        self.mOthersValue = others_value
        self.mOthersVariant = None
        self.mStat = Counter()
        self.mBadValues = False
        if variants is not None:
            self.__initVariants(variants)

    def isAtomic(self):
        return self.mAtomicMode

    def __initVariants(self, variants):
        self.mVariantNames = variants
        self.mVariantDict = {name: idx
            for idx, name in enumerate(self.mVariantNames)}
        if (self.mDefaultValue is not False and
                self.mDefaultValue in variants):
            self.mDefaultVariant = variants.index(self.mDefaultValue)
        else:
            self.mDefaultValue = None
        if (self.mOthersValue is not False and
                self.mOthersValue in variants):
            self.mOthersValue = variants.index(self.mOthersValue)
        else:
            self.mOthersValue = None

    def setup(self, rep_out):
        if self.mBadValues:
            print >> rep_out, "=NOTE: Has bad values!"
        elif self.mVariantNames is None:
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
            self.__initVariants(variants)
        used_names = set()
        if self.mVariantNames is not None:
            print >> rep_out, "=Variants(%d):" % len(self.mVariantNames)
            for name in self.mVariantNames:
                print "\t%s: %d" % (name, self.mStat[name])
                used_names.add(name)
        if len(set(self.mStat.keys()) - used_names) > 0:
            print >> rep_out, "=Rest:"
            for name in sorted(self.mStat.keys()):
                if name in used_names:
                    continue
                print "\t%s: %d" % (str(name), self.mStat[name])
        return not self.mBadValues and self.mVariantNames is not None

    def getVarTypeCode(self):
        return "enum"

    def hasDefault(self):
        return self.mDefaultVariant is not False

    def hasOthers(self):
        return self.mOthersValue is not False

    def getVariants(self):
        return self.mVariantNames

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
            if (self.mVariantDict is not None and
                    self.mOthersValueis is False):
                for val in values:
                    if val not in self.mVariantDict:
                        return False
            return True
        except Exception:
            self.mStat[repr(values)] += 1
            self.mBadValues = True
            return False

    def convert(self, values):
        if self.mChunker:
            values = self.mChunker.apply()
        if len(values) == 0:
            return {self.mDefaultVariant}
        ret = set()
        for val in values:
            if val in self.mVariantDict:
                ret.add(self.mVariantDict[val])
            if self.mAtomicMode:
                break
        if len(ret) == 0:
            return {self.mOthersVariant}
        return ret
