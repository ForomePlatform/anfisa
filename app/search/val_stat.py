from collections import Counter

#===============================================
class BoolStat:
    def __init__(self):
        self.mStat = Counter()

    def isDefined(self):
        return sum(self.mStat.values()) > 0

    def regValue(self, val):
        self.mStat[val] += 1

    def report(self, rep_out):
        print >> rep_out, (
            "True: %d, False: %d" % (self.mStat[True], self.mStat[False]))

    def getJSon(self, name):
        return ["bool", name, self.mStat[True], self.mStat[False]]

#===============================================
class NumDiapStat:
    def __init__(self, type_name):
        self.mTypeName = type_name
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

    def report(self, rep_out):
        print >> rep_out, "Min: %s, Max: %s" % (
            str(self.mMin), str(self.mMax))
        if self.mCntUndef > 0:
            print >> rep_out, "Undef: %d" % self.mStat[2]

    def getJSon(self, name):
        return [self.mTypeName, name,
            self.mMin, self.mMax, self.mCntDef, self.mCntUndef]

#===============================================
class EnumStat:
    def __init__(self, variants):
        self.mVariants = variants
        self.mStat = Counter()

    def isDefined(self):
        for cnt in self.mStat.values():
            if cnt > 0:
                return True
        return False

    def regValues(self, values, count = 1):
        for val in values:
            if not(0 <= val < len(self.mVariants)):
                continue
            assert 0 <= val < len(self.mVariants)
            self.mStat[val] += count

    def report(self, rep_out):
        #TRF: write it later
        assert False

    def getJSon(self, name):
        rep_list = []
        for idx, variant in enumerate(self.mVariants):
            cnt = self.mStat.get(idx)
            if cnt:
                rep_list.append([variant, cnt])
        return ["enum", name, rep_list]
