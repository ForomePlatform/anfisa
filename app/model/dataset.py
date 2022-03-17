#  Copyright (c) 2019. Partners HealthCare and other members of
#  Forome Association
#
#  Developed by Sergey Trifonov based on contributions by Joel Krier,
#  Michael Bouzinier, Shamil Sunyaev and other members of Division of
#  Genetics, Brigham and Women's Hospital
#
#  Licensed under the Apache License, Version 2.0 (the "License");
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
#
#        http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.
#

import json, abc
from datetime import datetime, timedelta
from xml.sax.saxutils import escape

from app.view.asp_set import AspectSetH
from app.config.a_config import AnfisaConfig
from app.config.view_tune import tuneAspects
from app.config.flt_tune import tuneUnits
from app.config.solutions import completeDsModes
from app.eval.condition import ConditionMaker
from app.eval.filter import FilterEval
from app.eval.dtree import DTreeEval
from app.eval.code_works import cmpTrees
from app.eval.dtree_parse import ParsedDTree
from app.eval.dtree_mod import modifyDTreeCode
from app.prepare.sec_ws import SecondaryWsCreation
from .ds_disk import DataDiskStorage
from .ds_favor import FavorStorage
from .sol_broker import SolutionBroker
from .family import FamilyInfo
from .zygosity import ZygositySupport
from .rest_api import RestAPI
from .rec_list import RecListTask
from .tab_report import reportCSV
#===============================================
class DataSet(SolutionBroker):
    sStatRqCount = 0
    sTimeCoeff = AnfisaConfig.configOption("tm.coeff")
    sMaxTabRqSize = AnfisaConfig.configOption("max.tab.rq.size")
    sMaxExportSize = AnfisaConfig.configOption("export.max.count")

    #===============================================
    def __init__(self, data_vault, dataset_info, dataset_path,
            sol_pack_name = None, add_modes = None):
        SolutionBroker.__init__(self,
            dataset_info["meta"].get("data_schema", "CASE"),
            dataset_info.get("modes"))
        self.addModes(data_vault.getApp().getRunModes())
        if add_modes:
            self.addModes(add_modes)
        self.mDataVault = data_vault
        self.mDataInfo = dataset_info
        self.mName = dataset_info["name"]
        self.mDSKind = dataset_info["kind"]
        self.mTotal = dataset_info["total"]
        self.mMongoAgent = (data_vault.getApp().getMongoConnector().
            getDSAgent(dataset_info["mongo"], dataset_info["kind"]))
        self.mAspects = AspectSetH.load(dataset_info["view_schema"])
        self.mFltSchema = dataset_info["flt_schema"]
        self.mPath = dataset_path
        self.mFInfo = self.mDataVault.checkFileStat(
            self.mPath + "/dsinfo.json")
        self.mCondVisitorTypes = []
        reference = dataset_info["meta"]["versions"].get("reference")
        self.mFastaBase = "hg38" if reference and "38" in reference else "hg19"

        if self.getBaseDSName():
            self.addModes({"DERIVED"})
        else:
            self.addModes({"SECONDARY"})

        if self.getDataSchema() == "FAVOR" and self.mDSKind == "xl":
            self.mRecStorage = FavorStorage(
                self.getApp().getOption("favor-url"))
        else:
            self.mRecStorage = DataDiskStorage(self, self.mPath)

        self.mFamilyInfo = FamilyInfo(dataset_info["meta"])
        if (self.mDataInfo.get("zygosity_var")
                and 1 <= len(self.mFamilyInfo) <= 10):
            self.addModes({"ZYG"})
        self.mZygSupport = None

        self.mViewContext = dict()
        if self.mFamilyInfo.getCohortList():
            self.mViewContext["cohorts"] = self.mFamilyInfo.getCohortMap()
            self.addModes({"COHORTS"})
        elif self.getDataSchema() != "FAVOR":
            self.addModes({"PROBAND"})
        completeDsModes(self)

        tuneAspects(self, self.mAspects)

    def startService(self):
        self.mZygSupport = ZygositySupport(self)
        tuneUnits(self)
        self.mDataVault.getVarRegistry().relax(self.mName)
        self.setSolEnv(self.mDataVault.makeSolutionEnv(self))

    def isUpToDate(self, fstat_info):
        return fstat_info == self.mFInfo

    def descrContext(self, rq_args, rq_descr):
        rq_descr.append("kind=" + self.mDSKind)
        rq_descr.append("dataset=" + self.mName)

    def addConditionVisitorType(self, visitor_type):
        self.mCondVisitorTypes.append(visitor_type)

    @abc.abstractmethod
    def getEvalSpace(self):
        assert False, "Abstract eval space"

    def getApp(self):
        return self.mDataVault.getApp()

    def getDataVault(self):
        return self.mDataVault

    def getName(self):
        return self.mName

    def getDSKind(self):
        return self.mDSKind

    def getTotal(self):
        return self.mTotal

    def getMongoAgent(self):
        return self.mMongoAgent

    def getFltSchema(self):
        return self.mFltSchema

    def getDataInfo(self):
        return self.mDataInfo

    def getFamilyInfo(self):
        return self.mFamilyInfo

    def getRecStorage(self):
        return self.mRecStorage

    def getDirPath(self):
        return self.mPath

    #===============================================
    def getViewSchema(self):
        return self.mAspects.dump()

    def getRecordData(self, rec_no):
        return self.mRecStorage.getRecordData(rec_no)

    def getFirstAspectID(self):
        return self.mAspects.getFirstAspectID()

    def getViewRepr(self, rec_no, details = None, active_samples = None):
        rec_data = self.mRecStorage.getRecordData(rec_no)
        v_context = self.mViewContext.copy()
        if details is not None:
            v_context["details"] = details
        if active_samples:
            if active_samples.strip().startswith('['):
                v_context["active-samples"] = set(json.parse(active_samples))
            else:
                v_context["active-samples"] = set(map(int,
                    active_samples.split(',')))
        v_context["data"] = rec_data
        v_context["rec_no"] = rec_no
        return self.mAspects.getViewRepr(rec_data, v_context)

    def getSourceVersions(self):
        if "versions" in self.mDataInfo["meta"]:
            versions = self.mDataInfo["meta"]["versions"]
            return [[key, str(versions[key])]
                for key in sorted(versions.keys())]
        return []

    def getBaseDSName(self):
        return self.mDataInfo.get("base")

    def getRootDSName(self):
        return self.mDataInfo.get("root")

    def getTagsMan(self):
        return None

    def getZygositySupport(self):
        return self.mZygSupport

    def getZygUnitNames(self):
        if self.testRequirements({"ZYG"}):
            var_name = self.mDataInfo["zygosity_var"]
            return ["%s_%d" % (var_name, idx)
                for idx in range(len(self.mFamilyInfo))]
        return []

    def makeSolEntry(self, key, entry_data, name,
            updated_time = None, updated_from = None):
        if key == "filter":
            return FilterEval(self.getEvalSpace(), entry_data,
                name, updated_time, updated_from)
        if key == "dtree":
            return DTreeEval(self.getEvalSpace(), entry_data,
                name, updated_time, updated_from)
        assert False, "Bad solution entry kind: " + key
        return None

    def getDocsInfo(self):
        ret = [None, [["Info", "info.html"]]]
        if self.mDataInfo.get("doc"):
            ret[-1] += self.mDataInfo["doc"]
        return ret

    def getMaxExportSize(self):
        return self.sMaxExportSize

    #===============================================
    @classmethod
    def shortPDataReport(cls, rec_no, rec_data):
        return {
            "no": rec_no,
            "lb": escape(rec_data.get("_label")),
            "cl": AnfisaConfig.normalizeColorCode(
                rec_data.get("_color"))}

    #===============================================
    def dumpDSInfo(self, navigation_mode = False):
        note, time_label = self.getMongoAgent().getNote()
        ret = {
            "name": self.mName,
            "upd-time": self.getMongoAgent().getCreationDate(),
            "create-time": self.mDataVault.getTimeOfStat(self.mFInfo),
            "kind": self.mDSKind,
            "note": note,
            "doc": self.getDocsInfo(),
            "total": self.getTotal(),
            "date-note": time_label}
        ancestors = []
        base_name = self.getBaseDSName()
        while base_name is not None:
            base_h = self.mDataVault.getDS(base_name)
            if base_h is None:
                ancestors.append([base_name, None])
                break
            ancestors.append([base_name, base_h.getDocsInfo()])
            base_name = base_h.getBaseDSName()
        if self.getRootDSName() and self.getRootDSName() != self.getName():
            if len(ancestors) == 0 or ancestors[-1][0] != self.getRootDSName():
                root_h = self.mDataVault.getDS(self.getRootDSName())
                ancestors.append([self.getRootDSName(),
                    None if root_h is None else root_h.getDocsInfo()])
        ret["ancestors"] = ancestors

        if navigation_mode:
            secondary_seq = self.mDataVault.getSecondaryWSNames(self)
            if secondary_seq:
                ret["secondary"] = [ws_h.getName() for ws_h in secondary_seq]
        else:
            ret["meta"] = self.mDataInfo["meta"]
            ret["cohorts"] = self.mFamilyInfo.getCohortList()
            ret["unit-classes"] = (
                self.mDataVault.getVarRegistry().getClassificationDescr())
            ret["export-max-count"] = self.sMaxExportSize
        if not navigation_mode:
            cur_v_group = None
            unit_groups = []
            for unit_h in self.getEvalSpace().iterUnits():
                if unit_h.isScreened():
                    continue
                if unit_h.getVGroup() != cur_v_group:
                    cur_v_group = unit_h.getVGroup()
                    if not cur_v_group:
                        cur_v_group = ""
                    if (len(unit_groups) == 0
                            or unit_groups[-1][0] != cur_v_group):
                        unit_groups.append([cur_v_group, []])
                unit_groups[-1][1].append(unit_h.getName())
            ret["unit-groups"] = unit_groups
            igv_url = self.mDataVault.getIGVUrl(self.getRootDSName())
            if igv_url is not None:
                ret["igv-urls"] = [
                    f"{igv_url}/{sample_nm}.{self.mFastaBase}.bam"
                    for sample_nm in self.mFamilyInfo.getNames()]
        return ret

    #===============================================
    def prepareAllUnitStat(self, condition, eval_h,
            time_end, point_no = None):
        ret = []
        for unit_h in self.getEvalSpace().iterUnits():
            if unit_h.isScreened():
                continue
            if unit_h.getUnitKind() == "func":
                ret.append(unit_h.makeInfoStat(eval_h, point_no))
                continue
            if point_no is not None and not unit_h.isInDTrees():
                continue
            if time_end is False:
                ret.append(unit_h.prepareStat(incomplete_mode = True))
                continue
            ret.append(unit_h.makeStat(condition, eval_h))
            if time_end is not None and datetime.now() > time_end:
                time_end = False
        return ret

    def prepareSelectedUnitStat(self, unit_names, condition,
            eval_h, time_end = None, point_no = None):
        ret = []
        for unit_name in unit_names:
            unit_h = self.getEvalSpace().getUnit(unit_name)
            assert not unit_h.isScreened() and unit_h.getUnitKind != "func", (
                "No function provided in DS: " + unit_name)
            assert point_no is None or unit_h.isInDTrees(), (
                "Unit is inaccessible in Decision Trees: " + unit_name)
            ret.append(unit_h.makeStat(condition, eval_h))
            if time_end is not None and datetime.now() > time_end:
                break
        return ret

    #===============================================
    def prepareDTreePointCounts(self, dtree_h, rq_id,
            point_idxs = None, time_end = None):
        counts = [None] * len(dtree_h)
        needs_more = point_idxs is not None
        zero_idx = None
        if point_idxs is None:
            point_idxs = range(len(dtree_h))
        for idx in point_idxs:
            if dtree_h.pointNotActive(idx):
                counts[idx] = self.getEvalSpace().makeEmptyCounts()
                continue
            if (not needs_more and time_end is not None
                    and datetime.now() > time_end):
                break
            if zero_idx is not None and idx >= zero_idx:
                continue
            counts[idx] = self.getEvalSpace().evalTotalCounts(
                dtree_h.getActualCondition(idx))
            needs_more = False
            if counts[idx][0] == 0 and dtree_h.checkZeroAfter(idx):
                zero_idx = idx
                for idx1 in range(zero_idx, len(dtree_h)):
                    counts[idx1] = counts[idx][:]
        return counts

    #===============================================
    def visitCondition(self, condition, ret_handle):
        if condition is None:
            return
        for cond_visitor_type in self.mCondVisitorTypes:
            visitor = cond_visitor_type(self)
            condition.visit(visitor)
            ret = visitor.makeResult()
            if ret:
                ret_handle[visitor.getName()] = ret

    #===============================================
    def _getArgCondFilter(self, rq_args,
            activate_it = True, join_cond_data = None):
        filter_h, cond_data = None, None
        if rq_args.get("filter"):
            filter_h = self.pickSolEntry("filter", rq_args["filter"])
            assert filter_h is not None, "No filter for: " + rq_args["filter"]
            if join_cond_data is not None:
                cond_data = filter_h.getCondDataSeq()
                filter_h = None
        if filter_h is None and cond_data is None:
            if "conditions" in rq_args:
                cond_data = json.loads(rq_args["conditions"])
            else:
                cond_data = ConditionMaker.condAll()
        if join_cond_data is not None:
            assert filter_h is None, "Filter&join collision"
            cond_data = cond_data[:] + join_cond_data[:]
        if filter_h is None:
            filter_h = FilterEval(self.getEvalSpace(), cond_data)
        filter_h = self.updateSolEntry("filter", filter_h)
        if activate_it:
            filter_h.activate()
        return filter_h

    def _getArgDTree(self, rq_args, activate_it = True,
            use_dtree = True, dtree_h = None, no_cache = False):
        if dtree_h is None:
            if use_dtree and "dtree" in rq_args:
                dtree_h = self.pickSolEntry("dtree", rq_args["dtree"])
                assert dtree_h is not None, (
                    "No decision tree: " + rq_args["dtree"])
            else:
                assert "code" in rq_args, (
                    'Missing request argument: "dtree" or "code"')
                dtree_h = DTreeEval(self.getEvalSpace(), rq_args["code"])
        if not no_cache:
            dtree_h = self.updateSolEntry("dtree", dtree_h)
        if activate_it:
            dtree_h.activate()
        return dtree_h

    def _getArgTimeEnd(self, rq_args):
        if self.getEvalSpace().heavyMode() and "tm" in rq_args:
            return datetime.now() + timedelta(
                seconds = self.sTimeCoeff * float(rq_args["tm"]) + 1E-5)
        return None

    def _makeRqId(self):
        self.sStatRqCount += 1
        return str(self.sStatRqCount) + '/' + str(datetime.now())

    #===============================================
    @RestAPI.ds_request
    def rq__ds_stat(self, rq_args):
        time_end = self._getArgTimeEnd(rq_args)
        join_cond_data = None
        if "instr" in rq_args:
            instr_info = json.loads(rq_args["instr"])
            if instr_info[0] == "JOIN":
                join_cond_data = self.pickSolEntry(
                    "filter", instr_info[1]).getCondDataSeq()
            else:
                if instr_info[0] == "DELETE":
                    instr_cond_data = None
                else:
                    instr_cond_data = self._getArgCondFilter(
                        rq_args, activate_it = False).getCondDataSeq()
                if not self.modifySolEntry("filter",
                        instr_info, instr_cond_data):
                    assert False, ("Bad instruction kind: "
                        + json.dumps(instr_info))
        filter_h = self._getArgCondFilter(rq_args,
            join_cond_data = join_cond_data)
        condition = filter_h.getCondition()
        ret_handle = {
            "kind": self.mDSKind,
            "total-counts": self.getEvalSpace().getTotalCounts(),
            "filtered-counts": self.getEvalSpace().evalTotalCounts(condition),
            "stat-list": self.prepareAllUnitStat(condition,
                filter_h, time_end),
            "filter-list": self.getSolEntryList("filter"),
            "cur-filter": filter_h.getFilterName(),
            "rq-id": self._makeRqId()}
        ret_handle.update(filter_h.reportInfo())
        return ret_handle

    #===============================================
    @RestAPI.ds_request
    def rq__dtree_stat(self, rq_args):
        time_end = self. _getArgTimeEnd(rq_args)
        dtree_h = self._getArgDTree(rq_args)
        assert "no" in rq_args, 'Missing request argument "no"'
        point_no = int(rq_args["no"])
        condition = dtree_h.getActualCondition(point_no)
        ret_handle = {
            "total-counts": self.getEvalSpace().getTotalCounts(),
            "filtered-counts": self.getEvalSpace().evalTotalCounts(condition),
            "stat-list": self.prepareAllUnitStat(condition,
                dtree_h, time_end, point_no),
            "rq-id": self._makeRqId()}
        return ret_handle

    #===============================================
    @RestAPI.ds_request
    def rq__statunits(self, rq_args):
        time_end = self. _getArgTimeEnd(rq_args)
        if "dtree" in rq_args or "code" in rq_args:
            eval_h = self._getArgDTree(rq_args)
            assert "no" in rq_args, 'Missing request argument "no"'
            point_no = int(rq_args["no"])
            condition = eval_h.getActualCondition(point_no)
        else:
            eval_h = self._getArgCondFilter(rq_args)
            condition, point_no = eval_h.getCondition(), None
        assert "units" in rq_args, 'Missing request argument "units"'
        ret_handle = {
            "rq-id": rq_args.get("rq_id"),
            "units": self.prepareSelectedUnitStat(
                json.loads(rq_args["units"]), condition,
                eval_h, time_end, point_no)}
        return ret_handle

    #===============================================
    @RestAPI.ds_request
    def rq__statfunc(self, rq_args):
        if "dtree" in rq_args or "code" in rq_args:
            eval_h = self._getArgDTree(rq_args)
            point_no = int(rq_args["no"])
            assert "no" in rq_args, 'Missing request argument "no"'
            condition = eval_h.getActualCondition(point_no)
        else:
            eval_h = self._getArgCondFilter(rq_args)
            condition = eval_h.getCondition()
            point_no = int(rq_args["no"]) if "no" in rq_args else None

        assert "unit" in rq_args, 'Missing request argument "unit"'
        unit_h = self.getEvalSpace().getUnit(rq_args["unit"])
        assert "param" in rq_args, 'Missing request argument "param"'
        parameters = json.loads(rq_args["param"])
        ret = unit_h.makeParamStat(condition, parameters, eval_h, point_no)
        if rq_args.get("rq_id"):
            ret["rq-id"] = rq_args.get("rq_id")
        if rq_args.get("no"):
            ret["no"] = rq_args.get("no")
        return ret

    #===============================================
    @RestAPI.ds_request
    def rq__dtree_set(self, rq_args):
        time_end = self._getArgTimeEnd(rq_args)

        instr = rq_args.get("instr")
        if instr is not None:
            instr = json.loads(instr)
        if instr and instr[0] == "DTREE":
            dtree_proc_h = self._getArgDTree(
                rq_args, activate_it = False)
            if not self.modifySolEntry("dtree", instr[1:],
                    dtree_proc_h.getCode()):
                assert False, (
                    "Failed to modify DTREE: " + json.dumps(instr[1:]))
            instr = None
        dtree_h = None
        if instr:
            assert "code" in rq_args, 'Missing request argument "code"'
            parsed = ParsedDTree(self.getEvalSpace(), rq_args["code"])
            dtree_code = modifyDTreeCode(parsed, instr)
            dtree_h = DTreeEval(self.getEvalSpace(), dtree_code)
        dtree_h = self._getArgDTree(rq_args, dtree_h = dtree_h)
        rq_id = self._makeRqId()
        ret_handle = {
            "kind": self.mDSKind,
            "total-counts": self.getEvalSpace().getTotalCounts(),
            "point-counts": self.prepareDTreePointCounts(
                dtree_h, rq_id, time_end = time_end),
            "dtree-list": self.getSolEntryList("dtree"),
            "rq-id": rq_id}

        ret_handle.update(dtree_h.reportInfo())
        return ret_handle

    #===============================================
    @RestAPI.ds_request
    def rq__dtree_counts(self, rq_args):
        time_end = self. _getArgTimeEnd(rq_args)
        dtree_h = self._getArgDTree(rq_args)
        assert "rq_id" in rq_args, 'Missing request argument "rq_id"'
        assert "points" in rq_args, 'Missing request argument "points"'
        rq_id = rq_args["rq_id"]
        return {
            "point-counts": self.prepareDTreePointCounts(dtree_h,
                rq_id, json.loads(rq_args["points"]), time_end),
            "rq-id": rq_id}

    #===============================================
    @RestAPI.ds_request
    def rq__dtree_check(self, rq_args):
        dtree_h = self._getArgDTree(rq_args,
            use_dtree = False, activate_it = False, no_cache = True)
        ret_handle = {"code": dtree_h.getCode()}
        if dtree_h.getErrorInfo() is not None:
            ret_handle.update(dtree_h.getErrorInfo())
        return ret_handle

    #===============================================
    @RestAPI.ds_request
    def rq__dtree_cmp(self, rq_args):
        dtree_h = self._getArgDTree(activate_it = False)
        assert "other" in rq_args, 'Missing request argument "other"'
        other_dtree_h = self.pickSolEntry("dtree", rq_args["other"])
        assert other_dtree_h is not None, (
            "Not found decision tree :" + rq_args["other"])
        return {"cmp": cmpTrees(
            dtree_h.getCode(), other_dtree_h.getCode())}

    #===============================================
    @RestAPI.ds_request
    def rq__recdata(self, rq_args):
        assert "rec" in rq_args, 'Missing request argument "rec"'
        return self.mRecStorage.getRecordData(int(rq_args.get("rec")))

    #===============================================
    @RestAPI.ds_request
    def rq__reccnt(self, rq_args):
        assert "rec" in rq_args, 'Missing request argument "rec"'
        return self.getViewRepr(int(rq_args["rec"]),
            details = rq_args.get("details"),
            active_samples = rq_args.get("samples"))

    #===============================================
    @RestAPI.ds_request
    def rq__dsinfo(self, rq_args):
        note = rq_args.get("note")
        if note is not None:
            with self:
                self.getMongoAgent().setNote(note)
        with self.mDataVault:
            return self.dumpDSInfo(navigation_mode = False)

    #===============================================
    @RestAPI.ds_request
    def rq__ds2ws(self, rq_args):
        assert "ws" in rq_args, 'Missing request argument "ws"'
        if "dtree" in rq_args or "code" in rq_args:
            eval_h = self._getArgDTree(rq_args)
        else:
            eval_h = self._getArgCondFilter(rq_args)
        task = SecondaryWsCreation(self, rq_args["ws"], eval_h,
            force_mode = rq_args.get("force"))
        return {"task_id": self.getApp().runTask(task)}

    #===============================================
    @RestAPI.ds_request
    def rq__ds_list(self, rq_args):
        if "dtree" in rq_args or "code" in rq_args:
            eval_h = self._getArgDTree(rq_args)
            assert "no" in rq_args, 'Missing request argument "no"'
            condition = eval_h.getActualCondition(int(rq_args["no"]))
        else:
            eval_h = self._getArgCondFilter(rq_args)
            condition = eval_h.getCondition()
        return {"task_id": self.getApp().runTask(
            RecListTask(self, condition, rq_args.get("smpcnt")))}

    #===============================================
    @RestAPI.ds_request
    def rq__tab_report(self, rq_args):
        assert "seq" in rq_args, 'Missing request argument "seq"'
        assert "schema" in rq_args, 'Missing request argument "schema"'
        seq_rec_no = json.loads(rq_args["seq"])
        tab_schema = self.getStdItem("tab-schema", rq_args["schema"]).getData()
        return [tab_schema.reportRecord(self, rec_no)
            for rec_no in seq_rec_no[:self.sMaxTabRqSize]]

    #===============================================
    @RestAPI.ds_request
    def rq__export(self, rq_args):
        filter_h = self._getArgCondFilter(rq_args)
        rec_no_seq = self.fiterRecords(filter_h.getCondition(),
            zone_data = rq_args.get("zone"))
        fname = self.getApp().makeExcelExport(
            self.getName(), self, rec_no_seq, self.getTagsMan())
        return {"kind": "excel", "fname": fname}

    #===============================================
    @RestAPI.ds_request
    def rq__csv_export(self, rq_args):
        filter_h = self._getArgCondFilter(rq_args)
        rec_no_seq = self.fiterRecords(filter_h.getCondition(),
            zone_data = rq_args.get("zone"))
        assert "schema" in rq_args, 'Missing request argument "schema"'
        tab_schema = self.getStdItem("tab-schema", rq_args["schema"]).getData()
        return ["!", "csv", reportCSV(self, tab_schema, rec_no_seq),
            [("Content-Disposition", "attachment;filename=anfisa_export.csv")]]

    #===============================================
    @RestAPI.ds_request
    def rq__solutions(self, rq_args):
        return self.reportSolutions()

    #===============================================
    @RestAPI.ds_request
    def rq__vsetup(self, rq_args):
        return {"aspects": self.mAspects.dump()}
