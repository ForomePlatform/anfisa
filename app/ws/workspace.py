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
from io import TextIOWrapper

from app.config.a_config import AnfisaConfig
from app.model.rest_api import RestAPI
from app.model.dataset import DataSet
from .rules import RulesUnit
from .tags_man import TagsManager
from .zone import FilterZoneH
from .ws_unit import loadWS_Unit
from .ws_space import WS_EvalSpace

#===============================================
class Workspace(DataSet):
    def __init__(self, data_vault, dataset_info, dataset_path):
        DataSet.__init__(self, data_vault, dataset_info, dataset_path)
        self.addModes({"WS"})
        self.mTabRecRand = array('q')
        self.mTabRecKey  = []
        self.mTabRecColor  = []
        self.mTabRecLabel = []
        self.mEvalSpace = WS_EvalSpace(self,
            self._makeRecArrayFunc(self.mTabRecRand))

        self.mZygArrays = []
        for zyg_name in self.getZygUnitNames():
            var_array = array('b')
            self.mZygArrays.append(var_array)
            self.mEvalSpace._addZygUnit(zyg_name,
                self._makeRecArrayFunc(var_array))

        for unit_data in self.getFltSchema():
            unit_h = loadWS_Unit(self.mEvalSpace, unit_data)
            if unit_h is not None:
                self.mEvalSpace._addUnit(unit_h)
        self._loadPData()
        self._loadFData()
        self.mRulesUnit = RulesUnit(self)
        self.mEvalSpace._insertUnit(self.mRulesUnit, insert_idx = 0)
        self.startService()

        self.mTagsMan = TagsManager(self,
            AnfisaConfig.configOption("check.tags"))

        self.mZoneHandlers  = []
        for zone_it in self.iterStdItems("zone"):
            unit_name = zone_it.getData()
            if (unit_name == "_tags"):
                zone_h = self.mTagsMan
                zone_h._setTitle(zone_it.getName())
            else:
                unit_h = self.mEvalSpace.getUnit(unit_name)
                if (not unit_h):
                    continue
                zone_h = FilterZoneH(self, zone_it.getName(), unit_h)
            self.mZoneHandlers.append(zone_h)

        if self.getDataSchema() == "CASE":
            self._setAspectHitGroup(
                *AnfisaConfig.configOption("transcript.view.setup"))

        for filter_h in self.iterSolEntries("filter"):
            filter_h.activate()
        for dtree_h in self.iterSolEntries("dtree"):
            dtree_h.activate()

    @staticmethod
    def _makeRecArrayFunc(val_array):
        return lambda rec_no: val_array[rec_no]

    def _loadPData(self):
        with self._openPData() as inp:
            pdata_inp = TextIOWrapper(inp,
                encoding = "utf-8", line_buffering = True)
            for line in pdata_inp:
                pre_data = json.loads(line.strip())
                for key, tab in (
                        ("_rand",  self.mTabRecRand),
                        ("_key",   self.mTabRecKey),
                        ("_color", self.mTabRecColor),
                        ("_label", self.mTabRecLabel)):
                    tab.append(pre_data.get(key))
        assert len(self.mTabRecRand) == self.getTotal()

    def _loadFData(self):
        with self._openFData() as inp:
            fdata_inp = TextIOWrapper(inp,
                encoding = "utf-8", line_buffering = True)
            for rec_no, line in enumerate(fdata_inp):
                inp_data = json.loads(line.strip())
                self.mEvalSpace.addItemGroup(inp_data["$1"])
                for unit_h in self.mEvalSpace.iterUnits():
                    unit_h.fillRecord(inp_data, rec_no)
                for idx, zyg_unit_h in enumerate(
                        self.mEvalSpace.iterZygUnits()):
                    self.mZygArrays[idx].append(
                        inp_data.get(zyg_unit_h.getName()))

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

    def getLastAspectID(self):
        return AnfisaConfig.configOption("aspect.tags.name")

    def reportRecord(self, rec_no, rec_it_map = None, marked_set = None):
        ret = {
            "no": rec_no,
            "lb": escape(self.mTabRecLabel[rec_no]),
            "cl": AnfisaConfig.normalizeColorCode(
                self.mTabRecColor[rec_no])}
        if marked_set is not None:
            ret["mr"] = rec_no in marked_set
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
        zone_f = None
        if zone_data is not None:
            zone_name, variants = json.loads(zone_data)
            zone_f = self.getZone(zone_name).getRestrictF(variants)
        rec_no_seq = []
        for rec_no, _ in condition.iterSelection():
            if zone_f is not None and not zone_f(rec_no):
                continue
            rec_no_seq.append(rec_no)
        return rec_no_seq

    def getRecFilters(self, rec_no):
        ret_handle = []
        for filter_h in self.iterSolEntries("filter"):
            if filter_h.getEvalStatus() != "ok":
                continue
            filter_h.activate()
            if filter_h.getCondition().recInSelection(rec_no):
                ret_handle.append(filter_h.getFilterName())
        return ret_handle

    #===============================================
    @RestAPI.ws_request
    def rq__list(self, rq_args):
        filter_h = self._getArgCondFilter(rq_args)
        if "zone" in rq_args:
            zone_name, variants = json.loads(rq_args["zone"])
            zone_f = self.getZone(zone_name).getRestrictF(variants)
        else:
            zone_f = None
        counts = [0, 0]
        records = []
        marked_set = self.mTagsMan.getMarkedSet()
        for rec_no, rec_it_map in filter_h.getCondition().iterSelection():
            if zone_f is not None and not zone_f(rec_no):
                continue
            records.append(self.reportRecord(rec_no, rec_it_map, marked_set))
            counts[0] += 1
            counts[1] += rec_it_map.count()
        ret_handle = {
            "ds": self.getName(),
            "total-counts": self.mEvalSpace.getTotalCounts(),
            "filtered-counts": counts,
            "records": records}
        if self._REST_NeedsBackup(rq_args, 'R'):
            ret_handle["records"] = self._REST_BackupRecords(
                ret_handle["records"])
        return ret_handle

    #===============================================
    @RestAPI.ws_request
    def rq__tags(self, rq_args):
        rec_no = int(rq_args.get("rec"))
        if rq_args.get("tags") is not None:
            tags_to_update = json.loads(rq_args.get("tags"))
            with self:
                self.mTagsMan.updateRec(rec_no, tags_to_update)
        rep = self.mTagsMan.makeRecReport(rec_no)
        rep["filters"] = self.getRecFilters(rec_no)
        rep["tags-version"] = self.mTagsMan.getIntVersion()
        return rep

    #===============================================
    @RestAPI.ws_request
    def rq__zone_list(self, rq_args):
        zone = rq_args.get("zone")
        if zone is not None:
            return self.getZone(zone).makeValuesReport()
        return [[zone_h.getName(), zone_h.getTitle()]
            for zone_h in self.mZoneHandlers]

    #===============================================
    @RestAPI.ws_request
    def rq__tag_select(self, rq_args):
        return self.mTagsMan.reportSelectTag(
            rq_args.get("tag"))
