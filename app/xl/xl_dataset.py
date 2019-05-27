import json
from time import time
from xml.sax.saxutils import escape

from app.config.a_config import AnfisaConfig
from app.config.solutions import codeHash, StdTreeCodes
from app.model.rest_api import RestAPI
from app.model.dataset import DataSet
from .xl_unit import XL_Unit
from .xl_cond import XL_CondEnv
from .comp_hets import CompHetsUnit, CompHetsMarkupBatch
from app.filter.decision import DecisionTree
from app.filter.tree_parse import ParsedDecisionTree
from app.filter.code_works import cmpTrees
#===============================================
class XLDataset(DataSet):
    sStatRqCount = 0
    sViewCountFull = AnfisaConfig.configOption("xl.view.count.full")
    sViewCountSamples = AnfisaConfig.configOption("xl.view.count.samples")
    sViewMinSamples = AnfisaConfig.configOption("xl.view.min.samples")
    sTimeCoeff = AnfisaConfig.configOption("tm.coeff")

    def __init__(self, data_vault, dataset_info, dataset_path):
        DataSet.__init__(self, data_vault, dataset_info, dataset_path)
        self.mMongoDS = (self.getApp().getMongoConnector().
            getDSAgent(self.getMongoName()))
        self.mDruidAgent = self.getApp().getDruidAgent()
        self.mCondEnv = XL_CondEnv()

        reserved_names = set()
        self.mOpUnits = []
        supp_h = CompHetsUnit(self)
        reserved_names.add(supp_h.getName())
        if supp_h.isActual():
            self.mOpUnits.append(supp_h)
            self.mCondEnv.addOperativeUnit(supp_h)
            for nm in supp_h.getReservedNames():
                self.mCondEnv.addReservedName(nm)
        else:
            self.mCondEnv.addReservedName(supp_h.getName())
        self.mCondEnv.addReservedName("_ord")

        self.mUnits = []
        for unit_data in self.getFltSchema():
            if unit_data["name"] in reserved_names:
                continue
            xl_unit = XL_Unit.create(self, unit_data)
            if xl_unit is not None:
                self.mUnits.append(xl_unit)
        self.mUnitDict = {unit_h.getName(): unit_h
            for unit_h in self.mUnits}
        for unit_h in self.mUnits:
            unit_h.setup()
        self.mFilterCache = dict()
        if self.mMongoDS is not None:
            for f_name, cond_seq, time_label in self.mMongoDS.getFilters():
                if self.mDruidAgent.goodOpFilterName(f_name):
                    self.cacheFilter(f_name, cond_seq, time_label)


    def getDruidAgent(self):
        return self.mDruidAgent

    def getMongoDS(self):
        return self.mMongoDS

    def getCondEnv(self):
        return self.mCondEnv

    def getUnit(self, name):
        return self.mUnitDict.get(name)

    def getOptionalUnit(self, unit_name):
        for op_unit in self.mOpUnits:
            if op_unit.getName() == unit_name:
                return op_unit
        return None

    def makeAllStat(self, condition, time_end,
            repr_context = None, tree = None, point_no = None):
        ret = []
        if tree is not None:
            for op_info in tree.getActiveOperativeUnits(point_no):
                p_no, unit_h, unit_comp = op_info
                if time_end is False:
                    ret.append(unit_h.prepareStat())
                else:
                    ret.append(unit_h.makeCompStat(
                        condition, unit_comp, repr_context))
                if time_end is not None and time() > time_end:
                    time_end = False
        for unit_h in self.mUnits:
            if unit_h.isScreened():
                continue
            if time_end is False:
                ret.append(unit_h.prepareStat())
                continue
            ret.append(unit_h.makeStat(condition, repr_context))
            if time_end is not None and time() > time_end:
                time_end = False
        return ret

    def makeSelectedStat(self, unit_names, condition, time_end,
            repr_context = None, tree = None, point_no = None):
        ret = []
        op_dict = dict()
        if tree is not None:
            for op_info in tree.getActiveOperativeUnits(point_no):
                op_dict[op_info[1].getName()] = op_info
        for unit_name in unit_names:
            if unit_name in op_dict:
                ret.append(op_info[1].makeCompStat(
                    condition, op_info[2], repr_context))
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
        if self.mDruidAgent.goodOpFilterName(flt_name):
            with self:
                if op == "UPDATE":
                    time_label = self.mMongoDS.setFilter(flt_name, cond_seq)
                    self.cacheFilter(flt_name, cond_seq, time_label)
                    filter_name = flt_name
                elif op == "DROP":
                    self.mMongoDS.dropFilter(flt_name)
                    self.dropFilter(flt_name)
                else:
                    assert False
        return filter_name

    def cacheFilter(self, filter_name, cond_seq, time_label):
        self.mFilterCache[filter_name] = [cond_seq, time_label]

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

    def evalSampleList(self, condition):
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
            "threshold": self.sViewCountFull + 5,
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

    def dump(self):
        note, time_label = self.mMongoDS.getDSNote()
        return {
            "name": self.mName,
            "note": note,
            "time": time_label}

    def _addVersion(self, tree_code, tree_hash, version_info_seq):
        new_ver_no = 0
        if len(version_info_seq) > 0:
            ver_no, ver_data, ver_hash = version_info_seq[-1]
            if ver_hash == tree_hash:
                return
            new_ver_no = ver_no + 1
        self.mMongoDS.addTreeCodeVersion(
            new_ver_no, tree_code, tree_hash)
        while (len(version_info_seq) + 1 >
                AnfisaConfig.configOption("max.tree.versions")):
            self.mMongoDS.dropTreeCodeVersion(version_info_seq[0][0])
            del version_info_seq[0]
        return self.mMongoDS.getTreeCodeVersions()

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

    def retrieveListKeys(self, rec_no_seq):
        rec_no_dict = {rec_no: None for rec_no in rec_no_seq}
        with self._openPData() as inp:
            for rec_no, line in enumerate(inp):
                if rec_no not in rec_no_dict:
                    continue
                pre_data = json.loads(line.decode("utf-8"))
                rec_no_dict[rec_no] = [rec_no,
                    escape(pre_data.get("_label")),
                    AnfisaConfig.normalizeColorCode(pre_data.get("_color"))]
        return rec_no_dict

    def _prepareTimeEnd(self, rq_args):
        if "tm" in rq_args:
            return time() + (self.sTimeCoeff * float(rq_args["tm"])) + 1E-5
        return None

    #===============================================
    @RestAPI.xl_request
    def rq__xl_filters(self, rq_args):
        self.sStatRqCount += 1
        time_end = self. _prepareTimeEnd(rq_args)
        if "conditions" in rq_args:
            cond_seq = json.loads(rq_args["conditions"])
        else:
            cond_seq = None
        filter_name = rq_args.get("filter")
        filter_name = self.filterOperation(
            filter_name, cond_seq, rq_args.get("instr"))
        if self.mDruidAgent.hasStdFilter(filter_name):
            cond_seq = self.mDruidAgent.getStdFilterConditions(filter_name)
        else:
            if filter_name in self.mFilterCache:
                cond_seq = self.mFilterCache[filter_name][0]
        condition = self.mCondEnv.parseSeq(cond_seq)
        if "ctx" in rq_args:
            repr_context = json.loads(rq_args["ctx"])
        else:
            repr_context = dict()
        return {
            "total": self.getTotal(),
            "count": self.evalTotalCount(condition),
            "stat-list": self.makeAllStat(condition, time_end, repr_context),
            "filter-list": self.getFilterList(),
            "cur-filter": filter_name,
            "conditions": cond_seq,
            "rq_id": str(self.sStatRqCount) + '/' + str(time())}

    #===============================================
    @RestAPI.xl_request
    def rq__xl_statunit(self, rq_args):
        condition = self.mCondEnv.parseSeq(
            json.loads(rq_args["conditions"]))
        if "ctx" in rq_args:
            repr_context = json.loads(rq_args["ctx"])
        else:
            repr_context = dict()
        the_unit = self.getUnit(rq_args["unit"])
        return the_unit.makeStat(condition, repr_context)

    #===============================================
    @RestAPI.xl_request
    def rq__xl_statunits(self, rq_args):
        time_end = self. _prepareTimeEnd(rq_args)
        if "compiled" in rq_args:
            comp_data = json.loads(rq_args["compiled"])
        else:
            comp_data = None
        if "conditions" in rq_args:
            condition = self.mCondEnv.parseSeq(
                json.loads(rq_args["conditions"]))
            tree, point_no = None, None
        else:
            point_no = int(rq_args["no"])
            if point_no >=0:
                tree = DecisionTree(ParsedDecisionTree
                    (self.mCondEnv, rq_args["code"]), comp_data)
                condition = tree.actualCondition(point_no)
            else:
                condition = self.mCondEnv.getCondNone()
        if "ctx" in rq_args:
            repr_context = json.loads(rq_args["ctx"])
        else:
            repr_context = dict()
        ret = {
            "rq_id": rq_args.get("rq_id"),
            "units": self.makeSelectedStat(json.loads(rq_args["units"]),
                condition, time_end, repr_context, tree, point_no)}
        return ret

    #===============================================
    @RestAPI.xl_request
    def rq__xl_list(self, rq_args):
        if "compiled" in rq_args:
            comp_data = json.loads(rq_args["compiled"])
        else:
            comp_data = None
        if "conditions" in rq_args:
            condition = self.mCondEnv.parseSeq(
                json.loads(rq_args["conditions"]))
            tree = None
        else:
            point_no = int(rq_args["no"])
            if point_no >=0:
                tree = DecisionTree(ParsedDecisionTree
                    (self.mCondEnv, rq_args["code"]), comp_data)
                condition = tree.actualCondition(point_no)
            else:
                condition = self.mCondEnv.getCondNone()
        rec_no_seq = self.evalSampleList(condition)

        if len(rec_no_seq) > self.sViewCountFull:
            rec_no_seq = rec_no_seq[:self.sViewCountSamples]
            q_samples, q_full = True, False
        elif len(rec_no_seq) <= self.sViewMinSamples:
            q_samples, q_full = False, True
        else:
            q_samples, q_full = True, True
        rec_no_dict = self.retrieveListKeys(rec_no_seq)
        ret = dict()
        if q_samples:
            ret["samples"] = [rec_no_dict[rec_no]
                for rec_no in rec_no_seq[:self.sViewCountSamples]]
        if q_full:
            ret["records"] = [rec_no_dict[rec_no]
                for rec_no in sorted(rec_no_seq)]
        return ret

    #===============================================
    @RestAPI.ws_request
    def rq__xl_recdata(self, rq_args):
        return self.getRecordData(int(rq_args.get("rec")))

    #===============================================
    @RestAPI.ws_request
    def rq__xl_reccnt(self, rq_args):
        modes = rq_args.get("m", "").upper()
        rec_no = int(rq_args.get("rec"))
        return self.getViewRepr(rec_no, 'R' in modes)

    #===============================================
    @RestAPI.xl_request
    def rq__dsnote(self, rq_args):
        note = rq_args.get("note")
        if note is not None:
            with self:
                self.mMongoDS.setDSNote(note)
        return self.dump()

    #===============================================
    @RestAPI.xl_request
    def rq__xltree(self, rq_args):
        tree_code = rq_args.get("code")
        std_name = rq_args.get("std")
        version = rq_args.get("version")
        instr = rq_args.get("instr")
        time_end = self. _prepareTimeEnd(rq_args)
        self.sStatRqCount += 1
        version_info_seq = self.mMongoDS.getTreeCodeVersions()
        assert instr is None or tree_code
        if version is not None:
            assert tree_code is None and std_name is None
            for ver_no, ver_date, ver_hash in version_info_seq:
                if ver_no == int(version):
                    tree_code = self.mMongoDS.getTreeCodeVersion(ver_no)
                    break
            assert tree_code is not None
        if tree_code is None:
            if std_name is None and len(version_info_seq) > 0:
                version = version_info_seq[-1][0]
                tree_code = self.mMongoDS.getTreeCodeVersion(version)
            else:
                tree_code = StdTreeCodes.getCode(std_name)
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
        if parsed.getError() is not None:
            ret = {"code": parsed.getTreeCode(),
                "error": parsed.getError()[-1]}
            tree = None
        else:
            tree = DecisionTree(parsed)
            ret = tree.dump()
            ret["counts"] = self.evalPointCounts(tree, time_end)

        if version is not None:
            for ver_no, ver_date, ver_hash in version_info_seq[-1::-1]:
                if ver_hash == tree_hash:
                    version = ver_no
                    break
        if version is not None:
            ret["cur_version"] = int(version)
        std_code = StdTreeCodes.getKeyByHash(tree_hash)
        if std_code:
            ret["std_code"] = std_code
        ret["total"] = self.getTotal()
        ret["versions"] = [info[:2] for info in version_info_seq]
        ret["rq_id"] = str(self.sStatRqCount) + '/' + str(time())
        if tree is not None:
            tree.reportCompData(ret)
        return ret

    #===============================================
    @RestAPI.xl_request
    def rq__xltree_counts(self, rq_args):
        if "compiled" in rq_args:
            comp_data = json.loads(rq_args["compiled"])
        else:
            comp_data = None
        time_end = self. _prepareTimeEnd(rq_args)
        tree = DecisionTree(ParsedDecisionTree
            (self.mCondEnv, rq_args["code"]), comp_data)
        return {
            "rq_id": rq_args.get("rq_id"),
            "counts": self.evalTreeSelectedCounts(tree,
                json.loads(rq_args["points"]), time_end)}

    #===============================================
    @RestAPI.xl_request
    def rq__xlstat(self, rq_args):
        time_end = self. _prepareTimeEnd(rq_args)
        self.sStatRqCount += 1
        point_no = int(rq_args["no"])
        if "compiled" in rq_args:
            comp_data = json.loads(rq_args["compiled"])
        else:
            comp_data = None
        if point_no >=0:
            tree = DecisionTree(ParsedDecisionTree
                (self.mCondEnv, rq_args["code"]), comp_data)
            condition = tree.actualCondition(point_no)
        else:
            condition = self.mCondEnv.getCondNone()
        if "ctx" in rq_args:
            repr_context = json.loads(rq_args["ctx"])
        else:
            repr_context = dict()
        count = self.evalTotalCount(condition)
        ret = {
            "total": self.getTotal(),
            "count": count,
            "stat-list": self.makeAllStat(
                condition, time_end, repr_context, tree, point_no),
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
        tree_code1 = self.mMongoDS.getTreeCodeVersion(int(rq_args["ver"]))
        if "verbase" in rq_args:
            tree_code2 = self.mMongoDS.getTreeCodeVersion(
                int(rq_args["verbase"]))
        else:
            tree_code2 = rq_args["code"]
        return {"cmp": cmpTrees(tree_code1, tree_code2)}

    #===============================================
    @RestAPI.xl_request
    def rq__xl2ws(self, rq_args):
        if "verbase" in rq_args:
            base_version = int(rq_args["verbase"])
            condition = None
        else:
            base_version = None
            condition = self.mCondEnv.parseSeq(
                json.loads(rq_args["conditions"]))
        markup_batch = None
        if self.getFamilyInfo() is not None:
            proband_rel = self.getFamilyInfo().getProbandRel()
            if proband_rel:
                markup_batch = CompHetsMarkupBatch(proband_rel)
        task_id = self.getApp().startCreateSecondaryWS(
            self, rq_args["ws"], base_version = base_version,
            condition = condition, markup_batch = markup_batch)
        return {"task_id" : task_id}

    #===============================================
    @RestAPI.xl_request
    def rq__xl_export(self, rq_args):
        condition = self.mCondEnv.parseSeq(
            json.loads(rq_args["conditions"]))
        rec_count = self.evalTotalCount(condition)
        assert rec_count <= AnfisaConfig.configOption("max.export.size")
        rec_no_seq = self.evalRecSeq(condition, rec_count)
        fname = self.getApp().makeExcelExport(
            self.getName(), self, rec_no_seq)
        return {"kind": "excel", "fname": fname}
