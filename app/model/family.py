#===============================================
class FamilyInfo:
    def __init__(self, samples):
        self.mMembers = sorted(samples.values(),
            key = lambda it: it["id"])
        for idx, it in enumerate(self.mMembers):
            if it["id"].endswith("a1"):
                if idx > 0:
                    del self.mMembers[idx]
                    self.mMembers.insert(0, it)
                break
        assert self.mMembers[0]["id"].endswith("a1")
        self.mIds, self.mNames, self.mAffectedGroup = [], [], []
        self.mIdMap = dict()
        for idx, it in enumerate(self.mMembers):
            self.mIds.append(it["id"])
            self.mNames.append(it["name"])
            self.mIdMap[it["id"]] = idx
            if it["affected"]:
                self.mAffectedGroup.append(idx)
        self.mTrioSeq = []
        for idx, it in enumerate(self.mMembers):
            idx_father = self.mIdMap.get(it.get("father"))
            if idx_father is None:
                continue
            idx_mother = self.mIdMap.get(it.get("mother"))
            if idx_mother is not None:
                trio_name = "Proband" if idx == 0 else it["id"]
                self.mTrioSeq.append(
                    (trio_name, idx, idx_father, idx_mother))

    def __len__(self):
        return len(self.mMembers)

    def __getitem__(self, idx):
        return self.mMembers[idx]

    def iterIds(self):
        return iter(self.mIds)

    def getNames(self):
        return self.mNames

    def getAffectedGroup(self):
        return self.mAffectedGroup

    def getTrioSeq(self):
        return self.mTrioSeq
