import json

from app.model.rest_api import RestAPI
from app.model.dataset import DataSet
from .xl_unit import XL_Unit
from .xl_filters import XL_Filter
#===============================================
class XLDataset(DataSet):
    def __init__(self, data_vault, dataset_info, dataset_path):
        DataSet.__init__(self, data_vault, dataset_info, dataset_path)
        self.mMongoDS = (self.mDataVault.getApp().getMongoConnector().
            getDSAgent(self.getMongoName()))
        self.mDruidAgent = self.getDataVault().getApp().getDruidAgent()

        self.mUnits = []
        for unit_data in self.getFltSchema():
            xl_unit = XL_Unit.create(self, unit_data)
            if xl_unit is not None:
                self.mUnits.append(xl_unit)
        self.mFilterCache = dict()
        if self.mMongoDS is not None:
            for filter_name, conditions in self.mMongoDS.getFilters():
                if not self.mDruidAgent.hasStdFilter(filter_name):
                        self.mFilterCache[filter_name] = conditions

    def getDruidAgent(self):
        return self.mDruidAgent

    def report(self, output):
        print >> output, "Report for datasource", self.getName()
        for unit in self.mUnits:
            unit.report(output)

    def filterOperation(self, filter_name, conditions, instr):
        if instr is None:
            return filter_name
        op, q, flt_name = instr.partition('/')
        if not self.mDruidAgent.hasStdFilter(flt_name):
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

    def cacheFilter(self, filter_name, conditions):
        self.mFilterCache[filter_name] = conditions

    def dropFilter(self, filter_name):
        if filter_name in self.mFilterCache:
            del self.mFilterCache[filter_name]

    def getFilterList(self):
        ret = []
        for filter_name in self.mDruidAgent.getStdFilterNames():
            ret.append([filter_name, True, True])
        for filter_name, flt_info in self.mFilterCache.items():
            if filter_name.startswith('_'):
                continue
            ret.append([filter_name, False, True])
        return sorted(ret)

    def evalTotalCount(self, filter):
        if filter is None:
            return self.getTotal()
        query = {
            "queryType": "timeseries",
            "dataSource": self.getName(),
            "granularity": self.mDruidAgent.GRANULARITY,
            "descending": "true",
            "aggregations": [
                { "type": "count", "name": "count",
                    "fieldName": "_ord"}],
            "intervals": [ self.mDruidAgent.INTERVAL ]}
        if filter is not None:
            query["filter"] = filter
        rq = self.mDruidAgent.call("query", query)
        assert len(rq) == 1
        return rq[0]["result"]["count"]

    def dump(self):
        return {
            "name": self.mName,
            "note": self.mMongoDS.getDSNote()}

    #===============================================
    @RestAPI.xl_request
    def rq__xl_filters(self, rq_args):
        filter_name = rq_args.get("filter")
        conditions = rq_args.get("conditions")
        if conditions:
            conditions = json.loads(conditions)
        filter_name = self.filterOperation(
            filter_name, conditions, rq_args.get("instr"))
        if self.mDruidAgent.hasStdFilter(filter_name):
            cond_seq = self.mDruidAgent.getStdFilterConditions()
        else:
            cond_seq = self.mFilterCache.get(filter_name, conditions)
        filter_data = XL_Filter.makeFilter(cond_seq)
        return {
            "total": self.getTotal(),
            "count": self.evalTotalCount(filter_data),
            "stat-list": [unit.makeStat(filter_data)
                for unit in self.mUnits],
            "filter-list": self.getFilterList(),
            "cur-filter": filter_name,
            "conditions": cond_seq}

    #===============================================
    @RestAPI.xl_request
    def rq__dsnote(self, rq_args):
        note = rq_args.get("note")
        if note is not None:
            with self:
                self.mMongoDS.setDSNote(note)
        return {
            "ds": self.getName(),
            "note": self.mMongoDS.getDSNote()}
