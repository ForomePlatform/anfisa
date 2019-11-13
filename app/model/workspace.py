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

import logging, json
from xml.sax.saxutils import escape
from io import TextIOWrapper

from .rest_api import RestAPI
from .dataset import DataSet
from .tags_man import TagsManager
from .zone import FilterZoneH
from app.config.a_config import AnfisaConfig
from app.filter.condition import ConditionMaker
from app.filter.cond_op import CondOpEnv
from app.search.index import Index

#===============================================
class Workspace(DataSet):
    def __init__(self, data_vault, dataset_info, dataset_path):
        DataSet.__init__(self, data_vault, dataset_info, dataset_path)
        self.mTabRecRand = []
        self.mTabRecKey  = []
        self.mTabRecColor  = []
        self.mTabRecLabel = []

        self.mIndex = Index(self)
        self._loadPData()
        self.mTagsMan = TagsManager(self,
            AnfisaConfig.configOption("check.tags"))

        self.mIndex.setup()
        for filter_name, cond_seq, time_label in \
                self.getMongoAgent().getFilters():
            if self.mIndex.goodOpFilterName(filter_name):
                if not self.mIndex.cacheFilter(filter_name,
                        ConditionMaker.upgradeOldFormatSeq(cond_seq),
                        time_label):
                    logging.error("Filter %s for ws=%s failed" %
                        (filter_name, self.getName()))
        self.mZoneHandlers  = []
        for zone_title, unit_name in self.mIndex.getCondEnv().iterZones():
            if (unit_name == "_tags"):
                zone_h = self.mTagsMan
                zone_h._setTitle(zone_title)
            else:
                unit = self.mIndex.getUnit(unit_name)
                if (not unit):
                    continue
                zone_h = FilterZoneH(self, zone_title, unit)
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

    def getIndex(self):
        return self.mIndex

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

    def getMongoRecData(self, key):
        return self.getMongoAgent().getRecData(key)

    def setMongoRecData(self, key, data, prev_data = False):
        self.getMongoAgent().setRecData(key, data, prev_data)

    def _reportListKeys(self, rec_no_seq, rec_it_map_seq):
        marked_set = self.mTagsMan.getMarkedSet()
        ret = []
        for idx, rec_no in enumerate(rec_no_seq):
            ret.append([rec_no, escape(self.mTabRecLabel[rec_no]),
                AnfisaConfig.normalizeColorCode(self.mTabRecColor[rec_no]),
                rec_no in marked_set,
                rec_it_map_seq[idx].to01()])
        return ret

    def reportList(self, rec_no_seq, rec_it_map_seq,
            counts_transctipts, random_mode):
        rep = {
            "workspace": self.getName(),
            "total": self.getTotal(),
            "transcripts": counts_transctipts,
            "filtered": len(rec_no_seq)}
        if (random_mode and len(rec_no_seq) >
                AnfisaConfig.configOption("rand.min.size")):
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

    def filterOperation(self, instr, filter_name, cond_seq):
        op, q, flt_name = instr.partition('/')
        if self.mIndex.hasStdFilter(flt_name):
            return filter_name
        with self:
            if op == "UPDATE":
                if cond_seq:
                    cond_seq = ConditionMaker.upgradeOldFormatSeq(cond_seq)
                time_label = self.getMongoAgent().setFilter(flt_name, cond_seq)
                self.mIndex.cacheFilter(flt_name, cond_seq, time_label)
                filter_name = flt_name
            elif op == "DELETE":
                self.getMongoAgent().dropFilter(flt_name)
                self.mIndex.dropFilter(flt_name)
                flt_name = None
            else:
                assert False
        return filter_name

    #===============================================
    def _prepareContext(self, rq_args):
        if "ctx" in rq_args:
            return json.loads(rq_args["ctx"])
        return dict()

    def _prepareConditions(self, rq_args, with_comp = True):
        #comp_data = (json.loads(rq_args["compiled"])
        #    if with_comp and "compiled" in rq_args else None)
        comp_data = None
        op_cond = CondOpEnv(self.mIndex.getCondEnv(), comp_data,
            json.loads(rq_args["conditions"])
            if "conditions" in rq_args else ConditionMaker.condAll())
        return op_cond, op_cond.getResult()

    #===============================================
    @RestAPI.ws_request
    def rq__list(self, rq_args):
        modes = rq_args.get("m", "").upper()
        if "filter" in rq_args:
            condition = self.mIndex.getFilterOpEnv(
                rq_args["filter"]).getResult()
            assert "conditions" not in rq_args
        else:
            _, condition = self._prepareConditions(rq_args)
        if "zone" in rq_args:
            zone_name, variants = json.loads(rq_args["zone"])
            zone_f = self.getZone(zone_name).getRestrictF(variants)
        else:
            zone_f = None
        rec_no_seq, rec_it_map_seq = [], []
        count_transctipts = 0
        for rec_no, rec_it_map in condition.iterSelection():
            if zone_f is not None and not zone_f(rec_no):
                continue
            rec_no_seq.append(rec_no)
            rec_it_map_seq.append(rec_it_map)
            count_transctipts += rec_it_map.count()
        return self.reportList(rec_no_seq, rec_it_map_seq,
            [count_transctipts, condition.getCondEnv().getTotalCount()],
            'S' in modes)

    #===============================================
    @RestAPI.ws_request
    def rq__stat(self, rq_args):
        modes = rq_args.get("m", "").upper()
        if "instr" in rq_args:
            op_env, _ = self._prepareConditions(rq_args, False)
            filter_name = self.filterOperation(rq_args["instr"],
                rq_args.get("filter"), op_env.getCondSeq())
            if filter_name is not None:
                op_env = self.mIndex.getFilterOpEnv(filter_name)
        elif "filter" in rq_args:
            assert "conditions" not in rq_args
            op_env = self.mIndex.getFilterOpEnv(rq_args["filter"])
        else:
            op_env, _ = self._prepareConditions(rq_args)
        repr_context = self._prepareContext(rq_args)
        return self.mIndex.makeStatReport(op_env, 'R' in modes, repr_context)

    #===============================================
    @RestAPI.ws_request
    def rq__statunits(self, rq_args):
        _, condition = self._prepareConditions(rq_args)
        repr_context = self._prepareContext(rq_args)
        return {
            "units": [self.mIndex.makeUnitStatReport(
                unit_name, condition, repr_context)
                for unit_name in json.loads(rq_args["units"])]}

    #===============================================
    @RestAPI.ws_request
    def rq__tags(self, rq_args):
        modes = rq_args.get("m", "").upper()
        rec_no = int(rq_args.get("rec"))
        if rq_args.get("tags") is not None:
            tags_to_update = json.loads(rq_args.get("tags"))
            with self:
                self.mTagsMan.updateRec(rec_no, tags_to_update)
        rep = self.mTagsMan.makeRecReport(rec_no)
        rep["filters"] = self.mIndex.getRecFilters(rec_no, 'R' in modes)
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
    def rq__rules_data(self, rq_args):
        modes = rq_args.get("m", "").upper()
        return self.mIndex.getRulesUnit().getJSonData('R' in modes)

    #===============================================
    @RestAPI.ws_request
    def rq__rules_modify(self, rq_args):
        modes = rq_args.get("m", "").upper()
        item = rq_args.get("it")
        content = rq_args.get("cnt")
        with self:
            return self.mIndex.getRulesUnit().modifyRulesData(
                'R' in modes, item, content)

    #===============================================
    @RestAPI.ws_request
    def rq__tag_select(self, rq_args):
        return self.mTagsMan.reportSelectTag(
            rq_args.get("tag"))

    #===============================================
    @RestAPI.ws_request
    def rq__export(self, rq_args):
        if "filter" in rq_args:
            condition = self.mIndex.getFilterOpEnv(
                rq_args["filter"]).getResult()
            assert "conditions" not in rq_args
        else:
            _, condition = self._prepareConditions(rq_args)
        if "zone" in rq_args:
            zone_name, variants = json.loads(rq_args["zone"])
            zone_f = self.getZone(zone_name).getRestrictF(variants)
        else:
            zone_f = None
        rec_no_seq = []
        for rec_no, _ in condition.iterSelection():
            if zone_f is not None and not zone_f(rec_no):
                continue
            rec_no_seq.append(rec_no)
        fname = self.getApp().makeExcelExport(
            self.getName(), self, rec_no_seq, self.mTagsMan)
        return {"kind": "excel", "fname": fname}

    #===============================================
    @RestAPI.ws_request
    def rq__vsetup(self, rq_args):
        return self.getViewSetupReport()

