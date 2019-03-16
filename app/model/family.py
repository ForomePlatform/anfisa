#===============================================
class FamilyInfo:
    def __init__(self, members, titles, affected_group, proband_rel):
        self.mMembers = members
        self.mTitles = titles
        self.mAffectedGroup = affected_group
        self.mProbandRel = proband_rel
        self.mMem2Idx = {member:idx
            for idx, member in enumerate(self.mMembers)}

    def __len__(self):
        return len(self.mMembers)

    def getMembers(self):
        return self.mMembers

    def getTitles(self):
        return self.mTitles

    def getAffectedGroup(self):
        return self.mAffectedGroup

    def getProbandRel(self):
        return self.mProbandRel

    def getMemberIdx(self, member):
        return self.mMem2Idx[member]

    def dump(self):
        return {
            "members": self.mMembers,
            "titles": self.mTitles,
            "affected": self.mAffectedGroup,
            "proband_rel": self.mProbandRel}

    @staticmethod
    def load(family_info):
        if family_info is None:
            return None
        return FamilyInfo(*[family_info[key]
            for key in ("members", "titles", "affected", "proband_rel")])

    @staticmethod
    def detect(samples):
        members = sorted(samples.keys())
        titles = members[:]
        affected_group = []
        for idx, member_id in enumerate(members):
            if samples[member_id]["affected"]:
                affected_group.append(idx)
        proband_info = samples[members[0]]
        if "father" in proband_info and "mother" in proband_info:
            proband_rel = [members.index(proband_info[key])
                for key in ("name", "father", "mother")]
        else:
            proband_rel = None
        return FamilyInfo(members, titles, affected_group, proband_rel)
