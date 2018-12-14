from .druid import DruidCfg

#===============================================
class XL_Unit:
    def __init__(self, xl_ds, descr):
        self.mDataset = xl_ds
        self.mType  = descr["type"]
        self.mName  = descr["name"]
        self.mTitle = descr["title"]
        self.mNo    = descr["no"]
        self.mVGroup = descr.get("vgroup")

    def getDS(self):
        return self.mDataset

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
    def create(xl_ds, descr):
        if descr["type"] in {"long", "float"}:
            return XL_NumUnit(xl_ds, descr)
        else:
            return XL_EnumUnit(xl_ds, descr)

    def _prepareStat(self):
        return [self.mType, {
            "name": self.mName,
            "title": self.mTitle,
            "vgroup": self.mVGroup}]

#===============================================
class XL_NumUnit(XL_Unit):
    def __init__(self, xl_ds, descr):
        XL_Unit.__init__(self, xl_ds, descr)

    def evalStat(self, filter = None):
        name_cnt = "_cnt_%d" % self.getNo()
        name_min = "_min_%d" % self.getNo()
        name_max = "_max_%d" % self.getNo()
        query = {
            "queryType": "timeseries",
            "dataSource": self.getDS().getDataSource(),
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
        rq = self.getDS().getQueryAgent().call(query)
        assert len(rq) == 1
        return [rq[0]["result"][nm] for nm in
            (name_min, name_max, name_cnt)]

    def report(self, output):
        XL_Unit.report(self, output)
        vmin, vmax, count = self.evalStat()
        print >> output, "\tdiap:", vmin, vmax, "count=", count

    def makeStat(self, filter):
        ret = self._prepareStat();
        vmin, vmax, count = self.evalStat(filter)
        #TRF: count_undef!!!
        return ret + [vmin, vmax, count, 0]

#===============================================
class XL_EnumUnit(XL_Unit):
    def __init__(self, xl_ds, descr):
        XL_Unit.__init__(self, xl_ds, descr)
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
            "dataSource": self.getDS().getDataSource(),
            "dimension": self.getName(),
            "threshold": len(self.mVariants),
            "metric": "count",
            "granularity": DruidCfg.GRANULARITY,
            "aggregations": [{
                "type": "count", "name": "count",
                "fieldName": self.getName()}],
            "intervals": [ DruidCfg.INTERVAL ]}
        rq = self.getDS().getQueryAgent().call(query)
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

    def makeStat(self, filter):
        ret = self._prepareStat();
        ret.append(self.evalStat(filter))
        return ret
