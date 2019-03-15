import json
from md5 import md5

from app.model.a_config import AnfisaConfig
from app.model.rest_api import RestAPI
from app.model.dataset import DataSet
from .xl_unit import XL_Unit
from .xl_cond import XL_Condition
from .decision import DecisionTree
from .xl_conf import defineDefaultDecisionTree
from .tree_repr import cmpTrees
#===============================================
class XLDataset(DataSet):
    def __init__(self, data_vault, dataset_info, dataset_path):
        DataSet.__init__(self, data_vault, dataset_info, dataset_path)
        self.mMongoDS = (self.getDataVault().getApp().getMongoConnector().
            getDSAgent(self.getMongoName()))
        self.mDruidAgent = self.getDataVault().getApp().getDruidAgent()
        self.mParseContext = dict()

        self.mUnits = []
        for unit_data in self.getFltSchema():
            xl_unit = XL_Unit.create(self, unit_data)
            if xl_unit is not None:
                self.mUnits.append(xl_unit)
                field, parse_f = xl_unit.getParseSupport()
                if field:
                    assert field not in self.mParseContext
                    self.mParseContext[field] = parse_f
        self.mFilterCache = dict()
        if self.mMongoDS is not None:
            for f_name, conditions, time_label in self.mMongoDS.getFilters():
                if self.mDruidAgent.goodOpFilterName(f_name):
                    self.cacheFilter(f_name, conditions, time_label)

    def getDruidAgent(self):
        return self.mDruidAgent

    def getMongoDS(self):
        return self.mMongoDS

    def getParseContext(self):
        return self.mParseContext

    def getUnit(self, name):
        for unit_h in self.mUnits:
            if unit_h.getName() == name:
                return unit_h
        return None

    def filterOperation(self, filter_name, conditions, instr):
        if instr is None:
            return filter_name
        op, q, flt_name = instr.partition('/')
        if self.mDruidAgent.goodOpFilterName(flt_name):
            with self:
                if op == "UPDATE":
                    time_label = self.mMongoDS.setFilter(flt_name, conditions)
                    self.cacheFilter(flt_name, conditions, time_label)
                    filter_name = flt_name
                elif op == "DROP":
                    self.mMongoDS.dropFilter(flt_name)
                    self.dropFilter(flt_name)
                else:
                    assert False
        return filter_name

    def cacheFilter(self, filter_name, conditions, time_label):
        self.mFilterCache[filter_name] = [conditions, time_label]

    def dropFilter(self, filter_name):
        if filter_name in self.mFilterCache:
            del self.mFilterCache[filter_name]

    def getFilterList(self):
        ret = []
        for filter_name in self.mDruidAgent.getStdFilterNames():
            ret.append([filter_name, True, True])
        for f_name, flt_info in self.mFilterCache.items():
            if f_name.startswith('_'):
                continue
            ret.append([f_name, False, True, flt_info[1]])
        return sorted(ret)

    def evalTotalCount(self, context):
        if context is None or "cond" not in context:
            return self.getTotal()
        query = {
            "queryType": "timeseries",
            "dataSource": self.mDruidAgent.normDataSetName(self.getName()),
            "granularity": self.mDruidAgent.GRANULARITY,
            "descending": "true",
            "aggregations": [
                { "type": "count", "name": "count",
                    "fieldName": "_ord"}],
            "filter": context["cond"].getDruidRepr(),
            "intervals": [ self.mDruidAgent.INTERVAL ]}
        ret = self.mDruidAgent.call("query", query)
        assert len(ret) == 1
        return ret[0]["result"]["count"]

    def _evalRecSeq(self, context, expect_count):
        query = {
            "queryType": "search",
            "dataSource": self.mDruidAgent.normDataSetName(self.getName()),
            "granularity": self.mDruidAgent.GRANULARITY,
            "searchDimensions": ["_ord"],
            "limit": expect_count + 5,
            "filter": context["cond"].getDruidRepr(),
            "intervals": [ self.mDruidAgent.INTERVAL ]}
        ret = self.mDruidAgent.call("query", query)
        assert len(ret) == 1
        return [int(it["value"]) for it in ret[0]["result"]]

    def evalRecSeq(self, context, expect_count):
        query = {
            "queryType": "topN",
            "dataSource": self.mDruidAgent.normDataSetName(self.getName()),
            "dimension": "_ord",
            "threshold": expect_count + 5,
            "metric": "count",
            "filter": context["cond"].getDruidRepr(),
            "granularity": self.mDruidAgent.GRANULARITY,
            "aggregations": [{
                "type": "count", "name": "count",
                "fieldName": "_ord"}],
            "intervals": [ self.mDruidAgent.INTERVAL ]}
        ret = self.mDruidAgent.call("query", query)
        assert len(ret) == 1
        assert len(ret[0]["result"]) == expect_count
        return [int(it["_ord"]) for it in ret[0]["result"]]

    def dump(self):
        note, time_label = self.mMongoDS.getDSNote()
        return {
            "name": self.mName,
            "note": note,
            "time": time_label}

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
            cond_seq = self.mDruidAgent.getStdFilterConditions(filter_name)
        else:
            if filter_name in self.mFilterCache:
                cond_seq = self.mFilterCache[filter_name][0]
            else:
                cond_seq = conditions
        if "ctx" in rq_args:
            context = json.loads(rq_args["ctx"])
        else:
            context = dict()
        context["cond"] = XL_Condition.parseSeq(cond_seq, self.mParseContext)
        return {
            "total": self.getTotal(),
            "count": self.evalTotalCount(context),
            "stat-list": [unit.makeStat(context)
                for unit in self.mUnits],
            "filter-list": self.getFilterList(),
            "cur-filter": filter_name,
            "conditions": cond_seq}

    #===============================================
    @RestAPI.xl_request
    def rq__xl_statunit(self, rq_args):
        if "ctx" in rq_args:
            context = json.loads(rq_args["ctx"])
        else:
            context = dict()
        context["cond"] = XL_Condition.parseSeq(
            json.loads(rq_args["conditions"]), self.mParseContext)
        unit_name = rq_args["unit"]
        the_unit = None
        for unit_h in self.mUnits:
            if unit_h.getName() == unit_name:
                the_unit = unit_h
                break
        return the_unit.makeStat(context)

    #===============================================
    @RestAPI.xl_request
    def rq__dsnote(self, rq_args):
        note = rq_args.get("note")
        if note is not None:
            with self:
                self.mMongoDS.setDSNote(note)
        return self.dump()

    #===============================================
    @staticmethod
    def _evalTreeHash(tree):
        return md5(json.dumps(tree,
            sort_keys = True, ensure_ascii = False)).hexdigest()

    @RestAPI.xl_request
    def rq__xltree(self, rq_args):
        tree_data = rq_args.get("tree")
        version = rq_args.get("version")
        instr = rq_args.get("instr")
        versions = self.mMongoDS.getVersionList()
        tree = None
        if len(versions) == 0 and tree_data is None:
            tree = defineDefaultDecisionTree()
            tree_hash = self._evalTreeHash(tree.dump())
            version = 0
            self.mMongoDS.addVersion(version, tree.dump(), tree_hash)
            versions = self.mMongoDS.getVersionList()
        elif version is not None:
            tree = DecisionTree.parse(
                self.mMongoDS.getVersionTree(int(version)))
            for ver_info in versions:
                if ver_info[0] == int(version):
                    tree_hash = ver_info[2]
                    break
        elif tree_data is None:
            tree = DecisionTree.parse(
                self.mMongoDS.getVersionTree(versions[-1][0]))
            tree_hash = versions[-1][2];
        else:
            tree = DecisionTree.parse(json.loads(tree_data))
            tree_hash = self._evalTreeHash(tree.dump())
            if instr == "add_version" and tree_hash not in {
                ver_info[2] for ver_info in versions}:
                self.mMongoDS.addVersion(
                    versions[-1][0] + 1, tree.dump(), tree_hash)
                versions = self.mMongoDS.getVersionList()

        cur_version = None
        versions_rep = []
        for ver_info in versions:
            versions_rep.append(ver_info[:2])
            if tree_hash == ver_info[2]:
                cur_version = ver_info[0]
        tree.evalCounts(self)
        return {
            "tree": tree.dump(),
            "counts": tree.getCounts(),
            "stat": tree.getStat(),
            "cur_version": cur_version,
            "versions": versions_rep}

    #===============================================
    @RestAPI.xl_request
    def rq__xlstat(self, rq_args):
        tree_data = rq_args["tree"]
        tree = DecisionTree.parse(json.loads(tree_data))
        point_no = int(rq_args["no"])
        filter_context = {"cond": tree.actualCondition(point_no)}
        count = self.evalTotalCount(filter_context)
        ret = {
            "total": self.getTotal(),
            "count": count}
        if count > 0:
            ret["stat-list"] = [unit.makeStat(filter_context)
                for unit in self.mUnits]
        return ret

    #===============================================
    @RestAPI.xl_request
    def rq__cmptree(self, rq_args):
        tree_data1 = self.mMongoDS.getVersionTree(
                int(rq_args["ver"]))
        if "verbase" in rq_args:
            tree_data2 = self.mMongoDS.getVersionTree(
                int(rq_args["verbase"]))
        else:
            tree_data2 = json.loads(rq_args["tree"])
        return {"cmp": cmpTrees(tree_data1, tree_data2)}

    #===============================================
    @RestAPI.xl_request
    def rq__xl2ws(self, rq_args):
        if "verbase" in rq_args:
            base_version = int(rq_args["verbase"])
            conditions = None
        else:
            base_version = None
            conditions = rq_args["conditions"]
        task_id = self.getDataVault().getApp().startCreateSecondaryWS(
            self, rq_args["ws"],
            base_version = base_version, conditions = conditions)
        return {"task_id" : task_id}

    #===============================================
    @RestAPI.xl_request
    def rq__xl_export(self, rq_args):
        context = {"cond":
            XL_Condition.parseSeq(json.loads(rq_args["conditions"]),
            self.getParseContext())}
        rec_count = self.evalTotalCount(context)
        assert rec_count <= AnfisaConfig.configOption("max.export.size")
        rec_no_seq = self.evalRecSeq(context, rec_count)
        fname = self.getDataVault().getApp().makeExcelExport(
            self.getName(), self, rec_no_seq)
        return {"kind": "excel", "fname": fname}
