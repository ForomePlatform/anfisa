import logging
from app.config.a_config import AnfisaConfig
from app.filter.condition import ConditionMaker
from app.filter.unit import Unit
from .xl_cond import XL_Condition, XL_NumCondition
#===============================================
class XL_Unit(Unit):
    def __init__(self, dataset_h, descr, unit_kind = None):
        Unit.__init__(self, descr, unit_kind)
        self.mDruidKind = descr["kind"]
        self.mDataSet = dataset_h

    def getDS(self):
        return self.mDataSet

    def getDruidKind(self):
        return self.mDruidKind

    @staticmethod
    def create(dataset_h, descr):
        if descr["kind"] == "zygosity":
            ret = XL_ZygosityUnit(dataset_h, descr)
            return None if ret.isDummy() else ret
        if descr["kind"] in {"long", "float"}:
            return XL_NumUnit(dataset_h, descr)
        ret = XL_EnumUnit(dataset_h, descr)
        if ret.isDummy():
            return None
        return ret

#===============================================
class XL_NumUnit(XL_Unit):
    def __init__(self, dataset_h, descr):
        XL_Unit.__init__(self, dataset_h, descr)
        self.getDS().getCondEnv().addNumUnit(self)

    def evalStat(self, condition):
        name_cnt = "_cnt_%d" % self.getNo()
        name_min = "_min_%d" % self.getNo()
        name_max = "_max_%d" % self.getNo()
        druid_agent = self.getDS().getDruidAgent()
        query = {
            "queryType": "timeseries",
            "dataSource": druid_agent.normDataSetName(self.getDS().getName()),
            "granularity": druid_agent.GRANULARITY,
            "descending": "true",
            "aggregations": [
                { "type": "count", "name": name_cnt,
                    "fieldName": self.getName()},
                { "type": "%sMin" % self.getDruidKind(),
                    "name": name_min,
                    "fieldName": self.getName()},
                { "type": "%sMax" % self.getDruidKind(),
                    "name": name_max,
                    "fieldName": self.getName()}],
            "intervals": [ druid_agent.INTERVAL ]}
        if condition is not None:
            cond_repr = condition.getDruidRepr()
            if cond_repr is False:
                return [None, None, 0]
            if cond_repr is not None:
                query["filter"] = cond_repr
        rq = druid_agent.call("query", query)
        assert len(rq) == 1
        return [rq[0]["result"][nm] for nm in
            (name_min, name_max, name_cnt)]

    def makeStat(self, condition, repr_context = None):
        ret = self.prepareStat();
        vmin, vmax, count = self.evalStat(condition)
        if count == 0:
            vmin, vmax = None, None
        return ret + [vmin, vmax, count, 0]

#===============================================
class XL_EnumUnit(XL_Unit):
    def __init__(self, dataset_h, descr):
        XL_Unit.__init__(self, dataset_h, descr,
            "status" if descr.get("atomic") else "enum")
        self.mVariants = [info[0]
            for info in descr["variants"]]
        self.mAccumCount = sum([info[1]
            for info in descr["variants"]])
        self.getDS().getCondEnv().addEnumUnit(self)

    def isDummy(self):
        return len(self.mVariants) < 1 or self.mAccumCount == 0

    def evalStat(self, condition):
        druid_agent = self.getDS().getDruidAgent()
        query = {
            "queryType": "topN",
            "dataSource": druid_agent.normDataSetName(self.getDS().getName()),
            "dimension": self.getName(),
            "threshold": len(self.mVariants) + 5,
            "metric": "count",
            "granularity": druid_agent.GRANULARITY,
            "aggregations": [{
                "type": "count", "name": "count",
                "fieldName": self.getName()}],
            "intervals": [ druid_agent.INTERVAL ]}
        if condition is not None:
            cond_repr = condition.getDruidRepr()
            if cond_repr is False:
                return []
            if cond_repr is not None:
                query["filter"] = cond_repr
        rq = druid_agent.call("query", query)
        if len(rq) != 1:
            logging.error("Got problem with xl_unit %s: %d" %
                (self.getName(), len(rq)))
            if len(rq) == 0:
                return [[var, 0] for var in self.mVariants]

        assert len(rq) == 1
        counts = dict()
        for rec in rq[0]["result"]:
            counts[rec[self.getName()]] = rec["count"]
        return [[var, counts.get(var, 0)]
            for var in self.mVariants]

    def makeStat(self, condition, repr_context = None):
        ret = self.prepareStat();
        ret.append(self.evalStat(condition))
        return ret

