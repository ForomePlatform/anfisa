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
from app.eval.var_unit import ComplexEnumUnit
from utils.variants import VariantSet

#===============================================
class ZygosityUnit(ComplexEnumUnit):
    sCaseKeys   = ("homo_recess", "x_linked", "dominant", "compens")
    sCaseLabels = [AnfisaConfig.configOption("zygosity.cases")[key]
        for key in sCaseKeys]
    sVariansSet = VariantSet(sCaseLabels)

    @staticmethod
    def makeIt(ds_h, descr, x_unit, x_values,
            before = None, after = None):
        unit_h = ZygosityUnit(ds_h, {
            "name": "Inheritance_Mode",
            "title": "Inheritance Mode",
            "vgroup": "Inheritance"}, x_unit, x_values)
        ds_h.getEvalSpace()._insertUnit(unit_h, before = before, after = after)

    def __init__(self, ds_h, descr, x_unit, x_values):
        ComplexEnumUnit.__init__(self, ds_h.getEvalSpace(), descr,
            unit_kind = "func", sub_kind = "trio-inheritance-z")

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
        problem_group = context["problem-group"]
        if variants is None or self.sCaseLabels[0] in variants:
            yield self.sCaseLabels[0], self.conditionZHomoRecess(problem_group)
        if variants is None or self.sCaseLabels[1] in variants:
            yield self.sCaseLabels[1], self.conditionZXLinked(problem_group)
        if variants is None or self.sCaseLabels[2] in variants:
            yield self.sCaseLabels[2], self.conditionZDominant(problem_group)
        if variants is None or self.sCaseLabels[3] in variants:
            yield self.sCaseLabels[3], self.conditionZCompens(problem_group)

    def makeStat(self, condition, repr_context):
        ret_handle = self.prepareStat()
        ret_handle["sub-kind"] = self.getSubKind()
        ret_handle["family"] = self.mFamilyInfo.getNames()
        ret_handle["affected"] = self.mFamilyInfo.getAffectedGroup()
        if repr_context is None or "problem-group" not in repr_context:
            p_group = self.mFamilyInfo.getAffectedGroup()
        else:
            p_group = (set(repr_context["problem-group"]) &
                self.mFamilyInfo.getIdSet())
        ret_handle["problem-group"] = sorted(p_group)
        if len(p_group) > 0:
            self.collectComplexStat(ret_handle, condition,
                {"problem-group": p_group})
        else:
            ret_handle["variants"] = None
        return ret_handle

    def locateContext(self, cond_data, eval_h):
        func_info = cond_data[2]
        assert func_info["sub-kind"] == self.getSubKind()
        p_group = func_info.get("problem-group")
        if p_group is None:
            p_group = self.mFamilyInfo.getAffectedGroup()
        return {"problem-group": set(p_group)}

    def validateCondition(self, cond_info, op_units):
        if (len(cond_info) != 5 or cond_info[0] != "func"
                or cond_info[1] != self.getName()):
            return False
        unit_name, func_info, filter_mode, variants = cond_info[1:]
        if not (filter_mode in {"", "OR", "AND", "NOT"}
                and isinstance(variants, list)):
            return False
        if func_info.get("sub-kind") != self.getSubKind():
            return False
        p_group = func_info.get("problem-group")
        return p_group is None or isinstance(p_group, list)

    def processAstNode(self, parser, ast_args, op_mode, variants):
        if len(ast_args) > 1:
            parser.errorIt(ast_args[1], "Extra argument not expected")
        if len(ast_args) == 0:
            p_group = self.mFamilyInfo.getAffectedGroup()
        else:
            p_group = parser.processIdSet(ast_args[0])
        return ["func", self.getName(), {
            "sub-kind": self.getSubKind(),
            "problem-group": sorted(p_group)}, op_mode, variants]
