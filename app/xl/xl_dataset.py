import codecs, json
from .rest import RestAgent
from .druid import DruidCfg
from .xl_unit import XL_Unit
from .xl_filters import XL_Filter

#===============================================
class XL_Dataset:
    def __init__(self, descr_path, name, title, query_url):
        with codecs.open(descr_path, "r", encoding = "utf-8") as inp:
            self.mDescr = json.loads(inp.read())
        self.mName = name
        self.mTitle = title
        self.mQueryAgent = RestAgent(query_url)
        self.mDataSource = self.mDescr["datasource"]
        self.mUnits = []
        for descr in self.mDescr["units"]:
            xl_unit = XL_Unit.create(self, descr)
            if xl_unit is not None:
                self.mUnits.append(xl_unit)
        self.mTotal = self.evalTotalCount()
        self.mFilterCache = dict()

    def getName(self):
        return self.mName

    def getTitle(self):
        return self.mTitle

    def getQueryAgent(self):
        return self.mQueryAgent

    def getDataSource(self):
        return self.mDataSource

    def report(self, output):
        print >> output, "Report for datasource", self.mDataSource
        for unit in self.mUnits:
            unit.report(output)

    def _evalInstr(self, filter_name, conditions, instr):
        op, q, flt_name = instr.partition('/')
        #if not self.mLegend.hasFilter(flt_name):
        #    with self:
        if op == "UPDATE":
            #self.mMongoWS.setFilter(flt_name, conditions)
            self.cacheFilter(flt_name, conditions)
            filter_name = flt_name
        elif op == "DROP":
            #self.mMongoWS.dropFilter(flt_name)
            self.dropFilter(flt_name)
        else:
            assert False
        return filter_name

    def makeStatReport(self, filter_name, conditions, instr):
        if instr is not None:
            filter_name = self._evalInstr(
                filter_name, conditions, instr)
        conditions = self.mFilterCache.get(filter_name, conditions)
        filter_data = XL_Filter.makeFilter(conditions)
        report = {
            "total": self.mTotal,
            "count": self.evalTotalCount(filter_data),
            "stat-list": [unit.makeStat(filter_data)
                for unit in self.mUnits],
            "filter-list": self.getFilterList(),
            "cur-filter": filter_name,
            "conditions": conditions}
        return report

    def cacheFilter(self, filter_name, conditions):
        self.mFilterCache[filter_name] = conditions

    def dropFilter(self, filter_name):
        if filter_name in self.mFilterCache:
            del self.mFilterCache[filter_name]

    def getFilterList(self):
        ret = []
        for filter_name, flt_info in self.mFilterCache.items():
            if filter_name.startswith('_'):
                continue
            ret.append([filter_name, False, True])
        return sorted(ret)

    def evalTotalCount(self, filter = None):
        query = {
            "queryType": "timeseries",
            "dataSource": self.mDataSource,
            "granularity": DruidCfg.GRANULARITY,
            "descending": "true",
            "aggregations": [
                { "type": "count", "name": "count",
                    "fieldName": "_ord"}],
            "intervals": [ DruidCfg.INTERVAL ]}
        if filter is not None:
            query["filter"] = filter
        rq = self.mQueryAgent.call(query)
        assert len(rq) == 1
        return rq[0]["result"]["count"]
