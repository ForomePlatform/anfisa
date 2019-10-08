#===============================================
class FamilyInfo:
    def __init__(self, samples, proband_id = None):
        self.mMembers = sorted(samples.values(),
            key = lambda it: it["id"])
        if proband_id is None:
            for it in self.mMembers:
                if it["id"].endswith("a1"):
                    proband_id = it["id"]
        for idx, it in enumerate(self.mMembers):
            if it["id"] == proband_id:
                if idx > 0:
                    del self.mMembers[idx]
                    self.mMembers.insert(0, it)
                break
        assert self.mMembers[0]["id"] == proband_id

        self.mIds, self.mNames, self.mAffectedGroup = [], [], []
        self.mIdMap = dict()
        self.mMaleSet = set()
        for idx, it in enumerate(self.mMembers):
            self.mIds.append(it["id"])
            self.mNames.append(it["name"])
            self.mIdMap[it["id"]] = idx
            if it["affected"]:
                self.mAffectedGroup.append(idx)
            if it["sex"] == 1:
                self.mMaleSet.add(idx)
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

    def groupHasMales(self, problem_group):
        return len(self.mMaleSet & set(problem_group)) > 0
