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
from app.filter.unit import ComplexEnumSupport
from utils.variants import VariantSet
#===============================================
class ZygosityComplex(ComplexEnumSupport):
    def __init__(self, family_info, descr):
        ComplexEnumSupport.__init__(self)
        self.mFamilyInfo = family_info
        self.mIsOK = (self.mFamilyInfo is not None
            and 1 < len(self.mFamilyInfo) <= 10)
        labels = AnfisaConfig.configOption("zygosity.cases")
        self.mCaseLabels = [labels[key]
            for key in ("homo_recess", "x_linked", "dominant", "compens")]
        self.mVariantSet = VariantSet(self.mCaseLabels)
        self.mConfig = descr.get("config", dict())
        self.mXCondition = None
        self.mFamNames = ["%s_%d" % (descr["name"], idx)
            for idx in range(len(self.mFamilyInfo))]
        self.mFamUnits = None
        assert ("size" not in descr
            or descr["size"] == len(self.mFamilyInfo))

    def iterFamNames(self):
        return iter(self.mFamNames)

    def getVariantSet(self):
        return self.mVariantSet

    def setupSubUnits(self, fam_units):
        self.mFamUnits = fam_units

    def setupXCond(self):
        x_unit_name = self.mConfig.get("x_unit", "Chromosome")
        self.mXCondition = self.getCondEnv().makeEnumCond(
            self.getDS().getUnit(x_unit_name),
            self.mConfig.get("x_values", ["chrX"]))

    def isOK(self):
        return self.mIsOK

    def validateCondition(self, cond_info):
        assert cond_info[0] == "zygosity"
        unit_name, p_group, filter_mode, variants = cond_info[1:]
        return (filter_mode in {"", "OR", "AND", "NOT"}
            and len(variants) > 0 and (p_group is None or len(p_group) > 0))

    def getFamUnit(self, idx):
        return self.mFamUnits[idx]

    def conditionZHomoRecess(self, problem_group):
        cond = self._conditionZHomoRecess(problem_group)
        if self.mFamilyInfo.groupHasMales(problem_group):
            return self.mXCondition.negative().addAnd(cond)
        return cond

    def _conditionZHomoRecess(self, problem_group):
        seq = []
        for idx, unit_h in enumerate(self.mFamUnits):
            if idx in problem_group:
                seq.append(self.getCondEnv().makeNumericCond(unit_h, [2, None]))
            else:
                seq.append(self.getCondEnv().makeNumericCond(unit_h, [0, 1]))
        return self.getCondEnv().joinAnd(seq)

    def conditionZXLinked(self, problem_group):
        if self.mFamilyInfo.groupHasMales(problem_group):
            return self.mXCondition.addAnd(
                self._conditionZHomoRecess(problem_group))
        return self.getCondEnv().getCondNone()

    def conditionZDominant(self, problem_group):
        seq = []
        for idx, unit_h in enumerate(self.mFamUnits):
            if idx in problem_group:
                seq.append(self.getCondEnv().makeNumericCond(unit_h, [1, None]))
            else:
                seq.append(self.getCondEnv().makeNumericCond(unit_h, [0, 0]))
        return self.getCondEnv().joinAnd(seq)

    def conditionZCompens(self, problem_group):
        seq = []
        for idx, unit_h in enumerate(self.mFamUnits):
            if idx in problem_group:
                seq.append(self.getCondEnv().makeNumericCond(unit_h, [0, 0]))
            else:
                seq.append(self.getCondEnv().makeNumericCond(unit_h, [1, None]))
        return self.getCondEnv().joinAnd(seq)

    def iterComplexCriteria(self, context, variants = None):
        problem_group = context["p_group"]
        if variants is None or self.mCaseLabels[0] in variants:
            yield self.mCaseLabels[0], self.conditionZHomoRecess(problem_group)
        if variants is None or self.mCaseLabels[1] in variants:
            yield self.mCaseLabels[1], self.conditionZXLinked(problem_group)
        if variants is None or self.mCaseLabels[2] in variants:
            yield self.mCaseLabels[2], self.conditionZDominant(problem_group)
        if variants is None or self.mCaseLabels[3] in variants:
            yield self.mCaseLabels[3], self.conditionZCompens(problem_group)

    def makeStat(self, ds_h, condition, repr_context = None):
        assert self.mIsOK
        ret = self.prepareStat()
        ret[1]["family"] = self.mFamilyInfo.getNames()
        ret[1]["affected"] = self.mFamilyInfo.getAffectedGroup()
        if repr_context is None or "problem_group" not in repr_context:
            p_group = self.mFamilyInfo.getAffectedGroup()
        else:
            p_group = {m_idx if 0 <= m_idx < len(self.mFamilyInfo)
                else None for m_idx in repr_context["problem_group"]}
            if None in p_group:
                p_group.remove(None)
        ret.append(sorted(p_group))
        if len(p_group) == 0:
            return ret + [None]
        ret.append(self.collectComplexStat(ds_h, condition,
            {"p_group": p_group}))
        return ret

    def parseCondition(self, cond_info):
        if not self.mIsOK:
            return self.getCondEnv().getCondNone()

        assert cond_info[0] == "zygosity"
        unit_name, p_group, filter_mode, variants = cond_info[1:]
        assert len(variants) > 0

        if p_group is None:
            p_group = self.mFamilyInfo.getAffectedGroup()
        return self.makeComplexCondition(filter_mode, variants,
            {"p_group": p_group})

    def processInstr(self, parser, ast_args, op_mode, variants):
        if len(ast_args) > 1:
            parser.errorIt(ast_args[1], "Extra argument not expected")
        if len(ast_args) == 0:
            p_group = self.mFamilyInfo.getAffectedGroup()
        else:
            p_group = parser.processIntSet(ast_args[0])
        return ["zygosity", self.getName(),
            sorted(p_group), op_mode, variants]
