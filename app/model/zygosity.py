from app.config.a_config import AnfisaConfig
from app.filter.condition import ConditionMaker
from app.filter.unit import ComplexEnumSupport
from utils.variants import VariantSet
#===============================================
class ZygosityComplex(ComplexEnumSupport):
    def __init__(self, family_info, cond_env, descr):
        ComplexEnumSupport.__init__(self)
        self.mFamilyInfo = family_info
        self.mCondEnv = cond_env
        self.mIsOK = (self.mFamilyInfo is not None and
            len(self.mFamilyInfo) > 1)
        labels = AnfisaConfig.configOption("zygosity.cases")
        self.mCaseLabels =[labels[key]
            for key in ("homo_recess", "x_linked", "dominant", "compens")]
        self.mVariantSet = VariantSet(self.mCaseLabels)
        self.mConfig = descr.get("config", dict())
        self.mXCondition = None
        self.mFamNames = ["%s_%d" % (descr["name"], idx)
            for idx in range(len(self.mFamilyInfo))]
        self.mFamUnits = None
        assert ("size" not in descr or
            descr["size"] == len(self.mFamilyInfo))

    def iterFamNames(self):
        return iter(self.mFamNames)

    def getVariantSet(self):
        return self.mVariantSet

    def setupSubUnits(self, fam_units):
        self.mFamUnits = fam_units

    def setupXCond(self):
        self.mXCondition = self.mCondEnv.parse(
            self.mConfig.get("x_cond",
            ConditionMaker.condEnum("Chromosome", ["chrX"])))

    def isOK(self):
        return self.mIsOK

    def getFamUnit(self, idx):
        return self.mFamUnits[idx]

    def conditionZHomoRecess(self, problem_group):
        seq = []
        for idx, unit_h in enumerate(self.mFamUnits):
            if idx in problem_group:
                seq.append(self.mCondEnv.makeNumericCond(unit_h, [2, None]))
            else:
                seq.append(self.mCondEnv.makeNumericCond(unit_h, [0, 1]))
        return self.mCondEnv.joinAnd(seq)

    def conditionZDominant(self, problem_group):
        return self.mXCondition.negative().addAnd(
            self._conditionZDominant(problem_group))

    def conditionZXLinked(self, problem_group):
        return self.mXCondition.addAnd(
            self._conditionZDominant(problem_group))

    def _conditionZDominant(self, problem_group):
        seq = []
        for idx, unit_h in enumerate(self.mFamUnits):
            if idx in problem_group:
                seq.append(self.mCondEnv.makeNumericCond(unit_h, [1, None]))
            else:
                seq.append(self.mCondEnv.makeNumericCond(unit_h, [0, 0]))
        return self.mCondEnv.joinAnd(seq)

    def conditionZCompens(self, problem_group):
        seq = []
        for idx, unit_h in enumerate(self.mFamUnits):
            if idx in problem_group:
                seq.append(self.mCondEnv.makeNumericCond(unit_h, [0, 0]))
            else:
                seq.append(self.mCondEnv.makeNumericCond(unit_h, [1, None]))
        return self.mCondEnv.joinAnd(seq)

    def iterComplexCriteria(self, context, variants = None):
        if variants is None or self.mCaseLabels[0] in variants:
            yield self.mCaseLabels[0], self.conditionZHomoRecess(context)
        if variants is None or self.mCaseLabels[1] in variants:
            yield self.mCaseLabels[1], self.conditionZXLinked(context)
        if variants is None or self.mCaseLabels[2] in variants:
            yield self.mCaseLabels[2], self.conditionZDominant(context)
        if variants is None or self.mCaseLabels[3] in variants:
            yield self.mCaseLabels[3], self.conditionZCompens(context)

    def makeStat(self, index, condition, repr_context = None):
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
        ret.append(self.collectComplexStat(index, condition, p_group))
        return ret

    def parseCondition(self, cond_info):
        if not self.mIsOK:
            return self.mCondEnv.getCondNone()

        assert cond_info[0] == "zygosity"
        unit_name, p_group, filter_mode, variants = cond_info[1:]
        assert filter_mode != "ONLY"
        assert len(variants) > 0

        if p_group is None:
            p_group = self.mFamilyInfo.getAffectedGroup()
        return self.makeComplexCondition(filter_mode, variants, p_group)

    def processInstr(self, parser, ast_args, op_mode, variants):
        if len(ast_args) > 1:
            parser.errorIt(ast_args[1], "Extra argument not expected")
        if len(ast_args) == 0:
            p_group = self.mFamilyInfo.getAffectedGroup()
        else:
            p_group = parser.processIntSet(ast_args[0])
        return ["zygosity", self.getName(),
            sorted(p_group), op_mode, variants]
