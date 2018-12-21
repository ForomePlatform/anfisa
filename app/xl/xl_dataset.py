import codecs, json
from threading import Lock

from .rest import RestAgent
from .druid import DruidCfg
from .xl_unit import XL_Unit
from .xl_filters import XL_Filter
from .xl_setup import XL_Setup
#===============================================
class XL_Dataset:

    def __init__(self, descr_path, name, query_url, mongo_ds = None):
        with codecs.open(descr_path, "r", encoding = "utf-8") as inp:
            self.mDescr = json.loads(inp.read())
        self.mName = name
        self.mQueryAgent = RestAgent(query_url)
        self.mDataSource = self.mDescr["datasource"]
        self.mMongoDS = mongo_ds
        self.mLock  = Lock()
        self.mUnits = []
        for descr in self.mDescr["units"]:
            xl_unit = XL_Unit.create(self, descr)
            if xl_unit is not None:
                self.mUnits.append(xl_unit)
        self.mTotal = self.evalTotalCount()
        self.mFilterCache = dict()
        if self.mMongoDS is not None:
            for filter_name, conditions in self.mMongoDS.getFilters():
                if not XL_Setup.hasFilter(filter_name):
                        self.mFilterCache[filter_name] = conditions

    def __enter__(self):
        self.mLock.acquire()
        return self

    def __exit__(self, type, value, traceback):
        self.mLock.release()

    def getName(self):
        return self.mName

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
        if not XL_Setup.hasFilter(flt_name):
            with self:
                if op == "UPDATE":
                    self.mMongoDS.setFilter(flt_name, conditions)
                    self.cacheFilter(flt_name, conditions)
                    filter_name = flt_name
                elif op == "DROP":
                    self.mMongoDS.dropFilter(flt_name)
                    self.dropFilter(flt_name)
                else:
                    assert False
        return filter_name

    def makeStatReport(self, filter_name, conditions, instr):
        if instr is not None:
            filter_name = self._evalInstr(
                filter_name, conditions, instr)
        if XL_Setup.hasFilter(filter_name):
            conditions = XL_Setup.getFilterConditions()
        else:
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
        for filter_name in XL_Setup.getFilterNames():
            ret.append([filter_name, True, True])
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

    def getDSNote(self, note = None):
        if note is not None:
            self.mMongoDS.setDSNote(note)
        return self.mMongoDS.getDSNote()

    def getJSonObj(self):
        return {"name": self.mName, "note": self.getDSNote()}
