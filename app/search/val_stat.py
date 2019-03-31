from collections import Counter

#===============================================
class NumDiapStat:
    def __init__(self):
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

    def result(self):
        return [self.mMin, self.mMax, self.mCntDef, self.mCntUndef]

#===============================================
class EnumStat:
    def __init__(self, variant_set):
        self.mVariantSet = variant_set
        self.mStat = Counter()

    def isDefined(self):
        for cnt in self.mStat.values():
            if cnt > 0:
                return True
        return False

    def regValues(self, values, count = 1):
        if not values:
            return
        for val in values:
            if not(0 <= val < len(self.mVariantSet)):
                continue
            assert 0 <= val < len(self.mVariantSet)
            self.mStat[val] += count

    def result(self):
        rep_list = []
        for idx, variant in enumerate(iter(self.mVariantSet)):
            rep_list.append([variant, self.mStat.get(idx, 0)])
        return [rep_list]
