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
class ZygositySupport:
    def __init__(self,  ds_h):
        self.mEvalSpace = ds_h.getEvalSpace()
        self.mFamilyInfo = ds_h.getFamilyInfo()
        self.mXCondition = None

    def setupX(self, x_unit, x_values):
        self.mXCondition = self.mEvalSpace.makeEnumCond(
            self.mEvalSpace.getUnit(x_unit), x_values)

    def getFamilyInfo(self):
        return self.mFamilyInfo

    def getAffectedGroup(self):
        return self.mFamilyInfo.getAffectedGroup()

    def getIds(self):
        return self.mFamilyInfo.getIds()

    def filter(self, p_group):
        return self.mFamilyInfo.filter(p_group)

    def getTrioSeq(self):
        return self.mFamilyInfo.getTrioSeq()

    def conditionScenario(self, scenario):
        seq = []
        for zyg_bounds, seq_samples in scenario.items():
            for idx in self.mFamilyInfo.ids2idxset(seq_samples):
                seq.append(self.mEvalSpace.makeNumericCond(
                    self.mEvalSpace.getZygUnit(idx), zyg_bounds = zyg_bounds))
        return self.mEvalSpace.joinAnd(seq)

    def conditionZHomoRecess(self, problem_group):
        cond = self._conditionZHomoRecess(problem_group)
        if self.mFamilyInfo.groupHasMales(problem_group):
            return self.mXCondition.negative().addAnd(cond)
        return cond

    def _conditionZHomoRecess(self, problem_group):
        return self.conditionScenario({
            "2": problem_group,
            "0-1": self.mFamilyInfo.complement(problem_group)})

    def conditionZXLinked(self, problem_group):
        if self.mFamilyInfo.groupHasMales(problem_group):
            return self.mXCondition.addAnd(
                self._conditionZHomoRecess(problem_group))
        return self.mEvalSpace.getCondNone()

    def conditionZDominant(self, problem_group):
        return self.conditionScenario({
            "1-2": problem_group,
            "0": self.mFamilyInfo.complement(problem_group)})

    def conditionZCompens(self, problem_group):
        return self.conditionScenario({
            "0": problem_group,
            "1-2": self.mFamilyInfo.complement(problem_group)})

