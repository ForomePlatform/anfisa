from search.hot_index import HotIndex
from mongo_db import MongoConnector
from tags_man import TagsManager
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
        self.mTagsMan = TagsManager(self)
        self.mIndex  = HotIndex(self.mDataSet, self.mLegend)

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

    def getFirstAspectID(self):
        return self.mViewSetup.getAspects()[0].getName()

    def getLastAspectID(self):
        return self.mViewSetup().configOption("aspect.hot.name")

    def getHotEvalData(self, expert_mode):
        return self.mLegend.getHotUnit().getJSonData(expert_mode)

    def modifyHotEvalData(self, hot_setup, expert_mode, item, content):
        report = self.mLegend.getHotUnit().modifyHotData(
            hot_setup, expert_mode, item, content)
        if report["status"] == "OK":
            self.mIndex.updateHotColumns()
        return report

    def makeTagsJSonReport(self, rec_no,
            expert_mode, tags_to_update = None):
        report = self.mTagsMan.makeRecReport(rec_no, tags_to_update)
        report["filters"] = self.mIndex.getRecFilters(
            rec_no, expert_mode),
        return report

