from collections import Counter

#===============================================
class BoolStat:
    def __init__(self, names):
        self.mNames = names
        self.mStat = Counter()

    def isDefined(self):
        return sum(self.mStat.values()) > 0

    def regValue(self, val):
        self.mStat[not not val] += 1

    def dump(self, names):
        return ["bool", self.mNames, self.mStat[True], self.mStat[False]]

#===============================================
class NumDiapStat:
    def __init__(self, type_name, names):
        self.mTypeName = type_name
        self.mNames = names
        self.mMin, self.mMax = None, None
        self.mCntDef = 0
        self.mCntUndef = 0

    def isDefined(self):
        return self.mCntDef > 0

    def regValue(self, val):
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

    def dump(self):
        return [self.mTypeName, self.mNames,
            self.mMin, self.mMax, self.mCntDef, self.mCntUndef]

#===============================================
class EnumStat:
    def __init__(self, variant_set, names, enum_type):
        self.mVariantSet = variant_set
        self.mNames = names
        self.mEnumType = enum_type
        self.mStat = Counter()

    def isDefined(self):
        for cnt in self.mStat.values():
            if cnt > 0:
                return True
        return False

    def regValues(self, values, count = 1):
        for val in values:
            if not(0 <= val < len(self.mVariantSet)):
                continue
            assert 0 <= val < len(self.mVariantSet)
            self.mStat[val] += count

    def dump(self):
        rep_list = []
        for idx, variant in enumerate(iter(self.mVariantSet)):
            rep_list.append([variant, self.mStat.get(idx, 0)])
        return ["enum", self.mNames, rep_list]
