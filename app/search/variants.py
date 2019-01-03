#===============================================
class VariantSet:
    @classmethod
    def create(cls, variants):
        if variants is None:
            return None
        return cls(variants)

    def __init__(self, variants):
        self.mVariants = variants
        self.mVarDict = {variant: idx
            for idx, variant in enumerate(self.mVariants)}

    def __iter__(self):
        return iter(self.mVariants)

    def __len__(self):
        return len(self.mVariants)

    def makeIdxSet(self, variants):
        idx_set = set()
        for var in variants:
            pos = self.mVarDict.get(var)
            if pos is not None:
                idx_set.add(pos)
        return idx_set

    def makeValueSet(self, idx_set):
        return {self.mVariants[pos] for pos in idx_set}

    def indexOf(self, variant):
        return self.mVarDict.get(variant)

    def getValue(self, idx_no):
        return self.mVariants[idx_no]

    def getVariants(self):
        return self.mVariants[:]

