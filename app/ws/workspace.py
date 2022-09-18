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

import json
from array import array
from xml.sax.saxutils import escape

from app.config.a_config import AnfisaConfig
from app.model.rest_api import RestAPI
from app.model.dataset import DataSet

from .rules import RulesUnit
from .tags_man import TagsManager, MacroTaggingOperation
from .zone import FilterZoneH, PanelZoneH
from .ws_unit import loadWS_Unit
from .ws_space import WS_EvalSpace
from .ws_io import exportWS
from .val_stat import EnumStat

#===============================================
class Workspace(DataSet):
    def __init__(self, data_vault, dataset_info, dataset_path):
        DataSet.__init__(self, data_vault, dataset_info, dataset_path)
        assert self.getDSKind() == "ws"
        assert self.getRecStorage().getKind() == "disk", (
            "Missing storage kind: " + self.getRecStorage().getKind())
        self.mTabRecRand = array('q')
        self.mTabRecKey  = []
        self.mTabRecColor  = []
        self.mTabRecLabel = []
        self.mKey2Idx = None
        self.mEvalSpace = WS_EvalSpace(self,
            self._makeRecArrayFunc(self.mTabRecRand))

        self.mZygArrays = []
        for zyg_name in self.getZygUnitNames():
            var_array = array('b')
            self.mZygArrays.append(var_array)
            self.mEvalSpace._addZygUnit(zyg_name,
                self._makeRecArrayFunc(var_array))

        transcript_id_unit = None
        for unit_data in self.getFltSchema():
            unit_h = loadWS_Unit(self.mEvalSpace, unit_data)
            if unit_h is not None:
                self.mEvalSpace._addUnit(unit_h)
                if unit_h.isTranscriptID() and transcript_id_unit is None:
                    transcript_id_unit = unit_h.getName()
        self._loadPData()
        self._loadFData()
        self.mRulesUnit = RulesUnit(self)
        self.mEvalSpace._insertUnit(self.mRulesUnit, insert_idx = 0)
        if not transcript_id_unit:
            transcript_id_unit = AnfisaConfig.configOption("ws.transcript.id")
        self.mEvalSpace._setupTrIdUnit(transcript_id_unit)
        self.mTagsMan = None
        self.startService()

        self.mTagsMan = TagsManager(self, "Check-Tags")
        self.mZoneHandlers  = []
        for zone_it in self.iterStdItems("zone"):
            unit_name = zone_it["data"]
            if unit_name == "_tags":
                zone_h = self.mTagsMan
                zone_h._setTitle(zone_it["name"])
            else:
                unit_h = self.mEvalSpace.getUnit(unit_name)
                if (not unit_h):
                    continue
                if (unit_h.getMean() == "panel"
                        and "dim-name" in unit_h.getDescr()):
                    zone_h = PanelZoneH(self, zone_it["name"], unit_h)
                else:
                    zone_h = FilterZoneH(self, zone_it["name"], unit_h)
            self.mZoneHandlers.append(zone_h)

        for filter_h in self.iterSolEntries("filter"):
            filter_h.activate()
        for dtree_h in self.iterSolEntries("dtree"):
            dtree_h.activate()

    @staticmethod
    def _makeRecArrayFunc(val_array):
        return lambda rec_no: val_array[rec_no]

    def _loadPData(self):
        for _, pre_data in self.getRecStorage().iterPData():
            for key, tab in (
                    ("_rand",  self.mTabRecRand),
                    ("_key",   self.mTabRecKey),
                    ("_color", self.mTabRecColor),
                    ("_label", self.mTabRecLabel)):
                tab.append(pre_data.get(key))
        assert len(self.mTabRecRand) == self.getTotal()
        self.mKey2Idx = {key: idx for idx, key in enumerate(self.mTabRecKey)}

    def _loadFData(self):
        for rec_no, f_data in self.getRecStorage().iterFData():
            self.mEvalSpace.addItemGroup(f_data["$1"])
            for unit_h in self.mEvalSpace.iterUnits():
                unit_h.fillRecord(f_data, rec_no)
            for idx, zyg_unit_h in enumerate(
                    self.mEvalSpace.iterZygUnits()):
                self.mZygArrays[idx].append(
                    f_data.get(zyg_unit_h.getName()))

    def getEvalSpace(self):
        return self.mEvalSpace

    def getTagsMan(self):
        return self.mTagsMan

    def iterZones(self):
        return iter(self.mZoneHandlers)

    def getZone(self, name):
        for zone_h in self.mZoneHandlers:
            if zone_h.getName() == name:
                return zone_h
        return None

    @staticmethod
    def makeNegation(func_f):
        return lambda rec_no: not func_f(rec_no)

    def checkSupportStat(self, name, condition):
        if name == "_tags":
            ret_handle = {"name": "_tags", "kind": "support"}
            enum_stat = EnumStat(self.mTagsMan.getTagList())
            for rec_no, _ in condition.iterSelection():
                enum_stat.regValues(self.mTagsMan.getRecTags(rec_no))
            enum_stat.reportResult(ret_handle)
            return ret_handle
        return None

    def restrictZoneF(self, zone_data):
        ret_seq = []
        if zone_data is None:
            return ret_seq
        for zone_info in json.loads(zone_data):
            zone_name, zone_variants = zone_info[:2]
            func_f = self.getZone(zone_name).getRestrictF(zone_variants)
            if len(zone_info) > 2:
                assert zone_info[2] is False
                func_f = self.makeNegation(func_f)
            ret_seq.append(func_f)
        return ret_seq

    def getLastAspectID(self):
        return AnfisaConfig.configOption("aspect.tags.name")

    def getRecNoByKey(self, key):
        return self.mKey2Idx.get(key)

    def reportRecord(self, rec_no, rec_it_map = None, marked_set = None):
        ret = {
            "no": rec_no,
            "lb": escape(self.mTabRecLabel[rec_no]),
            "cl": AnfisaConfig.normalizeColorCode(
                self.mTabRecColor[rec_no])}
        if rec_it_map is not None:
            ret["dt"] = rec_it_map.to01()
        return ret

    def getRecKey(self, rec_no):
        return self.mTabRecKey[rec_no]

    def getRecRand(self, rec_no):
        return self.mTabRecRand[rec_no]

    def iterRecKeys(self):
        return enumerate(self.mTabRecKey)

    def fiterRecords(self, condition, zone_data = None):
        zone_fseq = self.restrictZoneF(zone_data)
        rec_no_seq = []
        for rec_no, _ in condition.iterSelection():
            if all(zone_f(rec_no) for zone_f in zone_fseq):
                rec_no_seq.append(rec_no)
        return rec_no_seq

    def getRecFilters(self, rec_no):
        ret_seq = []
        for filter_h in self.iterSolEntries("filter"):
            if filter_h.getEvalStatus() != "ok":
                continue
            filter_h.activate()
            if filter_h.getCondition().recInSelection(rec_no):
                ret_seq.append(filter_h.getName())
        return sorted(ret_seq)

    def getRecDTrees(self, rec_no):
        ret_seq = []
        for dtree_h in self.iterSolEntries("dtree"):
            if dtree_h.getEvalStatus() != "ok":
                continue
            dtree_h.activate()
            if dtree_h.getFinalCondition().recInSelection(rec_no):
                ret_seq.append(dtree_h.getName())
        return sorted(ret_seq)

    #===============================================
    @RestAPI.ws_request
    def rq__ws_list(self, rq_args):
        filter_h = self._getArgCondFilter(rq_args)
        records = []
        condition = filter_h.getCondition()
        zone_fseq = self.restrictZoneF(rq_args.get("zone"))
        for rec_no, rec_it_map in condition.iterSelection():
            if all(zone_f(rec_no) for zone_f in zone_fseq):
                records.append(self.reportRecord(rec_no, rec_it_map))
        ret_handle = {
            "ds": self.getName(),
            "total-counts": self.mEvalSpace.getTotalCounts(),
            "filtered-counts": condition.getCounts(zone_fseq),
            "records": records}
        self.visitEvaluation(filter_h, ret_handle)
        return ret_handle

    #===============================================
    @RestAPI.ws_request
    def rq__ws_tags(self, rq_args):
        assert "rec" in rq_args, 'Missing request argument "rec"'
        rec_no = int(rq_args["rec"])
        if rq_args.get("tags") is not None:
            tags_data = json.loads(rq_args.get("tags"))
            with self:
                self.mTagsMan.updateRec(rec_no, tags_data)
        rep = self.mTagsMan.makeRecReport(rec_no)
        rep["filters"] = self.getRecFilters(rec_no)
        rep["tags-state"] = self.getSolEnv().getIntVersion("tags")
        return rep

    #===============================================
    @RestAPI.ws_request
    def rq__zone_list(self, rq_args):
        zone = rq_args.get("zone")
        if zone is not None:
            return self.getZone(zone).makeValuesReport()
        return [zone_h.makeValuesReport(serial_mode = True)
            for zone_h in self.mZoneHandlers]

    #===============================================
    @RestAPI.ws_request
    def rq__tag_select(self, rq_args):
        return self.mTagsMan.reportSelectTag(
            rq_args.get("tag"))

    #===============================================
    @RestAPI.ws_request
    def rq__macro_tagging(self, rq_args):
        tag_name = rq_args["tag"]
        off_mode = (rq_args.get("off") == "true")
        if off_mode:
            rec_no_seq = []
        else:
            if "dtree" in rq_args or "code" in rq_args:
                eval_h = self._getArgDTree(rq_args)
                rec_no_seq, _ = eval_h.collectRecSeq()
            else:
                eval_h = self._getArgCondFilter(rq_args)
                rec_no_seq = self.mEvalSpace.evalRecSeq(
                    eval_h.getCondition())
        zone_fseq = self.restrictZoneF(rq_args.get("zone"))
        assert self.mTagsMan.tagIsProper(tag_name), "Missing tag: " + tag_name
        with self:
            rec_keys = set()
            for rec_no in rec_no_seq:
                if all(zone_f(rec_no) for zone_f in zone_fseq):
                    rec_keys.add(self.getRecKey(rec_no))
            if rq_args.get("delay") == "true":
                task = MacroTaggingOperation(self.mTagsMan, tag_name, rec_keys)
                return {"task_id": self.getApp().runTask(task)}
            self.mTagsMan.macroTaggingOp(tag_name, rec_keys)
        return {"tags-state": self.getSolEnv().getIntVersion("tags")}

    #===============================================
    @RestAPI.ws_request
    def rq__export_ws(self, rq_args):
        use_support = rq_args.get("support") not in ("no", "off", "0")
        use_root_doc = rq_args.get("doc") not in ("no", "off", "0")
        return exportWS(self, use_support, use_root_doc)
