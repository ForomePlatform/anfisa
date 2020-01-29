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

import gzip, json, abc
from time import time

from utils.ixbz2 import IndexBZ2
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
from app.prepare.sec_ws import SecondaryWsCreation
from .sol_broker import SolutionBroker
from .family import FamilyInfo
from .zygosity import ZygositySupport
from .rest_api import RestAPI
from .rec_list import RecListTask
#===============================================
class DataSet(SolutionBroker):
    sStatRqCount = 0

    def __init__(self, data_vault, dataset_info, dataset_path,
            sol_pack_name = None):
        SolutionBroker.__init__(self,
            dataset_info["meta"].get("data_schema", "CASE"),
            dataset_info.get("modes"))
        self.addModes(data_vault.getApp().getRunModes())
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
        self.mVData = IndexBZ2(self.mPath + "/vdata.ixbz2")

        self.mFamilyInfo = FamilyInfo(dataset_info["meta"])
        if (self.mDataInfo.get("zygosity_var")
                and 1 < len(self.mFamilyInfo) <= 10):
            self.addModes({"ZYG"})
        self.mZygSupport = None

        self.mViewContext = None
        if self.mFamilyInfo.getCohortList():
            self.mViewContext = {"cohorts": self.mFamilyInfo.getCohortMap()}
            view_aspect = AnfisaConfig.configOption("view.cohorts.aspect")
            self.mAspects[view_aspect]._setViewColMode("cohorts")
        completeDsModes(self)

        tuneAspects(self, self.mAspects)

    def startService(self):
        self.mZygSupport = ZygositySupport(self)
        tuneUnits(self)
        self.setSolEnv(self.mDataVault.makeSolutionEnv(self))

    def _setAspectHitGroup(self, aspect_name, group_attr):
        self.mAspects.setAspectHitGroup(aspect_name, group_attr)

    def descrContext(self, rq_args, rq_descr):
        rq_descr.append("kind=" + self.mDSKind)
        rq_descr.append("dataset=" + self.mName)

    @abc.abstractmethod
    def getEvalSpace(self):
        assert False

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

    def getViewSchema(self):
        return self.mAspects.dump()

    def _openFData(self):
        return gzip.open(self.mPath + "/fdata.json.gz", "rb")

    def _openPData(self):
        return gzip.open(self.mPath + "/pdata.json.gz", "rb")

    def getRecordData(self, rec_no):
        assert 0 <= rec_no < self.mTotal
        return json.loads(self.mVData[rec_no])

    def getFirstAspectID(self):
        return self.mAspects.getFirstAspectID()

    def getViewRepr(self, rec_no, details = None):
        rec_data = self.getRecordData(rec_no)
        return self.mAspects.getViewRepr(rec_data, details, self.mViewContext)

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
        assert False
        return None

    #===============================================
    def dumpDSInfo(self, navigation_mode = False):
        note, time_label = self.getMongoAgent().getNote()
        ret = {
            "name": self.mName,
            "kind": self.mDSKind,
            "note": note,
            "total": self.getTotal(),
            "base": self.getBaseDSName(),
            "root": self.getRootDSName(),
            "date-note": time_label}
        if navigation_mode:
            secondary_seq = self.mDataVault.getSecondaryWSNames(self)
            if secondary_seq:
                ret["secondary"] = [ws_h.getName() for ws_h in secondary_seq]
            ret["doc-support"] = "doc" in self.mDataInfo
        else:
            ret["src-versions"] = self.getSourceVersions()
        if "doc" in self.mDataInfo:
            ret["doc"] = self.mDataInfo["doc"]
            base_h = self.mDataVault.getBaseDS(self)
            if base_h is not None and "doc" in base_h.getDataInfo():
                ret["doc-base"] = base_h.getDataInfo()["doc"]
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
            if time_end is not None and time() > time_end:
                time_end = False
        return ret

    def prepareSelectedUnitStat(self, unit_names, condition,
            eval_h, time_end = None, point_no = None):
        ret = []
        for unit_name in unit_names:
            unit_h = self.getEvalSpace().getUnit(unit_name)
            assert not unit_h.isScreened() and unit_h.getUnitKind != "func"
            assert point_no is None or unit_h.isInDTrees()
            ret.append(unit_h.makeStat(condition, eval_h))
            if time_end is not None and time() > time_end:
                break
        return ret

    #===============================================
    def prepareDTreePointCounts(self, dtree_h,
            point_idxs = None, time_end = None):
        counts = [None] * len(dtree_h)
        needs_more = point_idxs is not None
        zero_idx = None
        if point_idxs is None:
            point_idxs = range(len(dtree_h))
        for idx in point_idxs:
            if dtree_h.pointNotActive(idx):
                counts[idx] = 0
                continue
            if not needs_more and time_end is not None and time() > time_end:
                break
            if zero_idx is not None and idx >= zero_idx:
                continue
            counts[idx] = self.getEvalSpace().evalTotalCount(
                dtree_h.getActualCondition(idx))
            needs_more = False
            if counts[idx] == 0 and dtree_h.checkZeroAfter(idx):
                zero_idx = idx
                for idx1 in range(zero_idx, len(dtree_h)):
                    counts[idx1] = 0
        return counts

    #===============================================
    def _getArgCondFilter(self, rq_args, activate_it = True):
        if "filter" in rq_args:
            filter_h = self.pickSolEntry("filter", rq_args["filter"])
        else:
            if "conditions" in rq_args:
                cond_data = json.loads(rq_args["conditions"])
                if self._REST_NeedsBackup(rq_args, 'C'):
                    cond_data = self._REST_BackupConditionsUp(cond_data)
            else:
                cond_data = ConditionMaker.condAll()
            filter_h = FilterEval(self.getEvalSpace(), cond_data)
        filter_h = self.updateSolEntry("filter", filter_h)
        if activate_it:
            filter_h.activate()
        return filter_h

    def _getArgDTree(self, rq_args, activate_it = True,
            use_dtree = True, dtree_h = None):
        if dtree_h is None:
            if use_dtree and "dtree" in rq_args:
                dtree_h = self.pickSolEntry("dtree", rq_args["dtree"])
            else:
                dtree_h = DTreeEval(self.getEvalSpace(), rq_args["code"])
        dtree_h = self.updateSolEntry("dtree", dtree_h)
        if activate_it:
            dtree_h.activate()
        return dtree_h

    sTimeCoeff = AnfisaConfig.configOption("tm.coeff")

    def _getArgTimeEnd(self, rq_args):
        if self.getEvalSpace().heavyMode() and "tm" in rq_args:
            return time() + (self.sTimeCoeff * float(rq_args["tm"])) + 1E-5
        return None

    def _makeRqId(self):
        self.sStatRqCount += 1
        return str(self.sStatRqCount) + '/' + str(time())

    #===============================================
    @classmethod
    def _REST_NeedsBackup(cls, rq_args, key):
        backup_mode = rq_args.get("back", "").upper()
        return key in backup_mode

    @classmethod
    def _REST_BackupRecords(cls, record_info_seq):
        ret_handle = []
        for rinfo in record_info_seq:
            ret_handle.append([rinfo.get(key)
                for key in ("no", "lb", "cl", "mr", "dt")])
        return ret_handle

    @classmethod
    def _REST_BackupSolList(cls, sol_info_seq):
        ret_handle = []
        for sol_info in sol_info_seq:
            ret_handle.append([sol_info.get(key, True)
                for key in ("name", "standard", None, "upd-time")])
        return ret_handle

    def _REST_BackupStatUnits(self, stat_unit_seq):
        ret_handle, avail_import, avail_import_titles = [], [], []
        for unit_stat in stat_unit_seq:
            info = [unit_stat["kind"]]
            info_descr = dict()
            for key in ("kind", "name", "vgroup", "title", "render",
                    "tooltip", "family", "affected", "detailed"):
                if key in unit_stat:
                    info_descr[key] = unit_stat[key]
            if "affected" in info_descr:
                info_descr["affected"] = self.getFamilyInfo().ids2idxset(
                    info_descr["affected"])
            info.append(info_descr)
            if unit_stat["kind"] == "func":
                if unit_stat["sub-kind"] != "inheritance-z":
                    assert False
                    continue
                info[0] = "zygosity"
                info += [self.getFamilyInfo().ids2idxset(
                    unit_stat["problem_group"]), unit_stat["variants"]]
            elif unit_stat["kind"] == "inactive":
                avail_import.append(unit_stat["name"])
                avail_import_titles.append(unit_stat.get("title"))
                continue
            elif unit_stat["kind"] == "numeric":
                info[0] = unit_stat["sub-kind"]
                info += [unit_stat.get("min"), unit_stat.get("max"),
                    unit_stat["count"], 0]
            elif (unit_stat["kind"] == "enum"
                    and unit_stat["sub-kind"].startswith("transcript")):
                info[0] = unit_stat["sub-kind"]
                info.append(unit_stat.get("variants"))
            else:
                assert unit_stat["kind"] == "enum"
                if unit_stat["sub-kind"] == "status":
                    info[0] = "status"
                info.append(unit_stat.get("variants"))
            ret_handle.append(info)
        return ret_handle, avail_import, avail_import_titles

    def _REST_BackupConditionsUp(self, cond_data_seq):
        ret_handler = []
        for cond_data in cond_data_seq:
            if cond_data[0] == "numeric":
                min_v, max_v = cond_data[2]
                ret_handler.append(["numeric",
                    cond_data[1], [min_v, True, max_v, True]])
                continue
            if cond_data[0] == "zygosity":
                ret_handler.append(["func",
                    cond_data[1], cond_data[3], cond_data[4],
                    {"sub-kind": "inheritance-z",
                        "problem_group": (self.getFamilyInfo().idxset2ids(
                            cond_data[2]))}])
                continue
            ret_handler.append(cond_data)
        return ret_handler

    def _REST_BackupConditionsDown(self, cond_data_seq):
        ret_handler = []
        for cond_data in cond_data_seq:
            if cond_data[0] == "numeric":
                min_v, _, max_v, _ = cond_data[2]
                ret_handler.append(["numeric",
                    cond_data[1], [min_v, max_v], None])
                continue
            if cond_data[0] == "func":
                func_info = cond_data[4]
                assert func_info["sub-kind"] == "inheritance-z"
                ret_handler.append(["zygosity", cond_data[1],
                    self.getFamilyInfo().ids2idxset(
                        func_info["problem_group"]),
                    cond_data[2], cond_data[3]])
                continue
            ret_handler.append(cond_data)
        return ret_handler

    #===============================================
    @RestAPI.ds_request
    def rq__stat(self, rq_args):
        time_end = self._getArgTimeEnd(rq_args)
        if "instr" in rq_args:
            filter_proc_h = self._getArgCondFilter(
                rq_args, activate_it = False)
            if not self.modifySolEntry("filter", json.loads(rq_args["instr"]),
                    filter_proc_h.getCondDataSeq()):
                assert False
        filter_h = self._getArgCondFilter(rq_args)
        condition = filter_h.getCondition()
        ret_handle = {
            "total": self.getTotal(),
            "kind": self.mDSKind,
            "stat-list": self.prepareAllUnitStat(condition,
                filter_h, time_end),
            "filter-list": self.getSolEntryList("filter"),
            "cur-filter": filter_h.getFilterName(),
            "rq_id": self._makeRqId()}
        ret_handle.update(self.getEvalSpace().reportCounts(
            filter_h.getCondition()))
        ret_handle.update(filter_h.reportInfo())

        if self._REST_NeedsBackup(rq_args, 'U'):
            stat_seq, a_imp_names, a_imp_titles = self._REST_BackupStatUnits(
                ret_handle["stat-list"])
            ret_handle["stat-list"] = stat_seq
            ret_handle["avail-import"] = a_imp_names
            ret_handle["avail-import-titles"] = a_imp_titles

        if self._REST_NeedsBackup(rq_args, 'C'):
            if "conditions" in ret_handle:
                cond_data = ret_handle["conditions"]
                ret_handle["conditions"] = self._REST_BackupConditionsDown(
                    cond_data)

        if self._REST_NeedsBackup(rq_args, 'L'):
            ret_handle["filter-list"] = self._REST_BackupSolList(
                ret_handle["filter-list"])

        return ret_handle

    #===============================================
    @RestAPI.ds_request
    def rq__dtree_stat(self, rq_args):
        time_end = self. _getArgTimeEnd(rq_args)
        dtree_h = self._getArgDTree(rq_args)
        point_no = int(rq_args["no"])
        condition = dtree_h.getActualCondition(point_no)
        ret_handle = {
            "total": self.getTotal(),
            "stat-list": self.prepareAllUnitStat(condition,
                dtree_h, time_end, point_no),
            "rq_id": self._makeRqId()}
        ret_handle.update(self.getEvalSpace().reportCounts(
            condition))
        if self._REST_NeedsBackup(rq_args, 'U'):
            stat_seq, _, _ = self._REST_BackupStatUnits(
                ret_handle["stat-list"])
            ret_handle["stat-list"] = stat_seq
        return ret_handle

    #===============================================
    @RestAPI.ds_request
    def rq__statunits(self, rq_args):
        time_end = self. _getArgTimeEnd(rq_args)
        if "dtree" in rq_args or "code" in rq_args:
            eval_h = self._getArgDTree(rq_args)
            point_no = int(rq_args["no"])
            condition = eval_h.getActualCondition(point_no)
        else:
            eval_h = self._getArgCondFilter(rq_args)
            condition, point_no = eval_h.getCondition(), None
        ret_handle = {
            "rq_id": rq_args.get("rq_id"),
            "units": self.prepareSelectedUnitStat(
                json.loads(rq_args["units"]), condition,
                eval_h, time_end, point_no)}
        if self._REST_NeedsBackup(rq_args, 'U'):
            stat_seq, _, _ = self._REST_BackupStatUnits(
                ret_handle["units"])
            ret_handle["units"] = stat_seq
        return ret_handle

    #===============================================
    @RestAPI.ds_request
    def rq__statfunc(self, rq_args):
        if "dtree" in rq_args or "code" in rq_args:
            eval_h = self._getArgDTree(rq_args)
            point_no = int(rq_args["no"])
            condition = eval_h.getActualCondition(point_no)
        else:
            eval_h = self._getArgCondFilter(rq_args)
            condition = eval_h.getCondition()
            point_no = int(rq_args["no"]) if "no" in rq_args else None

        unit_h = self.getEvalSpace().getUnit(rq_args["unit"])
        parameters = json.loads(rq_args["param"])
        return unit_h.makeParamStat(condition, parameters, eval_h, point_no)

    #===============================================
    @RestAPI.ds_request
    def rq__dtree_set(self, rq_args):
        time_end = self._getArgTimeEnd(rq_args)

        instr = rq_args.get("instr")
        if instr is not None:
            instr = json.loads(instr)
        if instr and instr[0] != "EDIT":
            dtree_proc_h = self._getArgDTree(
                rq_args, activate_it = False)
            if not self.modifySolEntry("dtree", instr,
                    dtree_proc_h.getCode()):
                assert False
        dtree_h = None
        if instr and instr[0] == "EDIT":
            parsed = ParsedDTree(self.getEvalSpace(), rq_args["code"])
            dtree_code = parsed.modifyCode(instr[1:])
            dtree_h = DTreeEval(self.getEvalSpace(), dtree_code)
        dtree_h = self._getArgDTree(rq_args, dtree_h = dtree_h)
        ret_handle = {
            "total": self.getTotal(),
            "kind": self.mDSKind,
            "counts": self.prepareDTreePointCounts(
                dtree_h, time_end = time_end),
            "dtree-list": self.getSolEntryList("dtree"),
            "rq_id": self._makeRqId()}
        ret_handle.update(dtree_h.reportInfo())

        if self._REST_NeedsBackup(rq_args, 'L'):
            ret_handle["dtree-list"] = self._REST_BackupSolList(
                ret_handle["dtree-list"])

        return ret_handle

    #===============================================
    @RestAPI.ds_request
    def rq__dtree_counts(self, rq_args):
        time_end = self. _getArgTimeEnd(rq_args)
        dtree_h = self._getArgDTree(rq_args)
        return {
            "counts": self.prepareDTreePointCounts(dtree_h,
                json.loads(rq_args["points"]), time_end),
            "rq_id": rq_args.get("rq_id")}

    #===============================================
    @RestAPI.ds_request
    def rq__dtree_check(self, rq_args):
        dtree_h = self._getArgDTree(rq_args,
            use_dtree = False, activate_it = False)
        ret_handle = {"code": dtree_h.getCode()}
        if dtree_h.getErrorInfo() is not None:
            msg_text, lineno, col_offset = dtree_h.getErrorInfo()
            ret_handle.update(dtree_h.getErrorInfo())
        return ret_handle

    #===============================================
    @RestAPI.ds_request
    def rq__dtree_cmp(self, rq_args):
        dtree_h = self._getArgDTree(activate_it = False)
        other_dtree_h = self.pickSolEntry("dtree", rq_args["other"])
        return {"cmp": cmpTrees(
            dtree_h.getCode(), other_dtree_h.getCode())}

    #===============================================
    @RestAPI.ds_request
    def rq__dsmeta(self, rq_args):
        return self.getDataInfo()["meta"]

    #===============================================
    @RestAPI.ds_request
    def rq__recdata(self, rq_args):
        return self.getRecordData(int(rq_args.get("rec")))

    #===============================================
    @RestAPI.ds_request
    def rq__reccnt(self, rq_args):
        return self.getViewRepr(int(rq_args.get("rec")),
            details = rq_args.get("details"))

    #===============================================
    @RestAPI.ds_request
    def rq__dsinfo(self, rq_args):
        note = rq_args.get("note")
        if note is not None:
            with self:
                self.getMongoAgent().setNote(note)
        return self.dumpDSInfo(navigation_mode = False)

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
    def rq__ds2ws(self, rq_args):
        if "dtree" in rq_args or "code" in rq_args:
            eval_h = self._getArgDTree(rq_args)
        else:
            eval_h = self._getArgCondFilter(rq_args)
        task = SecondaryWsCreation(self, rq_args["ws"], eval_h,
            force_mode = "force" in rq_args)
        return {"task_id": self.getApp().runTask(task)}

    #===============================================
    @RestAPI.ds_request
    def rq__ds_list(self, rq_args):
        if "dtree" in rq_args or "code" in rq_args:
            eval_h = self._getArgDTree(rq_args)
            condition = eval_h.getActualCondition(int(rq_args["no"]))
        else:
            eval_h = self._getArgCondFilter(rq_args)
            condition = eval_h.getCondition()
        return {"task_id": self.getApp().runTask(
            RecListTask(self, condition,
                self._REST_NeedsBackup(rq_args, 'R')))}

    #===============================================
    @RestAPI.ds_request
    def rq__solutions(self, rq_args):
        return self.reportSolutions()

    #===============================================
    @RestAPI.ds_request
    def rq__vsetup(self, rq_args):
        return {"aspects": self.mAspects.dump()}
