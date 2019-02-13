import logging
#===============================================
class XL_Unit:
    def __init__(self, xl_ds, descr):
        self.mDataSet = xl_ds
        self.mUnitKind  = descr["kind"]
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

    def report(self, output):
        print >> output, "Unit", self.mName, "kind=", self.mUnitKind

    @staticmethod
    def create(xl_ds, descr):
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

    def evalStat(self, filter = None):
        name_cnt = "_cnt_%d" % self.getNo()
        name_min = "_min_%d" % self.getNo()
        name_max = "_max_%d" % self.getNo()
        druid_agent = self.getDS().getDruidAgent()
        query = {
            "queryType": "timeseries",
            "dataSource": self.getDS().getName(),
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
        if filter is not None:
            query["filter"] = filter
        rq = druid_agent.call("query", query)
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
        self.mVariants = [info[0]
            for info in descr["variants"]]
        self.mAccumCount = sum([info[1]
            for info in descr["variants"]])

    def isDummy(self):
        return len(self.mVariants) < 1 or self.mAccumCount == 0

    def evalStat(self, filter = None):
        druid_agent = self.getDS().getDruidAgent()
        query = {
            "queryType": "topN",
            "dataSource": self.getDS().getName(),
            "dimension": self.getName(),
            "threshold": len(self.mVariants),
            "metric": "count",
            "granularity": druid_agent.GRANULARITY,
            "aggregations": [{
                "type": "count", "name": "count",
                "fieldName": self.getName()}],
            "intervals": [ druid_agent.INTERVAL ]}
        if filter is not None:
            query["filter"] = filter
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
