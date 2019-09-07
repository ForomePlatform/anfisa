import json
from time import time
from copy import deepcopy

from app.config.a_config import AnfisaConfig
from app.model.rest_api import RestAPI
from app.model.dataset import DataSet
from .xl_unit import XL_Unit
from .xl_cond import XL_CondEnv
from .xl_list import XlListTask
from app.model.comp_hets import CompHetsOperativeUnit
from app.filter.cond_op import CondOpEnv
from app.filter.decision import DecisionTree
from app.filter.tree_parse import ParsedDecisionTree
from app.filter.code_works import cmpTrees
from app.filter.sol_pack import codeHash
from app.prepare.sec_ws import SecondaryWsCreation
#===============================================
class XLDataset(DataSet):
    sStatRqCount = 0
    sTimeCoeff = AnfisaConfig.configOption("tm.coeff")

    sStdFMark = AnfisaConfig.configOption("filter.std.mark")

    def __init__(self, data_vault, dataset_info, dataset_path):
        DataSet.__init__(self, data_vault, dataset_info, dataset_path)
        self.mDruidAgent = self.getApp().getDruidAgent()
        self.mDruidAgent = self.getApp().getDruidAgent()
        self.mCondEnv = XL_CondEnv(self.getDataInfo().get("modes"))
        self.mCondEnv.addMode("XL")
        self.mCondEnv.addMetaNumUnit("_ord")
        CompHetsOperativeUnit.setupCondEnv(self.mCondEnv, self)

        self.mUnits = []
        for unit_data in self.getFltSchema():
            if unit_data["kind"].startswith("transcript-"):
                continue
            if self.mCondEnv.nameIsReserved(unit_data["name"]):
                continue
            xl_unit = XL_Unit.create(self, unit_data)
            if xl_unit is not None:
                self.mUnits.append(xl_unit)
        self.mUnitDict = {unit_h.getName(): unit_h
            for unit_h in self.mUnits}
        for unit_h in self.mUnits:
            unit_h.setup()

        self.mStdFilters = {self.sStdFMark + flt_name: deepcopy(cond_seq)
            for flt_name, cond_seq in self.mCondEnv.getXlFilters()}

        self.mFilterCache = dict()
        for filter_name, cond_seq in self.mStdFilters.items():
            self.cacheFilter(filter_name, cond_seq, None)

        for f_name, cond_seq, time_label in self.getMongoAgent().getFilters():
            if self.goodOpFilterName(f_name):
                self.cacheFilter(f_name, cond_seq, time_label)

    def getDruidAgent(self):
        return self.mDruidAgent

    def getCondEnv(self):
        return self.mCondEnv

    def getUnit(self, name):
        return self.mUnitDict.get(name)

    def getIndex(self):
        return self

    def makeAllStat(self, condition, repr_context,
            op_env, time_end, point_no = None):
        active_stat_list = []
        for unit_h, unit_comp in op_env.getActiveOperativeUnits(point_no):
            if time_end is False:
                active_stat_list.append(unit_h.prepareStat())
            else:
                active_stat_list.append(unit_h.makeCompStat(
                    condition, unit_comp, repr_context))
            if time_end is not None and time() > time_end:
                time_end = False
        ret = []
        for unit_h in self.mUnits:
            if unit_h.isScreened():
                continue
            if time_end is False:
                ret.append(unit_h.prepareStat())
                continue
            ret.append(unit_h.makeStat(condition, repr_context))
            if time_end is not None and time() > time_end:
                time_end = False
        for act_stat in active_stat_list:
            pos_ins = 0
            for idx, stat in enumerate(ret):
                if stat[1].get("vgroup") == act_stat[1].get("vgroup"):
                    pos_ins = idx + 1
            ret.insert(pos_ins, act_stat)
        return ret

    def makeSelectedStat(self, unit_names, condition, repr_context,
            op_env, time_end, point_no = None):
        ret = []
        op_dict = dict()
        for op_info in op_env.getActiveOperativeUnits(point_no):
            op_dict[op_info[0].getName()] = op_info
        for unit_name in unit_names:
            if unit_name in op_dict:
                ret.append(op_info[0].makeCompStat(
                    condition, op_info[1], repr_context))
            else:
                unit_h = self.getUnit(unit_name)
                assert not unit_h.isScreened()
                ret.append(unit_h.makeStat(condition, repr_context))
            if time_end is not None and time() > time_end:
                break
        return ret

    def filterOperation(self, filter_name, cond_seq, instr):
        if instr is None:
            return filter_name
        op, q, flt_name = instr.partition('/')
        if self.goodOpFilterName(flt_name):
            with self:
                if op == "UPDATE":
                    time_label = self.getMongoAgent.setFilter(
                        flt_name, cond_seq)
                    self.cacheFilter(flt_name, cond_seq, time_label)
                    filter_name = flt_name
                elif op == "DELETE":
                    self.getMongoAgent().dropFilter(flt_name)
                    self.dropFilter(flt_name)
                else:
                    assert False
        return filter_name

    def cacheFilter(self, filter_name, cond_seq, time_label):
        self.mFilterCache[filter_name] = [cond_seq, time_label]

    def dropFilter(self, filter_name):
        if filter_name in self.mFilterCache:
            del self.mFilterCache[filter_name]

    def goodOpFilterName(self, flt_name):
        return (flt_name and not flt_name.startswith(self.sStdFMark)
            and flt_name[0].isalpha() and ' ' not in flt_name)

    def hasStdFilter(self, filter_name):
        return filter_name in self.mStdFilters

    def getFilterList(self, research_mode = True):
        ret = []
        for filter_name, flt_info in self.mFilterCache.items():
            if filter_name.startswith('_'):
                continue
            ret.append([filter_name, self.hasStdFilter(filter_name),
                True, flt_info[1]])
        return sorted(ret)

    def evalTotalCount(self, condition = None):
        if condition is None:
            return self.getTotal()
        cond_repr = condition.getDruidRepr()
        if cond_repr is None:
            return self.getTotal()
        if cond_repr is False:
            return 0
        query = {
            "queryType": "timeseries",
            "dataSource": self.mDruidAgent.normDataSetName(self.getName()),
            "granularity": self.mDruidAgent.GRANULARITY,
            "descending": "true",
            "aggregations": [
                { "type": "count", "name": "count",
                    "fieldName": "_ord"}],
            "filter": condition.getDruidRepr(),
            "intervals": [ self.mDruidAgent.INTERVAL ]}
        ret = self.mDruidAgent.call("query", query)
        assert len(ret) == 1
        return ret[0]["result"]["count"]

    def _evalRecSeq(self, condition, expect_count):
        if condition is None:
            cond_repr = None
        else:
            cond_repr = condition.getDruidRepr()
            if cond_repr is False:
                return []
        query = {
            "queryType": "search",
            "dataSource": self.mDruidAgent.normDataSetName(self.getName()),
            "granularity": self.mDruidAgent.GRANULARITY,
            "searchDimensions": ["_ord"],
            "limit": expect_count + 5,
            "intervals": [ self.mDruidAgent.INTERVAL ]}
        if cond_repr is not None:
            query["filter"] = cond_repr
        ret = self.mDruidAgent.call("query", query)
        assert len(ret) == 1
        return [int(it["value"]) for it in ret[0]["result"]]

    def evalRecSeq(self, condition, expect_count):
        if condition is None:
            cond_repr = None
        else:
            cond_repr = condition.getDruidRepr()
            if cond_repr is False:
                return []
        query = {
            "queryType": "topN",
            "dataSource": self.mDruidAgent.normDataSetName(self.getName()),
            "dimension": "_ord",
            "threshold": expect_count + 5,
            "metric": "count",
            "granularity": self.mDruidAgent.GRANULARITY,
            "aggregations": [{
                "type": "count", "name": "count",
                "fieldName": "_ord"}],
            "intervals": [ self.mDruidAgent.INTERVAL ]}
        if cond_repr is not None:
            query["filter"] = cond_repr
        ret = self.mDruidAgent.call("query", query)
        assert len(ret) == 1
        assert len(ret[0]["result"]) == expect_count
        return [int(it["_ord"]) for it in ret[0]["result"]]

    def evalSampleList(self, condition, max_count):
        if condition is None:
            cond_repr = None
        else:
            cond_repr = condition.getDruidRepr()
            if cond_repr is False:
                return []
        query = {
            "queryType": "topN",
            "dataSource": self.mDruidAgent.normDataSetName(self.getName()),
            "dimension": "_ord",
            "threshold": max_count,
            "metric": "max_rand",
            "granularity": self.mDruidAgent.GRANULARITY,
            "aggregations": [{
                "type": "longMax", "name": "max_rand",
                "fieldName": "_rand"}],
            "intervals": [ self.mDruidAgent.INTERVAL ]}
        if cond_repr is not None:
            query["filter"] = cond_repr
        ret = self.mDruidAgent.call("query", query)
        assert len(ret) == 1
        return [int(it["_ord"]) for it in ret[0]["result"]]

    def _addVersion(self, tree_code, tree_hash, version_info_seq):
        new_ver_no = 0
        if len(version_info_seq) > 0:
            ver_no, ver_data, ver_hash = version_info_seq[-1]
            if ver_hash == tree_hash:
                return version_info_seq
            new_ver_no = ver_no + 1
        self.getMongoAgent().addTreeCodeVersion(
            new_ver_no, tree_code, tree_hash)
        while (len(version_info_seq) + 1 >
                AnfisaConfig.configOption("max.tree.versions")):
            self.getMongoAgent().dropTreeCodeVersion(version_info_seq[0][0])
            del version_info_seq[0]
        return self.getMongoAgent().getTreeCodeVersions()

    def evalPointCounts(self, tree, time_end):
        counts = [None] * len(tree)
        for idx in range(len(tree)):
            if tree.pointNotActive(idx):
                counts[idx] = 0
                continue
            if time_end is not None and time() > time_end:
                break
            counts[idx] = self.evalTotalCount(tree.actualCondition(idx))
            if counts[idx] == 0 and tree.checkZeroAfter(idx):
                for idx1 in range(idx, len(tree)):
                    counts[idx1] = 0
                break
        return counts

    def evalTreeSelectedCounts(self, tree, point_idxs, time_end):
        counts = [None] * len(tree)
        has_some = False
        zero_idx = None
        for idx in point_idxs:
            if tree.pointNotActive(idx):
                counts[idx] = 0
                continue
            if has_some and time_end is not None and time() > time_end:
                break
            if zero_idx is not None and idx >= zero_idx:
                continue
            counts[idx] = self.evalTotalCount(tree.actualCondition(idx))
            has_some = True
            if counts[idx] == 0 and tree.checkZeroAfter(idx):
                zero_idx = idx
                for idx1 in range(zero_idx, len(tree)):
                    counts[idx1] = 0
        return counts

    #===============================================
    def _prepareTimeEnd(self, rq_args):
        if "tm" in rq_args:
            return time() + (self.sTimeCoeff * float(rq_args["tm"])) + 1E-5
        return None

    def _prepareContext(self, rq_args):
        if "ctx" in rq_args:
            return json.loads(rq_args["ctx"])
        return dict()

    def _prepareTree(self, rq_args, with_point = True):
        point_no = int(rq_args["no"])
        if with_point and point_no < 0:
            return None, point_no, self.mCondEnv.getCondNone()
        comp_data = (json.loads(rq_args["compiled"])
            if "compiled" in rq_args else None)
        parsed = ParsedDecisionTree(self.mCondEnv, rq_args["code"])
        tree = DecisionTree(parsed, comp_data)
        return tree, point_no,tree.actualCondition(point_no)

    def _prepareConditions(self, rq_args):
        comp_data = (json.loads(rq_args["compiled"])
            if "compiled" in rq_args else None)
        op_cond = CondOpEnv(self.mCondEnv, comp_data,
            json.loads(rq_args["conditions"]))
        return op_cond, op_cond.getResult()

    #===============================================
    @RestAPI.xl_request
    def rq__xl_stat(self, rq_args):
        self.sStatRqCount += 1
        time_end = self._prepareTimeEnd(rq_args)
        repr_context = self._prepareContext(rq_args)
        if "conditions" in rq_args:
            cond_seq = json.loads(rq_args["conditions"])
        else:
            cond_seq = None
        filter_name = rq_args.get("filter")
        filter_name = self.filterOperation(
            filter_name, cond_seq, rq_args.get("instr"))
        if self.hasStdFilter(filter_name):
            cond_seq = self.mStdFilters.get(filter_name)
        else:
            if filter_name in self.mFilterCache:
                cond_seq = self.mFilterCache[filter_name][0]
        op_env = CondOpEnv(self.mCondEnv, None, cond_seq)
        condition = op_env.getResult()
        stat_list = self.makeAllStat(condition, repr_context, op_env, time_end)
        ret = {
            "total": self.getTotal(),
            "count": self.evalTotalCount(condition),
            "stat-list": stat_list,
            "filter-list": self.getFilterList(),
            "cur-filter": filter_name,
            "conditions": cond_seq,
            "rq_id": str(self.sStatRqCount) + '/' + str(time())}
        op_env.report(ret)
        return ret

    #===============================================
    @RestAPI.xl_request
    def rq__xl_statunit(self, rq_args):
        the_unit = self.getUnit(rq_args["unit"])
        _, condition = self._prepareConditions(rq_args)
        repr_context = self._prepareContext(rq_args)
        return the_unit.makeStat(condition, repr_context)

    #===============================================
    @RestAPI.xl_request
    def rq__xl_statunits(self, rq_args):
        time_end = self. _prepareTimeEnd(rq_args)
        repr_context = self._prepareContext(rq_args)
        if "conditions" in rq_args:
            op_env, condition = self._prepareConditions(rq_args)
            point_no = None
        else:
            tree, point_no, condition = self._prepareTree(rq_args)
            op_env = tree.getCondOpEnv()
        ret = {
            "rq_id": rq_args.get("rq_id"),
            "units": self.makeSelectedStat(json.loads(rq_args["units"]),
                condition, repr_context, op_env, time_end, point_no)}
        return ret

    #===============================================
    @RestAPI.xl_request
    def rq__xl_list(self, rq_args):
        if "conditions" in rq_args:
            _, condition = self._prepareConditions(rq_args)
        else:
            tree, point_no, condition = self._prepareTree(rq_args)
        return {"task_id" : self.getApp().runTask(
            XlListTask(self, condition))}

    #===============================================
    @RestAPI.xl_request
    def rq__xltree(self, rq_args):
        tree_code = rq_args.get("code")
        std_name = rq_args.get("std_name")
        version = rq_args.get("version")
        instr = rq_args.get("instr")
        time_end = self. _prepareTimeEnd(rq_args)
        self.sStatRqCount += 1
        version_info_seq = self.getMongoAgent().getTreeCodeVersions()
        assert instr is None or tree_code
        if version is not None:
            assert tree_code is None and std_name is None
            for ver_no, ver_date, ver_hash in version_info_seq:
                if ver_no == int(version):
                    tree_code = self.getMongoAgent().getTreeCodeVersion(ver_no)
                    break
            assert tree_code is not None
        if tree_code is None:
            if std_name is None and len(version_info_seq) > 0:
                version = version_info_seq[-1][0]
                tree_code = self.getMongoAgent().getTreeCodeVersion(version)
            else:
                tree_code = self.mCondEnv.getStdTreeCode(std_name)
        else:
            assert std_name is None
        tree_hash = codeHash(tree_code)
        if instr is not None:
            instr = json.loads(instr)
            if len(instr) == 1 and instr[0] == "add_version":
                version_info_seq = self._addVersion(
                    tree_code, tree_hash, version_info_seq)
                version = version_info_seq[-1][0]
                instr = None
        parsed = ParsedDecisionTree.parse(self.mCondEnv, tree_code, instr)
        op_env = None
        if parsed.getError() is not None:
            ret = {"code": parsed.getTreeCode(),
                "error": True}
        else:
            tree = DecisionTree(parsed)
            op_env = tree.getCondOpEnv()
            ret = tree.dump()
            ret["counts"] = self.evalPointCounts(tree, time_end)

        if version is not None:
            for ver_no, ver_date, ver_hash in version_info_seq[-1::-1]:
                if ver_hash == tree_hash:
                    version = ver_no
                    break
        if version is not None:
            ret["cur_version"] = int(version)
        std_code = self.mCondEnv.getStdTreeNameByHash(tree_hash)
        if std_code:
            ret["std_code"] = std_code
        ret["total"] = self.getTotal()
        ret["versions"] = [info[:2] for info in version_info_seq]
        ret["rq_id"] = str(self.sStatRqCount) + '/' + str(time())
        if op_env is not None:
            op_env.report(ret)
        return ret

    #===============================================
    @RestAPI.xl_request
    def rq__xltree_counts(self, rq_args):
        time_end = self. _prepareTimeEnd(rq_args)
        tree, point_no, condition = self._prepareTree(rq_args, False)
        return {
            "rq_id": rq_args.get("rq_id"),
            "counts": self.evalTreeSelectedCounts(tree,
                json.loads(rq_args["points"]), time_end)}

    #===============================================
    @RestAPI.xl_request
    def rq__xltree_stat(self, rq_args):
        time_end = self. _prepareTimeEnd(rq_args)
        repr_context = self._prepareContext(rq_args)
        self.sStatRqCount += 1
        tree, point_no, condition = self._prepareTree(rq_args)
        count = self.evalTotalCount(condition)
        ret = {
            "total": self.getTotal(),
            "count": count,
            "stat-list": self.makeAllStat(condition, repr_context,
                tree.getCondOpEnv(), time_end, point_no),
            "rq_id": str(self.sStatRqCount) + '/' + str(time())}
        return ret


    #===============================================
    @RestAPI.xl_request
    def rq__xltree_code(self, rq_args):
        tree_code = rq_args["code"]
        parser = ParsedDecisionTree(self.mCondEnv, tree_code)
        ret = {"code": tree_code}
        if parser.getError() is not None:
            msg_text, lineno, col_offset = parser.getError()
            ret["line"] = lineno
            ret["pos"] = col_offset
            ret["error"] = msg_text
        return ret

    #===============================================
    @RestAPI.xl_request
    def rq__cmptree(self, rq_args):
        tree_code1 = self.getMongoAgent().getTreeCodeVersion(
            int(rq_args["ver"]))
        if "verbase" in rq_args:
            tree_code2 = self.getMongoAgent().getTreeCodeVersion(
                int(rq_args["verbase"]))
        else:
            tree_code2 = rq_args["code"]
        return {"cmp": cmpTrees(tree_code1, tree_code2)}

    #===============================================
    @RestAPI.xl_request
    def rq__xl2ws(self, rq_args):
        base_version, op_cond, std_name = None, None, None
        if "verbase" in rq_args:
            base_version = int(rq_args["verbase"])
        elif "std_name" in rq_args:
            std_name = rq_args["std_name"]
        else:
            op_cond, _ = self._prepareConditions(rq_args)
        markup_batch = None
        task = SecondaryWsCreation(self, rq_args["ws"],
            base_version, op_cond, std_name, markup_batch,
            "force" in rq_args)
        return {"task_id" : self.getApp().runTask(task)}

    #===============================================
    @RestAPI.xl_request
    def rq__xl_export(self, rq_args):
        _, condition = self._prepareConditions(rq_args)
        rec_count = self.evalTotalCount(condition)
        assert rec_count <= AnfisaConfig.configOption("max.export.size")
        rec_no_seq = self.evalRecSeq(condition, rec_count)
        fname = self.getApp().makeExcelExport(
            self.getName(), self, rec_no_seq)
        return {"kind": "excel", "fname": fname}
