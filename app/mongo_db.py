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

    def getRecData(self, rec_key):
        return self.mMongo[self.mPath].rec_data.find_one(
            {"_id": rec_key})

    def setRecData(self, rec_key, pairs, prev_data = False):
        data = pairs.copy()
        data["_id"] = rec_key
        update_instr = dict()
        if len(pairs) > 0:
            update_instr["$set"] = {key: value
                for key, value in pairs.items()}
        if prev_data is False:
            prev_data = self.getRecData(rec_key)
        unset_keys = set(prev_data.keys() if prev_data is not None else [])
        unset_keys -= set(pairs.keys())
        if len(unset_keys) > 0:
            update_instr["$unset"] = {key: "" for key in unset_keys}
        if len(update_instr) > 0:
            self.mMongo[self.mPath].rec_data.update(
                {"_id": rec_key}, update_instr, upsert = True)

    def getFilters(self):
        return [(it["_id"], it["seq"])
            for it in self.mMongo[self.mPath].filters.find()]

    def setFilter(self, filter_name, criteria):
        self.mMongo[self.mPath].filters.update(
            {"_id": filter_name},
            {"$set": {"seq": criteria}}, upsert = True)

    def dropFilter(self, filter_name):
        self.mMongo[self.mPath].filters.remove(
            {"_id": filter_name})