#===============================================
class XL_ZygosityUnit(XL_Unit):
    def __init__(self, dataset_h, descr):
        XL_Unit.__init__(self, dataset_h, descr)
        if descr.get("family") and self.getDS().getFamilyInfo() is None:
            self.getDS()._setFamilyInfo(descr["family"])

        self._setScreened(self.getDS().getApp().hasRunOption("no-custom"))
        self.mIsOK = (self.getDS().getFamilyInfo() is not None and
            len(self.getDS().getFamilyInfo()) > 1)
        self.mLabels = AnfisaConfig.configOption("zygosity.cases")
        self.mConfig = descr.get("config", dict())
        self.mXCondition = None
        self.getDS().getCondEnv().addSpecialUnit(self)

    def setup(self):
        self.mXCondition = self.getDS().getCondEnv().parse(
            self.mConfig.get("x_cond",
            ConditionMaker.condEnum("Chromosome", ["chrX"])))

    def isDummy(self):
        return not self.mIsOK

    def conditionZHomoRecess(self, problem_group):
        seq = []
        for idx in range(len(self.getDS().getFamilyInfo())):
            dim_name = "%s_%d" % (self.getName(), idx)
            if idx in problem_group:
                seq.append(XL_NumCondition(dim_name, [2, None]))
            else:
                seq.append(XL_NumCondition(dim_name, [None, 1]))
        return XL_Condition.joinAnd(seq)

    def conditionZDominant(self, problem_group):
        return self.mXCondition.negative().addAnd(
            self._conditionZDominant(problem_group))

    def conditionZXLinked(self, problem_group):
        return self.mXCondition.addAnd(
            self._conditionZDominant(problem_group))

    def _conditionZDominant(self, problem_group):
        seq = []
        for idx in range(len(self.getDS().getFamilyInfo())):
            dim_name = "%s_%d" % (self.getName(), idx)
            if idx in problem_group:
                seq.append(XL_NumCondition(dim_name, [1, None]))
            else:
                seq.append(XL_NumCondition(dim_name, [None, 0]))
        return XL_Condition.joinAnd(seq)

    def conditionZCompens(self, problem_group):
        seq = []
        for idx in range(len(self.getDS().getFamilyInfo())):
            dim_name = "%s_%d" % (self.getName(), idx)
            if idx in problem_group:
                seq.append(XL_NumCondition(dim_name, [None, 0]))
            else:
                seq.append(XL_NumCondition(dim_name, [1, None]))
        return XL_Condition.joinAnd(seq)

    def _iterCritSeq(self, p_group):
        yield (self.mLabels["homo_recess"],
            self.conditionZHomoRecess(p_group))
        yield (self.mLabels["x_linked"],
            self.conditionZXLinked(p_group))
        yield (self.mLabels["dominant"],
            self.conditionZDominant(p_group))
        yield (self.mLabels["compens"],
            self.conditionZCompens(p_group))

    def makeStat(self, condition, repr_context = None):
        assert self.mIsOK
        ret = self.prepareStat()
        ret[-1]["family"] = self.getDS().getFamilyInfo().getTitles()
        ret[-1]["affected"] = self.getDS().getFamilyInfo().getAffectedGroup()
        if repr_context is None or "problem_group" not in repr_context:
            p_group = self.getDS().getFamilyInfo().getAffectedGroup()
        else:
            p_group = {m_idx if 0 <= m_idx < len(self.getDS().getFamilyInfo())
                else None for m_idx in repr_context["problem_group"]}
            if None in p_group:
                p_group.remove(None)
        if len(p_group) == 0:
            return ret + [sorted(p_group), None]
        stat = []
        for name, z_condition in self._iterCritSeq(p_group):
            cur_cond = z_condition
            if condition is not None:
                cur_cond = condition.addAnd(cur_cond)
            stat.append([name, self.getDS().evalTotalCount(cur_cond)])
        return ret + [sorted(p_group), stat]

    def parseCondition(self, cond_info):
        if not self.mIsOK:
            return self.getDS().getCondEnv().getCondNone()

        assert cond_info[0] == "zygosity"
        unit_name, p_group, filter_mode, variants = cond_info[1:]
        assert unit_name == self.getName()
        assert filter_mode != "ONLY"
        assert len(variants) > 0

        if p_group is None:
            p_group = self.getDS().getFamilyInfo().getAffectedGroup()

        singles = []
        for name, z_condition in self._iterCritSeq(p_group):
            if name in variants:
                singles.append(z_condition)
        assert len(singles) == len(variants)

        if filter_mode == "NOT":
            return XL_Condition.joinAnd([cond.negative() for cond in singles])
        if filter_mode == "AND":
            return XL_Condition.joinAnd(singles)
        return XL_Condition.joinOr(singles)

    def processInstr(self, parser, ast_args, op_mode, variants):
        if len(ast_args) > 1:
            parser.errorIt(ast_args[1], "Extra argument not expected")
        if len(ast_args) == 0:
            p_group = self.getDS().getFamilyInfo().getAffectedGroup()
        else:
            p_group = parser.processIntSet(ast_args[0])
        return ["zygosity", self.getName(),
            sorted(p_group), op_mode, variants]
