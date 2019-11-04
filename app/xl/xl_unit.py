import logging
from app.filter.unit import Unit
from app.model.zygosity import ZygosityComplex
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

    def isDetailed(self):
        return False

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
class XL_ZygosityUnit(XL_Unit, ZygosityComplex):
    def __init__(self, dataset_h, descr):
        XL_Unit.__init__(self, dataset_h, descr)
        ZygosityComplex.__init__(self,
            dataset_h.getFamilyInfo(), dataset_h.getCondEnv(), descr)

        fam_units = []
        for fam_name in self.iterFamNames():
            fam_units.append(
                self.getDS().getCondEnv().addMetaNumUnit(fam_name))
        self.getDS().getCondEnv().addSpecialUnit(self)
        self.setupSubUnits(fam_units)

    def setup(self):
        self.setupXCond()

    def isDummy(self):
        return not self.isOK()

    def makeStat(self, condition, repr_context = None):
        return ZygosityComplex.makeStat(self, self.getDS(),
            condition, repr_context)

