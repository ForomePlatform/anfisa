from search.hot_index import HotIndex
from mongo_db import MongoConnector

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
        self.mIndex  = HotIndex(self.mDataSet, self.mLegend)

    def getName(self):
        return self.mName

    def getMongoPath(self):
        return self.mMongoPath

    def getDataSet(self):
        return self.mDataSet

    def getIndex(self):
        return self.mIndex

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
        rec_key = self.mDataSet.getRecKey(rec_no)
        if tags_to_update is not None:
            self.mMongoConn.setRecData(rec_key, tags_to_update)
        return {
            "filters": self.mIndex.getRecFilters(rec_no, expert_mode),
            "tags": self.mMongoConn.getRecData(rec_key)}

