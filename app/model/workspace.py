from threading import Lock
from app.search.index import Index
from .tags_man import TagsManager
from .zone import FilterZoneH

#===============================================
class Workspace:
    def __init__(self, name, legend, data_set, mongo_ws):
        self.mName = name
        self.mLegend = legend
        self.mDataSet = data_set
        self.mMongoWS = mongo_ws
        self.mViewSetup = self.mDataSet.getViewSetup()
        self.mLock  = Lock()
        self.mTagsMan = TagsManager(self,
            self.mViewSetup.configOption("check.tags"))
        self.mIndex  = Index(self.mDataSet, self.mLegend)
        for filter_name, conditions in self.mMongoWS.getFilters():
            if not self.mLegend.hasFilter(filter_name):
                try:
                    self.mIndex.cacheFilter(filter_name, conditions)
                except Exception as ex:
                    print str(ex)
        self.mZoneHandlers  = []
        for zone_title, unit_name in self.mViewSetup.configOption("zones"):
            if (unit_name == "_tags"):
                zone_h = self.mTagsMan
                zone_h._setTitle(zone_title)
            else:
                zone_h = FilterZoneH(self, zone_title,
                    self.mLegend.getUnit(unit_name))
            self.mZoneHandlers.append(zone_h)
        par_data = self.mMongoWS.getRulesParamValues()
        if par_data is not None:
            self.mLegend.getRulesUnit().changeParamEnv(par_data)

    def __enter__(self):
        self.mLock.acquire()
        return self

    def __exit__(self, type, value, traceback):
        self.mLock.release()

    def getName(self):
        return self.mName

    def getDataSet(self):
        return self.mDataSet

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

    def getFirstAspectID(self):
        return self.mViewSetup.getFirstAspectID()

    def getLastAspectID(self):
        return self.mViewSetup.configOption("aspect.tags.name")

    def getRulesData(self, research_mode):
        return self.mLegend.getRulesUnit().getJSonData(research_mode)

    def modifyRulesData(self, research_mode, item, content):
        with self:
            report, par_data = self.mLegend.getRulesUnit().modifyRulesData(
                research_mode, item, content)
            if report["status"] == "OK":
                self.mIndex.updateRulesEnv()
                if par_data is not None:
                    self.mMongoWS.setRulesParamValues(par_data)
        return report

    def makeTagsJSonReport(self, rec_no,
            research_mode, tags_to_update = None):
        update_info = None
        if tags_to_update is not None:
            with self:
                update_info = self.mTagsMan.updateRec(rec_no, tags_to_update)
        report = self.mTagsMan.makeRecReport(rec_no, update_info)
        report["filters"] = self.mIndex.getRecFilters(rec_no)
        report["tags-version"] = self.mTagsMan.getIntVersion()
        return report

    def makeStatReport(self, filter_name, research_mode, conditions, instr):
        if instr:
            op, q, flt_name = instr.partition('/')
            if not self.mLegend.hasFilter(flt_name):
                with self:
                    if op == "UPDATE":
                        self.mMongoWS.setFilter(flt_name, conditions)
                        self.mIndex.cacheFilter(flt_name, conditions)
                        filter_name = flt_name
                    elif op == "DROP":
                        self.mMongoWS.dropFilter(flt_name)
                        self.mIndex.dropFilter(flt_name)
                    else:
                        assert False
        return self.mIndex.makeStatReport(
            filter_name, research_mode, conditions)

    def getMongoRecData(self, key):
        return self.mMongoWS.getRecData(key)

    def setMongoRecData(self, key, data, prev_data = False):
        self.mMongoWS.setRecData(key, data, prev_data)

    def getWSNote(self, note = None):
        if note is not None:
            self.mMongoWS.setWSNote(note)
        return self.mMongoWS.getWSNote()

    def getJSonObj(self):
        return {"name": self.mName, "note": self.getWSNote()}
