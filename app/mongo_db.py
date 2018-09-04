from pymongo import MongoClient

#===============================================
class MongoConnector:
    def __init__(self, path, host = None, port = None):
        self.mPath = path
        if host is None:
            host = "localhost"
        if port is None:
            port  = 27017
        self.mMongo = MongoClient(host="localhost",  port  = 27017)

    @staticmethod
    def _goodPair(key_value):
        return key_value[0] and key_value[0][0] != '_'

    def getRecData(self, rec_key):
        data = self.mMongo[self.mPath].rec_data.find_one(
            {"_key": rec_key})
        if data is None:
            return dict()
        return dict(filter(self._goodPair, data.items()))

    def setRecData(self, rec_key, pairs):
        data = pairs.copy()
        data["_key"] = rec_key
        update_instr = {"$set":
            {key: value for key, value in pairs.items()}}
        unset_keys = set(self.getRecData(rec_key).keys())
        unset_keys -= set(pairs.keys())
        if len(unset_keys) > 0:
            update_instr["$unset"] = {key: "" for key in unset_keys}
        self.mMongo[self.mPath].rec_data.update(
            {"_key": rec_key}, update_instr, upsert = True)

