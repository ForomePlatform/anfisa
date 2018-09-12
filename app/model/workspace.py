from app.search.index import Index
from .mongo_db import MongoConnector
from .tags_man import TagsManager
from .zone import FilterZoneH

#===============================================
class Workspace:
    def __init__(self, name, legend, data_set, mongo_path,
            mongo_host = None, mongo_port = None):
        self.mName = name
        self.mLegend = legend
        self.mDataSet = data_set
        self.mMongoConn = MongoConnector(mongo_path,
            mongo_host, mongo_port)
        self.mViewSetup = self.mDataSet.getViewSetup()
        self.mTagsMan = TagsManager(self,
            self.mViewSetup.configOption("check.tags"))
        self.mIndex  = Index(self.mDataSet, self.mLegend)
        for filter_name, conditions in self.mMongoConn.getFilters():
            if not self.mLegend.hasFilter(filter_name):
                self.mIndex.cacheFilter(filter_name, conditions)
        self.mZoneHandlers  = []
        for zone_title, unit_name in self.mViewSetup.configOption("zones"):
            if (unit_name == "_tags"):
                zone_h = self.mTagsMan
                zone_h._setTitle(zone_title)
            else:
                zone_h = FilterZoneH(self, zone_title,
                    self.mLegend.getUnit(unit_name))
            self.mZoneHandlers.append(zone_h)

    def getName(self):
        return self.mName

    def getMongoConn(self):
        return self.mMongoConn

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
        return self.mViewSetup.getAspects()[0].getName()

    def getLastAspectID(self):
        return self.mViewSetup.configOption("aspect.tags.name")

    def getRulesData(self, expert_mode):
        return self.mLegend.getRulesUnit().getJSonData(expert_mode)

    def modifyRulesData(self, expert_mode, item, content):
        report = self.mLegend.getRulesUnit().modifyHotData(
            expert_mode, item, content)
        if report["status"] == "OK":
            self.mIndex.updateRulesEnv()
        return report

    def makeTagsJSonReport(self, rec_no,
            expert_mode, tags_to_update = None):
        report = self.mTagsMan.makeRecReport(rec_no, tags_to_update)
        report["filters"] = self.mIndex.getRecFilters(rec_no)
        return report

    def makeStatReport(self, filter_name, expert_mode, conditions, instr):
        if instr:
            op, q, flt_name = instr.partition('/')
            if not self.mLegend.hasFilter(flt_name):
                if op == "UPDATE":
                    self.mMongoConn.setFilter(flt_name, conditions)
                    self.mIndex.cacheFilter(flt_name, conditions)
                    filter_name = flt_name
                elif op == "DROP":
                    self.mMongoConn.dropFilter(flt_name)
                    self.mIndex.dropFilter(flt_name)
                else:
                    assert False
        return self.mIndex.makeStatReport(
            filter_name, expert_mode, conditions)
