import logging
from app.model.a_config import AnfisaConfig
from xl_cond import XL_Condition, XL_NumCondition
#===============================================
class XL_Unit:
    def __init__(self, xl_ds, descr, unit_kind = None):
        self.mDataSet = xl_ds
        self.mUnitKind  = descr["kind"] if unit_kind is None else unit_kind
        self.mName  = descr["name"]
        self.mTitle = descr["title"]
        self.mNo    = descr["no"]
        self.mVGroup = descr.get("vgroup")

    def getDS(self):
        return self.mDataSet

    def getUnitKind(self):
        return self.mUnitKind

    def getName(self):
        return self.mName

    def getTitle(self):
        return self.mTitle

    def getVGroup(self):
        return self.mVGroup

    def getNo(self):
        return self.mNo

    def getParseSupport(self):
        return (None, None)

    @staticmethod
    def create(xl_ds, descr):
        if descr["kind"] == "zygosity":
            ret = XL_ZygosityUnit(xl_ds, descr)
            return None if ret.isDummy() else ret
        if descr["kind"] in {"long", "float"}:
            return XL_NumUnit(xl_ds, descr)
        ret = XL_EnumUnit(xl_ds, descr)
        if ret.isDummy():
            return None
        return ret

    def _prepareStat(self):
        return [self.mUnitKind, {
            "name": self.mName,
            "title": self.mTitle,
            "vgroup": self.mVGroup}]

#===============================================
class XL_NumUnit(XL_Unit):
    def __init__(self, xl_ds, descr):
        XL_Unit.__init__(self, xl_ds, descr)

    def evalStat(self, context = None):
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
                { "type": "%sMin" % self.getUnitKind(),
                    "name": name_min,
                    "fieldName": self.getName()},
                { "type": "%sMax" % self.getUnitKind(),
                    "name": name_max,
                    "fieldName": self.getName()}],
            "intervals": [ druid_agent.INTERVAL ]}
        if context and  context.get("cond") is not None:
            query["filter"] = context["cond"].getDruidRepr()
        rq = druid_agent.call("query", query)
        assert len(rq) == 1
        return [rq[0]["result"][nm] for nm in
            (name_min, name_max, name_cnt)]

    def makeStat(self, context = None):
        ret = self._prepareStat();
        vmin, vmax, count = self.evalStat(context)
        #TRF: count_undef!!!
        return ret + [vmin, vmax, count, 0]

#===============================================
class XL_EnumUnit(XL_Unit):
    def __init__(self, xl_ds, descr):
        XL_Unit.__init__(self, xl_ds, descr,
            "status" if descr.get("atomic") else "enum")
        self.mVariants = [info[0]
            for info in descr["variants"]]
        self.mAccumCount = sum([info[1]
            for info in descr["variants"]])

    def isDummy(self):
        return len(self.mVariants) < 1 or self.mAccumCount == 0

    def evalStat(self, context = None):
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
        if context and  context.get("cond") is not None:
            query["filter"] = context["cond"].getDruidRepr()
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

    def makeStat(self, context):
        ret = self._prepareStat();
        ret.append(self.evalStat(context))
        return ret

#===============================================
class XL_ZygosityUnit(XL_Unit):
    def __init__(self, xl_ds, descr):
        XL_Unit.__init__(self, xl_ds, descr)
        self.mFamily = descr["family"]
        if not self.isDummy():
            self.mFamMap = {member:idx
                for idx, member in enumerate(self.mFamily)}
        self.mLabels = AnfisaConfig.configOption("zygosity.cases")

    def isDummy(self):
        return not self.mFamily or len(self.mFamily) < 2

    def getFamilyInfo(self):
        return self.mFamily

    def getParseSupport(self):
        return ("zygosity", self.parseZCondition)

    def conditionZHomoRecess(self, problem_group):
        seq = []
        for idx in range(len(self.mFamily)):
            dim_name = "%s_%d" % (self.getName(), idx)
            if idx in problem_group:
                # z >= 2
                seq.append(XL_NumCondition(dim_name, False, 2))
            else:
                # z <= 1
                seq.append(XL_NumCondition(dim_name, True, 1))
        return XL_Condition.joinAnd(seq)

    def conditionZDominant(self, problem_group):
        seq = []
        for idx in range(len(self.mFamily)):
            dim_name = "%s_%d" % (self.getName(), idx)
            if idx in problem_group:
                # z >= 1
                seq.append(XL_NumCondition(dim_name, False, 1))
            else:
                # z <= 0
                seq.append(XL_NumCondition(dim_name, True, 0))
        return XL_Condition.joinAnd(seq)

    def conditionZCompens(self, problem_group):
        seq = []
        for idx in range(len(self.mFamily)):
            dim_name = "%s_%d" % (self.getName(), idx)
            if idx in problem_group:
                # z <= 0
                seq.append(XL_NumCondition(dim_name, True, 0))
            else:
                # z >= 1
                seq.append(XL_NumCondition(dim_name, False, 1))
        return XL_Condition.joinAnd(seq)

    def _evalOneCrit(self, z_condition, context):
        condition = z_condition
        if context and "cond" in context:
            condition = z_condition.addAnd(context["cond"])
        return self.getDS.evalTotalCount({"cond": condition})

    def _iterCritSeq(self, p_group):
        yield (self.mLabels["homo_recess"],
            self.conditionZHomoRecess(p_group))
        yield (self.mLabels["dominant"],
            self.conditionZDominant(p_group))
        yield (self.mLabels["compens"],
            self.conditionZCompens(p_group))

    def makeStat(self, context = None):
        ret = self._prepareStat() + [self.mFamily]
        if context is None or "problem_group" not in context:
            return ret + [[], None]
        p_group = {m_idx if 0 <= m_idx < len(self.mFamily) else None
            for m_idx in context["problem_group"]}
        if None in p_group:
            p_group.remove(None)
        if (len(p_group) == 0 or len(p_group) == len(self.mFamily)):
            return ret + [sorted(p_group), None]
        stat = []
        for name, z_condition in self._iterCritSeq(p_group):
            condition = z_condition
            if "cond" in context:
                condition = z_condition.addAnd(context["cond"])
            stat.append([name,
                self.getDS().evalTotalCount({"cond": condition})])
        return ret + [sorted(p_group), stat]

    def parseZCondition(self, cond_info):
        assert cond_info[0] == "zygosity"
        unit_name, p_group, filter_mode, variants = cond_info[1:]
        assert unit_name == self.getName()
        assert filter_mode != "ONLY"
        assert len(variants) > 0

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
