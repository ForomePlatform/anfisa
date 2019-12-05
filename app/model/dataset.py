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

import gzip, json
from time import time

from utils.ixbz2 import IndexBZ2
from app.view.asp_set import AspectSetH
from app.config.a_config import AnfisaConfig
from app.config.view_tune import tuneAspects
from app.config.solutions import completeDsModes
from app.filter.condition import ConditionMaker
from app.filter.filter_conj import FilterConjunctional
from app.filter.filter_dtree import FilterDTree
from app.filter.code_works import cmpTrees
from app.filter.dtree_parse import ParsedDTree
from .sol_space import SolutionSpace
from .sol_handler import SolutionTypeHandler
from .family import FamilyInfo
from .rest_api import RestAPI
from .comp_hets import CompHetsOperativeUnit
#===============================================
class DataSet(SolutionSpace):
    sStatRqCount = 0

    def __init__(self, data_vault, dataset_info, dataset_path,
            sol_pack_name = None):
        SolutionSpace.__init__(self,
            dataset_info.get("modes"), sol_pack_name)
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
        self.mViewContext = None
        if self.mFamilyInfo.getCohortList():
            self.mViewContext = {"cohorts": self.mFamilyInfo.getCohortMap()}
            view_aspect = AnfisaConfig.configOption("view.cohorts.aspect")
            self.mAspects[view_aspect]._setViewColMode("cohorts")
        completeDsModes(self)

        self.mUnits = []
        self.mUnitDict = dict()
        tuneAspects(self, self.mAspects)

        self.mSolAgent = None
        self.mSolHandlers = None

    def _addUnit(self, unit_h):
        self.mUnits.append(unit_h)
        assert unit_h.getName() not in self.mUnitDict, (
            "Duplicate unit name: " + unit_h.getName())
        self.mUnitDict[unit_h.getName()] = unit_h

    def _setupUnits(self):
        for unit_h in self.mUnits:
            unit_h.setup()
        CompHetsOperativeUnit.setupCondEnv(self)
        self.mSolAgent = self.mDataVault.attachSolutionAgent(self)
        self.mSolHandlers = {
            "filter": SolutionTypeHandler(self, self.mSolAgent,
                "filter", FilterConjunctional),
            "dtree": SolutionTypeHandler(self, self.mSolAgent,
                "dtree", FilterDTree)}

    def deactivate(self):
        self.mSolAgent.detachDataset(self)

    def _setAspectHitGroup(self, aspect_name, group_attr):
        self.mAspects.setAspectHitGroup(aspect_name, group_attr)

    def descrContext(self, rq_args, rq_descr):
        rq_descr.append("kind=" + self.mDSKind)
        rq_descr.append("dataset=" + self.mName)

    def getApp(self):
        return self.mDataVault.getApp()

    def heavyMode(self):
        return False

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

    def getUnit(self, unit_name):
        return self.mUnitDict.get(unit_name)

    def iterUnits(self):
        return iter(self.mUnits)

    def _openFData(self):
        return gzip.open(self.mPath + "/fdata.json.gz", "rb")

    def _openPData(self):
        return gzip.open(self.mPath + "/pdata.json.gz", "rb")

    def _getSolAgent(self):
        return self.mSolAgent

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

    def getTagsMan(self):
        return None

    def refreshSolEntries(self, key):
        if self.mSolHandlers is not None:
            with self:
                self.mSolHandlers[key].refreshSolEntries()

    def iterSolEntries(self, key):
        for info in self.mSolHandlers[key].getList():
            yield self.mSolHandlers[key].pickByName(info[0])

    #===============================================
    def dumpDSInfo(self, navigation_mode = False):
        note, time_label = self.getMongoAgent().getNote()
        ret = {
            "name": self.mName,
            "kind": self.mDSKind,
            "note": note,
            "total": self.getTotal(),
            "date-note": time_label}
        base_h = self.mDataVault.getBaseDS(self)
        if base_h is not None:
            ret["base"] = base_h.getName()
        if navigation_mode:
            secondary_seq = self.mDataVault.getSecondaryWS(self)
            if secondary_seq:
                ret["secondary"] = [ws_h.getName() for ws_h in secondary_seq]
            ret["doc-support"] = "doc" in self.mDataInfo
        else:
            ret["src-versions"] = self.getSourceVersions()
        if "doc" in self.mDataInfo:
            ret["doc"] = self.mDataInfo["doc"]
            if base_h is not None and "doc" in base_h.getDataInfo():
                ret["doc-base"] = base_h.getDataInfo()["doc"]
        if not navigation_mode:
            cur_v_group = None
            unit_groups = []
            for unit_h in self.iterUnits():
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
            for unit_h in self.getCondEnv().iterOpUnits():
                for group_info in unit_groups:
                    if group_info[0] == unit_h.getVGroup():
                        group_info[1].append(unit_h.getName())
                        unit_h = None
                        break
                if unit_h is not None:
                    unit_groups.append(
                        [unit_h.getVGroup(), [unit_h.getName()]])
            ret["unit-groups"] = unit_groups
        return ret

    #===============================================
    def prepareAllUnitStat(self, condition, repr_context,
            flt_base_h, time_end, point_no = None):
        active_stat_list = []
        for unit_h in flt_base_h.iterActiveOperativeUnits(point_no):
            if time_end is False:
                active_stat_list.append(unit_h.prepareStat())
            else:
                active_stat_list.append(unit_h.makeActiveStat(
                    condition, flt_base_h, repr_context))
            if time_end is not None and time() > time_end:
                time_end = False
        ret = []
        for unit_h in self.iterUnits():
            if unit_h.isScreened():
                continue
            if time_end is False:
                ret.append(unit_h.prepareStat())
                continue
            ret.append(unit_h.makeStat(condition, repr_context))
            if time_end is not None and time() > time_end:
                time_end = False
        for act_stat in active_stat_list:
            pos_ins = len(ret)
            for idx, stat in enumerate(ret):
                if stat[1].get("vgroup") == act_stat[1].get("vgroup"):
                    pos_ins = idx + 1
                    break
            ret.insert(pos_ins, act_stat)
        return ret

    def prepareSelectedUnitStat(self, unit_names, condition,
            repr_context, flt_base_h, time_end = None, point_no = None):
        ret = []
        op_units = dict()
        for unit_h in flt_base_h.iterActiveOperativeUnits(point_no):
            op_units[unit_h.getName()] = unit_h
        for unit_name in unit_names:
            if unit_name in op_units:
                ret.append(op_units[unit_name].makeActiveStat(
                    condition, flt_base_h, repr_context))
            else:
                unit_h = self.getUnit(unit_name)
                assert not unit_h.isScreened()
                ret.append(unit_h.makeStat(condition, repr_context))
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
            counts[idx] = self.evalTotalCount(dtree_h.getActualCondition(idx))
            needs_more = False
            if counts[idx] == 0 and dtree_h.checkZeroAfter(idx):
                zero_idx = idx
                for idx1 in range(zero_idx, len(dtree_h)):
                    counts[idx1] = 0
        return counts

    #===============================================
    def _getArgContext(self, rq_args):
        if "ctx" in rq_args:
            return json.loads(rq_args["ctx"])
        return dict()

    def _getArgCondFilter(self, rq_args, activate_it = True):
        if "filter" in rq_args:
            filter_h = self.mSolHandlers["filter"].pickByName(
                rq_args["filter"])
        else:
            if "conditions" in rq_args:
                cond_data = json.loads(rq_args["conditions"])
            else:
                cond_data = ConditionMaker.condAll()
            filter_h = FilterConjunctional(self.getCondEnv(), cond_data)
        filter_h = self.mSolHandlers["filter"].updateFltObj(filter_h)
        if activate_it:
            filter_h.activate()
        return filter_h

    def _getArgDTree(self, rq_args, activate_it = True,
            use_dtree = True, dtree_h = None):
        if dtree_h is None:
            if use_dtree and "dtree" in rq_args:
                dtree_h = self.mSolHandlers["dtree"].pickByName(
                    rq_args["dtree"])
            else:
                dtree_h = FilterDTree(self.getCondEnv(), rq_args["code"])
        dtree_h = self.mSolHandlers["dtree"].updateFltObj(dtree_h)
        if activate_it:
            dtree_h.activate()
        return dtree_h

    sTimeCoeff = AnfisaConfig.configOption("tm.coeff")

    def _getArgTimeEnd(self, rq_args):
        if self.heavyMode() and "tm" in rq_args:
            return time() + (self.sTimeCoeff * float(rq_args["tm"])) + 1E-5
        return None

    def _makeRqId(self):
        self.sStatRqCount += 1
        return str(self.sStatRqCount) + '/' + str(time())

    #===============================================
    @RestAPI.ds_request
    def rq__stat(self, rq_args):
        time_end = self._getArgTimeEnd(rq_args)
        repr_context = self._getArgContext(rq_args)
        if "instr" in rq_args:
            filter_h = self._getArgCondFilter(rq_args, activate_it = False)
            if not self.mSolHandlers["filter"].modify(rq_args["instr"],
                    filter_h.getCondData()):
                assert False
        filter_h = self._getArgCondFilter(rq_args)
        condition = filter_h.getCondition()
        ret_handle = {
            "total": self.getTotal(),
            "kind": self.mDSKind,
            "stat-list": self.prepareAllUnitStat(condition,
                repr_context, filter_h, time_end),
            "filter-list": self.mSolHandlers["filter"].getList(),
            "cur-filter": filter_h.getFilterName(),
            "rq_id": self._makeRqId()}
        ret_handle.update(self._reportCounts(filter_h.getCondition()))
        ret_handle.update(filter_h.reportInfo())
        return ret_handle

    #===============================================
    @RestAPI.ds_request
    def rq__dtree_stat(self, rq_args):
        time_end = self. _getArgTimeEnd(rq_args)
        repr_context = self._getArgContext(rq_args)
        dtree_h = self._getArgDTree(rq_args)
        point_no = int(rq_args["no"])
        condition = dtree_h.getActualCondition(point_no)
        ret_handle = {
            "total": self.getTotal(),
            "stat-list": self.prepareAllUnitStat(condition,
                repr_context, dtree_h, time_end, point_no),
            "rq_id": self._makeRqId()}
        ret_handle.update(self._reportCounts(condition))
        return ret_handle

    #===============================================
    @RestAPI.ds_request
    def rq__statunits(self, rq_args):
        time_end = self. _getArgTimeEnd(rq_args)
        repr_context = self._getArgContext(rq_args)
        if "dtree" in rq_args or "code" in rq_args:
            flt_base_h = self._getArgDTree(rq_args)
            point_no = int(rq_args["no"])
            condition = flt_base_h.getActualCondition(point_no)
        else:
            flt_base_h = self._getArgCondFilter(rq_args)
            condition, point_no = flt_base_h.getCondition(), None
        return {
            "rq_id": rq_args.get("rq_id"),
            "units": self.prepareSelectedUnitStat(
                json.loads(rq_args["units"]), condition, repr_context,
                flt_base_h, time_end, point_no)}

    #===============================================
    @RestAPI.ds_request
    def rq__dtree(self, rq_args):
        time_end = self._getArgTimeEnd(rq_args)
        dtree_h = None
        if "modify" in rq_args:
            parsed = ParsedDTree(self.getCondEnv(), rq_args["code"])
            dtree_code = parsed.modifyCode(json.loads(rq_args["modify"]))
            dtree_h = FilterDTree(self.getCondEnv(), dtree_code)
        if "instr" in rq_args:
            if dtree_h is None:
                dtree_h = self._getArgDTree(rq_args, activate_it = False)
            if not self.mSolHandlers["dtree_h"].modify(rq_args["instr"],
                    dtree_h.getCode()):
                assert False
        dtree_h = self._getArgDTree(rq_args, dtree_h = dtree_h)
        ret_handle = {
            "total": self.getTotal(),
            "kind": self.mDSKind,
            "counts": self.prepareDTreePointCounts(
                dtree_h, time_end = time_end),
            "rq_id": self._makeRqId()}
        ret_handle.update(dtree_h.reportInfo())
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
        if dtree_h.getError() is not None:
            msg_text, lineno, col_offset = dtree_h.getError()
            ret_handle.update(
                {"line": lineno, "pos": col_offset, "error": msg_text})
        return ret_handle

    #===============================================
    @RestAPI.ds_request
    def rq__dtree_cmp(self, rq_args):
        dtree_h = self._getArgDTree(activate_it = False)
        other_dtree_h = self.mSolHandlers["dtree"].pickByName(
            rq_args["other"])
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
    def rq__solutions(self, rq_args):
        return self.reportSolutions()

    #===============================================
    @RestAPI.ds_request
    def rq__vsetup(self, rq_args):
        return {"aspects": self.mAspects.dump()}
