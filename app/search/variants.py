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

    def makeStringSet(self, idx_set):
        ret = {self.mVarDict.get(pos) for pos in idx_set}
        if None in ret:
            ret.remove(None)
        return ret

    def indexOf(self, variant):
        return self.mVarDict.get(variant)
