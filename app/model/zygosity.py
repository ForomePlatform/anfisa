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
import logging

from app.config.a_config import AnfisaConfig
from app.eval.condition import ZYG_BOUNDS_VAL
#===============================================
class ZygositySupport:
    sMaxGeneCompCount = AnfisaConfig.configOption("max.gene.comp.count")

    def __init__(self,  ds_h):
        self.mEvalSpace = ds_h.getEvalSpace()
        self.mFamilyInfo = ds_h.getFamilyInfo()
        self.mXCondition = None
        self.mApproxInfo = []
        self.mGeneUnits = dict()

    def setupX(self, x_unit, x_values):
        self.mXCondition = self.mEvalSpace.makeEnumCond(
            self.mEvalSpace.getUnit(x_unit), x_values)

    def regGeneApprox(self, approx_key, unit_name, approx_title):
        self.mGeneUnits[approx_key] = self.mEvalSpace.getUnit(unit_name)
        assert self.mGeneUnits[approx_key] is not None, (
            "Bad gene unit: " + unit_name)
        self.mApproxInfo.append([approx_key, approx_title])

    def getFamilyInfo(self):
        return self.mFamilyInfo

    def getApproxInfo(self):
        return self.mApproxInfo

    def getAffectedGroup(self):
        return self.mFamilyInfo.getAffectedGroup()

    def getNames(self):
        return self.mFamilyInfo.getNames()

    def filter(self, p_group):
        return self.mFamilyInfo.filter(p_group)

    def getTrioSeq(self):
        return self.mFamilyInfo.getTrioSeq()

    def getGeneUnit(self, approx_mode):
        return self.mGeneUnits[approx_mode]

    def normalizeApprox(self,  approx_mode):
        if not approx_mode:
            return self.mApproxInfo[0][0]
        if approx_mode in self.mGeneUnits:
            return approx_mode
        return False

    def hasXLinked(self):
        return self.mFamilyInfo.groupHasMales()

    #=========================
    # Scenarios
    #=========================
    def conditionScenario(self, scenario):
        seq = []
        for zyg_bounds, seq_samples in scenario.items():
            for idx in self.mFamilyInfo.names2idxset(seq_samples):
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

    #=========================
    # Compound requests
    #=========================
    def makeCompoundRequest(self, approx_mode,
            actual_condition, c_rq, unit_name):
        set_genes = None
        cond_scenario_seq = []
        for min_count, scenario in c_rq:
            cond_scenario = self.conditionScenario(scenario)
            if cond_scenario.getCondType() == "null":
                continue
            if min_count < 1:
                continue
            cond_scenario_seq.append(cond_scenario)
            stat_info = self.mGeneUnits[approx_mode].makeStat(
                actual_condition.addAnd(cond_scenario), None)
            genes = set()
            for info in stat_info["variants"]:
                gene, count = info[:2]
                if count >= min_count:
                    genes.add(gene)
            if set_genes is not None:
                set_genes &= genes
            else:
                set_genes = genes
            if len(set_genes) == 0:
                return self.mEvalSpace.getCondNone()
        if set_genes is None:
            return self.mEvalSpace.getCondNone()
        if len(set_genes) >= self.sMaxGeneCompCount:
            return None
        logging.info("Eval compound genes for %s: %d" %
            (unit_name,  len(set_genes)))

        return self.mEvalSpace.joinAnd([
            actual_condition,
            self.mEvalSpace.makeEnumCond(
                self.mGeneUnits[approx_mode], sorted(set_genes)),
            self.mEvalSpace.joinOr(cond_scenario_seq)])

    @classmethod
    def emptyRequest(cls, request):
        for rq_var in request:
            if rq_var[0] > 0:
                for val in rq_var[1].values():
                    if val:
                        return False
        return True

    #=========================
    # Validation
    #=========================
    @classmethod
    def validateScenario(cls,  scenario):
        if not isinstance(scenario, dict):
            return "Scenario expected in form of dict"
        bad_keys = set(scenario.keys()) - set(ZYG_BOUNDS_VAL.keys())
        if len(bad_keys) > 0:
            return ("Improper keys in scenario: "
                + " ".join(sorted(bad_keys)))
        for val in scenario.values():
            if (not isinstance(val, list)
                    or not all(isinstance(v,  str) for v in val)):
                return ("Values in scenario dict "
                    + "should be lists of identifiers")
        return None

    @classmethod
    def validateRequest(cls,  request):
        if not isinstance(request, list):
            return "Request expected in form of list"
        for idx, rq_var in enumerate(request):
            if (not isinstance(rq_var, list) or len(rq_var) != 2
                    or not isinstance(rq_var[0], int)):
                return "Invalid request record no %d" % (idx + 1)
            err_msg = cls.validateScenario(rq_var[1])
            if err_msg:
                return err_msg + (" in record no %d" % (idx + 1))
        return None
