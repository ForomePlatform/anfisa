from app.config.a_config import AnfisaConfig
from app.filter.condition import ConditionMaker
from utils.variants import VariantSet
#===============================================
class ZygosityComplex:
    def __init__(self, family_info, cond_env, descr):
        self.mFamilyInfo = family_info
        self.mCondEnv = cond_env
        self.mIsOK = (self.mFamilyInfo is not None and
            len(self.mFamilyInfo) > 1)
        labels = AnfisaConfig.configOption("zygosity.cases")
        self.mVariantSet = VariantSet([labels[key]
            for key in ("homo_recess", "x_linked", "dominant", "compens")])
        self.mConfig = descr.get("config", dict())
        self.mXCondition = None
        if not self.mIsOK:
            return
        self.mFamNames = ["%s_%d" % (descr["name"], idx)
            for idx in range(len(self.mFamilyInfo.getMembers()))]
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
        if self.mXCondition.getCondEnv().getKind() == "ws":
            print ("XCond:", len(self.mXCondition.getBitArray()))

    def isOK(self):
        return self.mIsOK

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

    def _iterCritSeq(self):
        for label, func in zip(self.getVariantSet(),
                [self.conditionZHomoRecess, self.conditionZXLinked,
                self.conditionZDominant, self.conditionZCompens]):
            yield (label, func)

    def makeStat(self, index, condition, repr_context = None):
        assert self.mIsOK
        ret = self.prepareStat()
        ret[1]["family"] = self.mFamilyInfo.getTitles()
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
        stat = []
        for name, z_condition_f in self._iterCritSeq():
            cur_cond = z_condition_f(p_group)
            if condition is not None:
                cur_cond = condition.addAnd(cur_cond)
            stat.append([name, index.evalTotalCount(cur_cond)])
        return ret + [stat]

    def parseCondition(self, cond_info):
        if not self.mIsOK:
            return self.mCondEnv.getCondNone()

        assert cond_info[0] == "zygosity"
        unit_name, p_group, filter_mode, variants = cond_info[1:]
        assert filter_mode != "ONLY"
        assert len(variants) > 0

        if p_group is None:
            p_group = self.mFamilyInfo.getAffectedGroup()

        singles = []
        for name, z_condition_f in self._iterCritSeq():
            if name in variants:
                singles.append(z_condition_f(p_group))
        assert len(singles) == len(variants)

        if filter_mode == "NOT":
            return self.mCondEnv.joinAnd(
                [cond.negative() for cond in singles])
        if filter_mode == "AND":
            return self.mCondEnv.joinAnd(singles)
        return self.mCondEnv.joinOr(singles)

    def processInstr(self, parser, ast_args, op_mode, variants):
        if len(ast_args) > 1:
            parser.errorIt(ast_args[1], "Extra argument not expected")
        if len(ast_args) == 0:
            p_group = self.mFamilyInfo.getAffectedGroup()
        else:
            p_group = parser.processIntSet(ast_args[0])
        return ["zygosity", self.getName(),
            sorted(p_group), op_mode, variants]
