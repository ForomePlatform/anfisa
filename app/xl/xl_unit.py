from .druid import DruidCfg

#===============================================
class XL_Unit:
    def __init__(self, xl_legend, descr):
        self.mLegend = xl_legend
        self.mType  = descr["type"]
        self.mName  = descr["name"]
        self.mTitle = descr["title"]
        self.mNo    = descr["no"]
        self.mVGroup = descr.get("vgroup")

    def getLegend(self):
        return self.mLegend

    def getUnitType(self):
        return self.mType

    def getName(self):
        return self.mName

    def getTitle(self):
        return self.mTitle

    def getVGroup(self):
        return self.mVGroup

    def getNo(self):
        return self.mNo

    def report(self, output):
        print >> output, "Unit", self.mName, "tp=", self.mType

    @staticmethod
    def create(legend, descr):
        if descr["type"] in {"long", "float"}:
            return XL_NumUnit(legend, descr)
        else:
            return XL_EnumUnit(legend, descr)

#===============================================
class XL_NumUnit(XL_Unit):
    def __init__(self, legend, descr):
        XL_Unit.__init__(self, legend, descr)

    def evalStat(self, filter = None):
        name_cnt = "_cnt_%d" % self.getNo()
        name_min = "_min_%d" % self.getNo()
        name_max = "_max_%d" % self.getNo()
        query = {
            "queryType": "timeseries",
            "dataSource": self.getLegend().getDataSource(),
            "granularity": DruidCfg.GRANULARITY,
            "descending": "true",
            "aggregations": [
                { "type": "count", "name": name_cnt,
                    "fieldName": self.getName()},
                { "type": "%sMin" % self.getUnitType(),
                    "name": name_min,
                    "fieldName": self.getName()},
                { "type": "%sMax" % self.getUnitType(),
                    "name": name_max,
                    "fieldName": self.getName()}],
            "intervals": [ DruidCfg.INTERVAL ]}
        if filter is not None:
            query["filter"] = filter
        rq = self.getLegend().getQueryAgent().call(query)
        assert len(rq) == 1
        return {key: rq[0]["result"][nm] for key, nm in
            (("count", name_cnt),
            ("min", name_min), ("max", name_max))}

    def report(self, output):
        XL_Unit.report(self, output)
        ret = self.evalStat()
        print >> output, "\tdiap:", \
            ret["min"], ret["max"], "count=", ret["count"]

#===============================================
class XL_EnumUnit(XL_Unit):
    def __init__(self, legend, descr):
        XL_Unit.__init__(self, legend, descr)
        self.mVariants = descr["variants"]
        self.mVarDict = {var: idx
            for idx, var in enumerate(self.mVariants)}

    def _recKeyOrd(self, rec):
        return self.mVarDict.get(rec[0])

    def _recKeyTop(self, rec):
        return -rec[1]

    def evalStat(self, filter = None):
        query = {
            "queryType": "topN",
            "dataSource": self.getLegend().getDataSource(),
            "dimension": self.getName(),
            "threshold": len(self.mVariants),
            "metric": "count",
            "granularity": DruidCfg.GRANULARITY,
            "aggregations": [{
                "type": "count", "name": "count",
                "fieldName": self.getName()}],
            "intervals": [ DruidCfg.INTERVAL ]}
        rq = self.getLegend().getQueryAgent().call(query)
        assert len(rq) == 1
        ret = [[rec[self.getName()], rec["count"]]
            for rec in rq[0]["result"]]
        return sorted(ret, key = self._recKeyTop)

    def report(self, output):
        XL_Unit.report(self, output)
        stat = self.evalStat()
        if len(stat) < 5:
            cnt = len(stat)
        else:
            cnt = 3
        for idx in range(cnt):
            var, count = stat[idx]
            print >> output, "\t%s: %d" % (var, count)
        if cnt < len(stat):
            print >> output, "\t\t...and %d more" % (len(stat) - cnt)

