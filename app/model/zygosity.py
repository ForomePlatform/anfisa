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

from app.config.a_config import AnfisaConfig
from app.eval.var_unit import FunctionUnit
from utils.variants import VariantSet

#===============================================
class InheritanceUnit(FunctionUnit):
    sCaseKeys   = ("homo_recess", "x_linked", "dominant", "compens")
    sCaseLabels = [AnfisaConfig.configOption("zygosity.cases")[key]
        for key in sCaseKeys]
    sVariansSet = VariantSet(sCaseLabels)

    @staticmethod
    def makeIt(ds_h, descr, x_unit, x_values,
            before = None, after = None):
        unit_h = InheritanceUnit(ds_h, descr, x_unit, x_values)
        ds_h.getEvalSpace()._insertUnit(unit_h, before = before, after = after)

    def __init__(self, ds_h, descr, x_unit, x_values):
        FunctionUnit.__init__(self, ds_h.getEvalSpace(), descr,
            sub_kind = "inheritance-z", parameters = ["problem_group"])

        assert ds_h.testRequirements({"ZYG"})
        self.mFamilyInfo = ds_h.getFamilyInfo()
        self.mXCondition = self.getEvalSpace().makeEnumCond(
            self.getEvalSpace().getUnit(x_unit), x_values)
        assert ("size" not in descr
            or descr["size"] == len(self.mFamilyInfo))

    def getVariantSet(self):
        return self.sVariantSet

    def conditionZHomoRecess(self, problem_group):
        cond = self._conditionZHomoRecess(problem_group)
        if self.mFamilyInfo.groupHasMales(problem_group):
            return self.mXCondition.negative().addAnd(cond)
        return cond

    def _conditionZHomoRecess(self, problem_group):
        seq = []
        for idx, unit_h in enumerate(self.getEvalSpace().iterZygUnits()):
            if idx in problem_group:
                seq.append(self.getEvalSpace().makeNumericCond(
                    unit_h, zyg_bounds = "2"))
            else:
                seq.append(self.getEvalSpace().makeNumericCond(
                    unit_h, zyg_bounds = "0-1"))
        return self.getEvalSpace().joinAnd(seq)

    def conditionZXLinked(self, problem_group):
        if self.mFamilyInfo.groupHasMales(problem_group):
            return self.mXCondition.addAnd(
                self._conditionZHomoRecess(problem_group))
        return self.getEvalSpace().getCondNone()

    def conditionZDominant(self, problem_group):
        seq = []
        for idx, unit_h in enumerate(self.getEvalSpace().iterZygUnits()):
            if idx in problem_group:
                seq.append(self.getEvalSpace().makeNumericCond(
                    unit_h, zyg_bounds = "1-2"))
            else:
                seq.append(self.getEvalSpace().makeNumericCond(
                    unit_h, zyg_bounds = "0"))
        return self.getEvalSpace().joinAnd(seq)

    def conditionZCompens(self, problem_group):
        seq = []
        for idx, unit_h in enumerate(self.getEvalSpace().iterZygUnits()):
            if idx in problem_group:
                seq.append(self.getEvalSpace().makeNumericCond(
                    unit_h, zyg_bounds = "0"))
            else:
                seq.append(self.getEvalSpace().makeNumericCond(
                    unit_h, zyg_bounds = "1-2"))
        return self.getEvalSpace().joinAnd(seq)

    def iterComplexCriteria(self, context, variants = None):
        if context is None:
            return
        problem_group = context["problem_group"]
        if variants is None or self.sCaseLabels[0] in variants:
            yield self.sCaseLabels[0], self.conditionZHomoRecess(problem_group)
        if variants is None or self.sCaseLabels[1] in variants:
            yield self.sCaseLabels[1], self.conditionZXLinked(problem_group)
        if variants is None or self.sCaseLabels[2] in variants:
            yield self.sCaseLabels[2], self.conditionZDominant(problem_group)
        if variants is None or self.sCaseLabels[3] in variants:
            yield self.sCaseLabels[3], self.conditionZCompens(problem_group)

    def makeInfoStat(self, eval_h, point_no):
        ret_handle = self.prepareStat()
        ret_handle["family"] = self.mFamilyInfo.getNames()
        ret_handle["affected"] = self.mFamilyInfo.getAffectedGroup()
        return ret_handle

    def makeParamStat(self, condition, parameters, eval_h, point_no):
        ret_handle = self.prepareStat()
        if parameters is None or "problem_group" not in parameters:
            p_group = self.mFamilyInfo.getAffectedGroup()
        else:
            p_group = (set(parameters["problem_group"])
                & self.mFamilyInfo.getIdSet())
        ret_handle["problem_group"] = sorted(p_group)
        if len(p_group) > 0:
            self.collectComplexStat(ret_handle, condition,
                {"problem_group": p_group})
        else:
            ret_handle["variants"] = None
            ret_handle["err"] = "Problem group is empty"
        return ret_handle

    def locateContext(self, cond_data, eval_h):
        p_group = cond_data[2].get("problem_group")
        if p_group is None:
            p_group = self.mFamilyInfo.getAffectedGroup()
        else:
            extra_names = (set(p_group) - set(self.mFamilyInfo.getNames()))
            if len(extra_names) > 0:
                eval_h.operationError(cond_data, "No sample(s) registered: "
                    + ' '.join(sorted(extra_names)))
            return None
        if len(p_group) == 0:
            eval_h.operationError(cond_data, "Problem group is empty")
            return None
        if len(cond_data[4]) == 0:
            eval_h.operationError(cond_data,
                "%s: empty set of variants" % self.getName())
            return None
        return {"problem_group": set(p_group)}

    def validateArgs(self, func_args):
        if "problem_group" in func_args:
            if not isinstance(func_args["problem_group"], list):
                return "Problem group expected in form of set or list"
        return None
