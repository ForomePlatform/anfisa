from pymongo import MongoClient

#===============================================
class MongoConnector:
    def __init__(self, path, host = None, port = None):
        self.mPath = path
        if host is None:
            host = "localhost"
        if port is None:
            port  = 27017
        self.mMongo = MongoClient(host,  port)
        self.mAgents = {"_common_": MongoCommonAgent(self,
            self.mMongo[self.mPath]["_common_"])}

    def getCommonAgent(self):
        return self.mAgents["_common_"]

    def getAgent(self, name):
        if name not in self.mAgents:
            self.mAgents[name] = MongoCollectionAgent(self,
                self.mMongo[self.mPath][name], name)
        return self.mAgents[name]

#===============================================
class MongoCollectionAgent:
    def __init__(self, connector, agent, name):
        self.mConnector = connector
        self.mAgent = agent
        self.mName = name

    def getName(self):
        return self.mName

    def getRecData(self, rec_key):
        return self.mAgent.find_one({"_id": "rec-" + rec_key})

    def setRecData(self, rec_key, pairs, prev_data = False):
        data = pairs.copy()
        data["_id"] = "rec-" + rec_key
        update_instr = dict()
        if len(pairs) > 0:
            update_instr["$set"] = {key: value
                for key, value in pairs.items()}
        if prev_data is False:
            prev_data = self.getRecData(rec_key)
        unset_keys = set(prev_data.keys() if prev_data is not None else [])
        unset_keys -= set(pairs.keys())
        if "_id" in unset_keys:
            unset_keys.remove("_id")
        if len(unset_keys) > 0:
            update_instr["$unset"] = {key: "" for key in unset_keys}
        if len(update_instr) > 0:
            self.mAgent.update(
                {"_id": "rec-" + rec_key}, update_instr, upsert = True)

    def getFilters(self):
        ret = []
        for it in self.mAgent.find({"_tp": "flt"}):
            it_id = it["_id"]
            if it_id.startswith("flt-"):
                ret.append((it_id[4:], it["seq"]))
        return ret

    def setFilter(self, filter_name, conditions):
        self.mAgent.update({"_id": "flt-" + filter_name},
            {"$set": {"seq": conditions, "_tp": "flt"}}, upsert = True)

    def dropFilter(self, filter_name):
        self.mAgent.remove({"_id": "flt-" + filter_name})

    def getRulesParamValues(self):
        it = self.mAgent.find_one({"_id": "params"})
        if it is not None:
            return it["params"]
        return None

    def setRulesParamValues(self, param_values):
        self.mAgent.update(
            {"_id": "params"},
            {"$set": {"params": param_values}}, upsert = True)

    def getWSNote(self):
        it = self.mAgent.find_one({"_id": "note"})
        if it is not None:
            return it["note"].strip()
        return ""

    def setWSNote(self, note):
        self.mAgent.update(
            {"_id": "note"},
            {"$set": {"note": note.strip()}}, upsert = True)

#===============================================
class MongoCommonAgent:
    def __init__(self, connector, agent):
        self.mConnector = connector
        self.mAgent = agent

