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
    def __init__(self, variant_set, detailed = False):
        self.mVariantSet = variant_set
        self.mStat = Counter()
        self.mGroupStat = None
        if detailed:
            self.mGroupStat = Counter()
            self.mCurGroupNo = None
            self.mGroupSet = set()

    def isDefined(self):
        for cnt in self.mStat.values():
            if cnt > 0:
                return True
        return False

    def flushGroup(self):
        for val in self.mGroupSet:
            self.mGroupStat[val] += 1
        self.mGroupSet = set()

    def regValues(self, values, count = 1, group_no = None):
        if not values:
            return
        if group_no is not None and group_no != self.mCurGroupNo:
            self.mCurGroupNo = group_no
            self.flushGroup()

        for val in values:
            if not(0 <= val < len(self.mVariantSet)):
                continue
            assert 0 <= val < len(self.mVariantSet)
            self.mStat[val] += count
            if self.mGroupStat is not None:
                self.mGroupSet.add(val)

    def result(self):
        if self.mGroupStat is not None:
            self.flushGroup()
        rep_list = []
        for idx, variant in enumerate(iter(self.mVariantSet)):
            info = [variant, self.mStat.get(idx, 0)]
            if self.mGroupStat is not None:
                info.append(self.mGroupStat.get(idx, 0))
            rep_list.append(info)
        return [rep_list]
