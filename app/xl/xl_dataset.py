import codecs, json
from .rest import RestAgent
from .xl_unit import XL_Unit

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
            self.mUnits.append(XL_Unit.create(self, descr))

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
        #TRF: rewrite it
        op, q, flt_name = instr.partition('/')
        if not self.mLegend.hasFilter(flt_name):
            with self:
                if op == "UPDATE":
                    self.mMongoWS.setFilter(flt_name, conditions)
                    self.mIndex.cacheFilter(flt_name, conditions)
                    filter_name = flt_name
                elif op == "DROP":
                    self.mMongoWS.dropFilter(flt_name)
                    self.mIndex.dropFilter(flt_name)
                else:
                    assert False
        return filter_name

    def _getFilterList(self):
        #TRF: write it!!!
        return []

    def _prepareFilter(self, filter_name, conditions):
        #TRF: write it!!!
        return None

    def makeStatReport(self, filter_name, conditions, instr):
        if instr is not None:
            filter_name = self._evalInstr(filter_name, conditions, instr)
        filter_data = self._prepareFilter(filter_name, conditions)
        report = {
            "stat-list": [unit.makeStat(filter_data)
                for unit in self.mUnits],
            "filter-list": self._getFilterList(),
            "cur-filter": filter_name}
        if (filter_name and filter_name in self.mFilterCache and
                not filter_name.startswith('_')):
            report["conditions"] = self.mFilterCache[filter_name][0]
        return report
