#  Copyright (c) 2019. Partners HealthCare and other members of
#  Forome Association
#
#  Developed by Sergey Trifonov based on contributions by Joel Krier,
#  Michael Bouzinier, Shamil Sunyaev and other members of Division of
#  Genetics, Brigham and Women's Hospital
#
#  Licensed under the Apache License, Version 2.0 (the "License");
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
#
#        http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.
#

#===============================================
class FamilyInfo:
    def __init__(self, meta_record):
        self.mMembers = sorted(meta_record["samples"].values(),
            key = lambda it: it["id"]) if "samples" in meta_record else []
        proband_id = meta_record.get("proband")
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
        assert (len(self.mMembers) == 0
            or self.mMembers[0]["id"] == proband_id), (
            "Family setup: first member" + self.mMembers[0]["id"]
            + "should be proband: " + proband_id)

        self.mIds, self.mNames, self.mAffectedGroup = [], [], []
        self.mIdMap = dict()
        self.mNameMap = dict()
        self.mMaleSet = set()
        for idx, it in enumerate(self.mMembers):
            self.mIds.append(it["id"])
            self.mNames.append(it["name"])
            self.mIdMap[it["id"]] = idx
            self.mNameMap[it["name"]] = idx
            if it["affected"]:
                self.mAffectedGroup.append(it["name"])
            if it["sex"] == 1:
                self.mMaleSet.add(it["name"])
        self.mTrioSeq = []
        for idx, it in enumerate(self.mMembers):
            idx_father = self.mIdMap.get(it.get("father"))
            if idx_father is None:
                continue
            idx_mother = self.mIdMap.get(it.get("mother"))
            if idx_mother is not None:
                trio_id = "Proband" if idx == 0 else it["id"]
                self.mTrioSeq.append((trio_id, self.mNames[idx],
                    self.mNames[idx_father], self.mNames[idx_mother]))

        self.mCohortList = None
        self.mCohortMap = None
        if "cohorts" in meta_record:
            self.mCohortList = []
            self.mCohortMap = dict()
            for item in meta_record["cohorts"]:
                self.mCohortList.append(item["name"])
                for it_id in item["members"]:
                    assert it_id not in self.mCohortMap, (
                        "Sample in two cohorts: %s, %s" %
                        (self.mCohortMap[it_id], item["name"]))
                    assert it_id in self.mIdMap, (
                        "Cohort sample is not registered: " + it_id)
                    self.mCohortMap[it_id] = item["name"]

    def prepareModes(self):
        ret = set()
        trio_seq = self.getTrioSeq()
        if trio_seq:
            ret.add("trio")
            if trio_seq[0][0] == "Proband":
                ret.add("trio_base")
                if len(self) == 3:
                    ret.add("trio_pure")
        if self.mCohortList is not None:
            ret.add("COHORTS")
        else:
            ret.add("PROBAND")

    def __len__(self):
        return len(self.mMembers)

    def __getitem__(self, idx):
        return self.mMembers[idx]

    def getIds(self):
        return self.mIds

    def complement(self, p_group):
        return set(self.mNames) - set(p_group)

    def filter(self, p_group):
        return set(self.mNames) & set(p_group)

    def getNames(self):
        return self.mNames

    def getAffectedGroup(self):
        return self.mAffectedGroup

    def getMaleSet(self):
        return self.mMaleSet

    def getTrioSeq(self):
        return self.mTrioSeq

    def groupHasMales(self, problem_group = None):
        if problem_group is None:
            return len(self.mMaleSet) > 0
        return len(self.mMaleSet & set(problem_group)) > 0

    def getCohortList(self):
        return self.mCohortList

    def getCohortMap(self):
        return self.mCohortMap

    def id2cohort(self, it_id):
        if self.mCohortMap is not None:
            return self.mCohortMap.get(it_id)
        return None

    def sampleIdx(self, name):
        return self.mNameMap.get(name)

    def names2idxset(self, names):
        if not names:
            return []
        return sorted({self.mNameMap[nm] for nm in names})

    def idxset2names(self, idx_set):
        if not idx_set:
            return idx_set
        return sorted({self.mNames[idx] for idx in idx_set})
