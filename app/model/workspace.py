import logging, json
from xml.sax.saxutils import escape

from .rest_api import RestAPI
from .dataset import DataSet
from .tags_man import TagsManager
from .zone import FilterZoneH
from app.config.a_config import AnfisaConfig
from app.filter.condition import ConditionMaker
from app.search.index import Index

#===============================================
class Workspace(DataSet):
    def __init__(self, data_vault, dataset_info, dataset_path):
        DataSet.__init__(self, data_vault, dataset_info, dataset_path)
        self.mTabRecRand = []
        self.mTabRecKey  = []
        self.mTabRecColor  = []
        self.mTabRecLabel = []

        self.mMongoWS = (self.mDataVault.getApp().getMongoConnector().
            getWSAgent(self.getMongoName()))
        self.mIndex = Index(self)
        self._loadPData()
        self.mTagsMan = TagsManager(self,
            AnfisaConfig.configOption("check.tags"))

        for filter_name, cond_seq, time_label in self.mMongoWS.getFilters():
            if self.mIndex.goodOpFilterName(filter_name):
                try:
                    self.mIndex.cacheFilter(filter_name,
                        ConditionMaker.upgradeOldFormatSeq(cond_seq),
                        time_label)
                except Exception as ex:
                    logging.error("Exception on load filter %s:\n %s" %
                        filter_name, str(ex))
        self.mZoneHandlers  = []
        for zone_title, unit_name in AnfisaConfig.configOption("zones"):
            if (unit_name == "_tags"):
                zone_h = self.mTagsMan
                zone_h._setTitle(zone_title)
            else:
                zone_h = FilterZoneH(self, zone_title,
                    self.mIndex.getUnit(unit_name))
            self.mZoneHandlers.append(zone_h)

    def _loadPData(self):
        with self._openPData() as inp:
            for line in inp:
                pre_data = json.loads(line.decode("utf-8"))
                for key, tab in (
                        ("_rand",  self.mTabRecRand),
                        ("_key",   self.mTabRecKey),
                        ("_color", self.mTabRecColor),
                        ("_label", self.mTabRecLabel)):
                    tab.append(pre_data.get(key))
        assert len(self.mTabRecRand) == self.getTotal()

    def getName(self):
        return self.mName

    def getIndex(self):
        return self.mIndex

    def getTagsMan(self):
        return self.mTagsMan

    def getMongoWS(self):
        return self.mMongoWS

    def iterZones(self):
        return iter(self.mZoneHandlers)

    def getZone(self, name):
        for zone_h in self.mZoneHandlers:
            if zone_h.getName() == name:
                return zone_h
        return None

    def getLastAspectID(self):
        return AnfisaConfig.configOption("aspect.tags.name")

    def dump(self):
        note, time_label = self.mMongoWS.getWSNote()
        return {
            "name": self.mName,
            "note": note,
            "time": time_label}

    def getMongoRecData(self, key):
        return self.mMongoWS.getRecData(key)

    def setMongoRecData(self, key, data, prev_data = False):
        self.mMongoWS.setRecData(key, data, prev_data)

    def _reportListKeys(self, rec_no_seq):
        marked_set = self.mTagsMan.getMarkedSet()
        ret = []
        for rec_no in rec_no_seq:
            ret.append([rec_no, escape(self.mTabRecLabel[rec_no]),
                AnfisaConfig.normalizeColorCode(self.mTabRecColor[rec_no]),
                rec_no in marked_set])
        return ret

    def reportList(self, rec_no_seq, random_mode):
        rep = {
            "workspace": self.getName(),
            "total": self.getTotal()}
        rep["filtered"] = len(rec_no_seq)

        if (random_mode and len(rec_no_seq) >
                AnfisaConfig.configOption("rand.min.size")):
            sheet = [(self.mTabRecRand[rec_no], rec_no)
                for rec_no in rec_no_seq]
            sheet.sort()
            del sheet[AnfisaConfig.configOption("rand.sample.size"):]
            reduced_rec_no_seq = [rec_no for hash, rec_no in sheet]
            rep["records"] = self._reportListKeys(reduced_rec_no_seq)
            rep["list-mode"] = "samples"
        else:
            rep["records"] = self._reportListKeys(rec_no_seq)
            rep["list-mode"] = "complete"
        return rep

    def getRecKey(self, rec_no):
        return self.mTabRecKey[rec_no]

    def iterRecKeys(self):
        return enumerate(self.mTabRecKey)

    def filterOperation(self, instr, filter_name, cond_seq):
        if instr is None:
            return filter_name
        op, q, flt_name = instr.partition('/')
        if self.mIndex.hasStdFilter(flt_name):
            return filter_name
        with self:
            if op == "UPDATE":
                if cond_seq:
                    cond_seq = ConditionMaker.upgradeOldFormatSeq(cond_seq)
                time_label = self.mMongoWS.setFilter(flt_name, cond_seq)
                self.mIndex.cacheFilter(flt_name, cond_seq, time_label)
                filter_name = flt_name
            elif op in {"DROP", "DELETE"}:
                self.mMongoWS.dropFilter(flt_name)
                self.mIndex.dropFilter(flt_name)
            else:
                assert False
        return filter_name

    def _getCond(self, rq_args):
        if "conditions" in rq_args:
            cond_seq = json.loads(rq_args["conditions"])
            return cond_seq, self.getIndex().parseCondSeq(cond_seq)
        return None, None

    #===============================================
    @RestAPI.ws_request
    def rq__list(self, rq_args):
        modes = rq_args.get("m", "").upper()
        _, condition = self._getCond(rq_args)
        filter_name = rq_args.get("filter")
        if filter_name == "null":
            filter_name = None
        rec_no_seq = self.mIndex.getRecNoSeq(filter_name, condition)
        zone_data = rq_args.get("zone")
        if zone_data is not None:
            zone_name, variants = json.loads(zone_data)
            rec_no_seq = self.getZone(zone_name).restrict(
                rec_no_seq, variants)
        return self.reportList(sorted(rec_no_seq), 'S' in modes)

    #===============================================
    @RestAPI.ws_request
    def rq__stat(self, rq_args):
        modes = rq_args.get("m", "").upper()
        filter_name = rq_args.get("filter")
        cond_seq, _ = self._getCond(rq_args)
        filter_name = self.filterOperation(rq_args.get("instr"),
            filter_name, cond_seq)
        if "ctx" in rq_args:
            repr_context = json.loads(rq_args["ctx"])
        else:
            repr_context = dict()
        return self.mIndex.makeStatReport(
            filter_name, 'R' in modes, cond_seq, repr_context)

    #===============================================
    @RestAPI.ws_request
    def rq__statunit(self, rq_args):
        _, condition = self._getCond(rq_args)
        if "ctx" in rq_args:
            repr_context = json.loads(rq_args["ctx"])
        else:
            repr_context = dict()
        return self.mIndex.makeUnitStatReport(rq_args["unit"],
            condition, repr_context)

    #===============================================
    @RestAPI.ws_request
    def rq__statunits(self, rq_args):
        _, condition = self._getCond(rq_args)
        if "ctx" in rq_args:
            repr_context = json.loads(rq_args["ctx"])
        else:
            repr_context = dict()
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
        filter_name = rq_args.get("filter")
        if filter_name == "null":
            filter_name = None
        _, condition = self._getCond(rq_args)
        rec_no_seq = self.getIndex().getRecNoSeq(
            filter_name, condition)
        zone_data = rq_args.get("zone")
        if zone_data is not None:
            zone_name, variants = json.loads(zone_data)
            rec_no_seq = self.getZone(zone_name).restrict(
                rec_no_seq, variants)
        fname = self.getApp().makeExcelExport(
            self.getName(), self, rec_no_seq, self.mTagsMan)
        return {"kind": "excel", "fname": fname}

    #===============================================
    @RestAPI.ws_request
    def rq__vsetup(self, rq_args):
        return self.getViewSetupReport()

    #===============================================
    @RestAPI.ws_request
    def rq__recdata(self, rq_args):
        return self.getRecordData(int(rq_args.get("rec")))

    #===============================================
    @RestAPI.ws_request
    def rq__reccnt(self, rq_args):
        modes = rq_args.get("m", "").upper()
        rec_no = int(rq_args.get("rec"))
        return self.getViewRepr(rec_no, 'R' in modes)

    #===============================================
    @RestAPI.ws_request
    def rq__wsnote(self, rq_args):
        note = rq_args.get("note")
        if note is not None:
            with self:
                self.mMongoWS.setWSNote(note)
        return self.dump()
