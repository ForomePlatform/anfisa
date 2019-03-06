from pymongo import MongoClient
from datetime import datetime

from .a_config import AnfisaConfig

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

    def getWSAgent(self, name):
        if name not in self.mAgents:
            self.mAgents[name] = MongoWSAgent(self,
                self.mMongo[self.mPath][name], name)
        return self.mAgents[name]

    def getDSAgent(self, name):
        if name not in self.mAgents:
            self.mAgents[name] = MongoDSAgent(self,
                self.mMongo[self.mPath][name], name)
        return self.mAgents[name]

#===============================================
class MongoWSAgent:
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
                ret.append((it_id[4:], it["seq"],
                    AnfisaConfig.normalizeTime(it.get("time"))))
        return ret

    def setFilter(self, filter_name, conditions):
        time_label = datetime.now().isoformat()
        self.mAgent.update({"_id": "flt-" + filter_name},
            {"$set": {"seq": conditions,
                "_tp": "flt", "time": time_label}}, upsert = True)
        return time_label

    def dropFilter(self, filter_name):
        self.mAgent.remove({"_id": "flt-" + filter_name})

    def getRulesParamValues(self):
        it = self.mAgent.find_one({"_id": "params"})
        if it is not None:
            return it["params"]
        return None

    def setRulesParamValues(self, param_values):
        self.mAgent.update({"_id": "params"},
            {"$set": {"params": param_values}}, upsert = True)

    def getWSNote(self):
        it = self.mAgent.find_one({"_id": "note"})
        if it is not None:
            return (it["note"].strip(),
                AnfisaConfig.normalizeTime(it.get("time")))
        return ("", None)

    def setWSNote(self, note):
        time_label = datetime.now().isoformat()
        self.mAgent.update({"_id": "note"},
            {"$set": {"note": note.strip(), "time": time_label}},
                upsert = True)

#===============================================
class MongoCommonAgent:
    def __init__(self, connector, agent):
        self.mConnector = connector
        self.mAgent = agent

#===============================================
class MongoDSAgent:
    def __init__(self, connector, agent, name):
        self.mConnector = connector
        self.mAgent = agent
        self.mName = name

    def getName(self):
        return self.mName

    def getFilters(self):
        ret = []
        for it in self.mAgent.find({"_tp": "flt"}):
            it_id = it["_id"]
            if it_id.startswith("flt-"):
                ret.append((it_id[4:], it["seq"],
                    AnfisaConfig.normalizeTime(it.get("time"))))
        return ret

    def setFilter(self, filter_name, conditions):
        time_label = datetime.now().isoformat()
        self.mAgent.update({"_id": "flt-" + filter_name},
            {"$set": {"seq": conditions, "_tp": "flt", "time": time_label}},
            upsert = True)
        return time_label

    def dropFilter(self, filter_name):
        self.mAgent.remove({"_id": "flt-" + filter_name})

    def getDSNote(self):
        it = self.mAgent.find_one({"_id": "note"})
        if it is not None:
            return (it["note"].strip(),
                AnfisaConfig.normalizeTime(it.get("time")))
        return ("", None)

    def setDSNote(self, note):
        time_label = datetime.now().isoformat()
        self.mAgent.update({"_id": "note"},
            {"$set": {"note": note.strip(), "time": time_label}},
            upsert = True)

    def getVersionList(self):
        ret = []
        for it in self.mAgent.find({"_tp": "version"}):
            it_id = it["_id"]
            if it_id.startswith("ver-"):
                ret.append((int(it_id[4:]), it["date"], it["hash"]))
        return sorted(ret)

    def getVersionTree(self, version):
        for it in self.mAgent.find({"_id": "ver-" + str(version)}):
            return it["tree"]
        return None

    def addVersion(self, version, tree, hash, date = None):
        if date is None:
            date = datetime.now().isoformat()
        self.mAgent.update({"_id": "ver-" + str(version)},
            {"$set": {"hash": hash, "tree": tree,
                "date": date, "_tp": "version"}}, upsert = True)

    def dropVersion(self, version):
        self.mAgent.remove({"_id": "ver-" + str(version)})

