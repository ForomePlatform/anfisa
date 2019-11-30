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
from xml.sax.saxutils import escape
from io import TextIOWrapper

from app.config.a_config import AnfisaConfig
from app.model.rest_api import RestAPI
from app.model.dataset import DataSet
from .tags_man import TagsManager
from .zone import FilterZoneH
from .ws_unit import loadWS_Unit
from .ws_cond import WS_CondEnv

#===============================================
class Workspace(DataSet):
    def __init__(self, data_vault, dataset_info, dataset_path):
        DataSet.__init__(self, data_vault, dataset_info, dataset_path)
        self.addModes({"WS"})
        self.mCondEnv = WS_CondEnv(self)
        self.mTabRecRand = []
        self.mTabRecKey  = []
        self.mTabRecColor  = []
        self.mTabRecLabel = []

        # self.mRulesUnit = RulesEvalUnit(self)
        # self._addUnit(self.mRulesUnit)
        for unit_data in self.getFltSchema():
            unit_h = loadWS_Unit(self, unit_data)
            if unit_h is not None:
                self._addUnit(unit_h)
        self._loadPData()
        self._loadFData()
        self._setupUnits()

        self.mTagsMan = TagsManager(self,
            AnfisaConfig.configOption("check.tags"))

        self.mZoneHandlers  = []
        for zone_it in self.iterStdItems("zone"):
            unit_name = zone_it.getData()
            if (unit_name == "_tags"):
                zone_h = self.mTagsMan
                zone_h._setTitle(zone_it.getName())
            else:
                unit = self.getUnit(unit_name)
                if (not unit):
                    continue
                zone_h = FilterZoneH(self, zone_it.getName(), unit)
            self.mZoneHandlers.append(zone_h)

        self._setAspectHitGroup(
            *AnfisaConfig.configOption("transcript.view.setup"))

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
                self.mCondEnv.addItemGroup(inp_data["$1"])
                for unit_h in self.iterUnits():
                    unit_h.fillRecord(inp_data, rec_no)
                # self.mRulesUnit.fillRulesPart(inp_data, rec_no)

    def getCondEnv(self):
        return self.mCondEnv

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

    def _reportListKeys(self, rec_no_seq, rec_it_map_seq):
        marked_set = self.mTagsMan.getMarkedSet()
        ret = []
        for idx, rec_no in enumerate(rec_no_seq):
            ret.append([rec_no, escape(self.mTabRecLabel[rec_no]),
                AnfisaConfig.normalizeColorCode(self.mTabRecColor[rec_no]),
                rec_no in marked_set,
                rec_it_map_seq[idx].to01()])
        return ret

    def _reportCounts(self, condition):
        count, count_items, total_items = condition.getAllCounts()
        return {
            "count": count,
            "transcripts": [count_items, total_items]}

    def reportList(self, rec_no_seq, rec_it_map_seq,
            counts_transctipts, random_mode = False):
        rep = {
            "workspace": self.getName(),
            "total": self.getTotal(),
            "transcripts": counts_transctipts,
            "filtered": len(rec_no_seq)}
        if (random_mode and len(rec_no_seq)
                > AnfisaConfig.configOption("rand.min.size")):
            sheet = [(self.mTabRecRand[rec_no], idx)
                for idx, rec_no in enumerate(rec_no_seq)]
            sheet.sort()
            del sheet[AnfisaConfig.configOption("rand.sample.size"):]
            rec_no_seq = [rec_no_seq[idx] for _, idx in sheet]
            rec_it_map_seq = [rec_it_map_seq[idx] for _, idx in sheet]
            rep["list-mode"] = "samples"
        else:
            rep["list-mode"] = "complete"
        rep["records"] = self._reportListKeys(rec_no_seq, rec_it_map_seq)
        return rep

    def getRecKey(self, rec_no):
        return self.mTabRecKey[rec_no]

    def iterRecKeys(self):
        return enumerate(self.mTabRecKey)

    def evalTotalCount(self, condition):
        if condition is None:
            return self.getTotal()
        return condition.getAllCounts()[0]

    def evalDetailedTotalCount(self, condition):
        if condition is None:
            return self.mCondEnv.getTotalCount()
        return condition.getItemCount()

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
            if not filter_h.noErrors():
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
        rec_no_seq, rec_it_map_seq = [], []
        count_transctipts = 0
        for rec_no, rec_it_map in filter_h.getCondition().iterSelection():
            if zone_f is not None and not zone_f(rec_no):
                continue
            rec_no_seq.append(rec_no)
            rec_it_map_seq.append(rec_it_map)
            count_transctipts += rec_it_map.count()
        return self.reportList(rec_no_seq, rec_it_map_seq,
            [count_transctipts, self.mCondEnv.getTotalCount()])

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

    #===============================================
    #@RestAPI.ws_request
    #def rq__rules_data(self, rq_args):
    #    return self.mRulesUnit.getJSonData()

    #===============================================
    #@RestAPI.ws_request
    #def rq__rules_modify(self, rq_args):
    #    item = rq_args.get("it")
    #    content = rq_args.get("cnt")
    #    with self:
    #        return self.mRulesUnit.modifyRulesData(
    #            item, content)
