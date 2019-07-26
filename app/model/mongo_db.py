from pymongo import MongoClient
from datetime import datetime

from app.config.a_config import AnfisaConfig

#===============================================
class MongoConnector:
    def __init__(self, path, host = None, port = None):
        self.mPath = path
        if host is None:
            host = "localhost"
        if port is None:
            port  = 27017
        self.mMongo = MongoClient(host,  port)
        self.mAgents = {}

    def close(self):
        self.mMongo.close()

    def getWSAgent(self, name):
        if name not in self.mAgents:
            self.mAgents[name] = MongoWSAgent(self,
                self.mMongo[self.mPath][name], name)
        return self.mAgents[name]

    def getXLAgent(self, name):
        if name not in self.mAgents:
            self.mAgents[name] = MongoXLAgent(self,
                self.mMongo[self.mPath][name], name)
        return self.mAgents[name]

    def getDSAgent(self, name, kind):
        if kind.lower() == "ws":
            return self.getWSAgent(name)
        if kind.lower() == "xl":
            return self.getXLAgent(name)
        assert False

#===============================================
class MongoDSAgent:
    def __init__(self, connector, agent, name):
        self.mConnector = connector
        self.mAgent = agent
        self.mName = name

    def getName(self):
        return self.mName

    def getAgent(self):
        return self.mAgent

    def getKind(self):
        assert False

    #===== CreationDate
    def getCreationDate(self):
        it = self.mAgent.find_one({"_id": "created"})
        if it is not None:
            return AnfisaConfig.normalizeTime(it.get("time"))
        return None

    def checkCreationDate(self, time_label = None):
        it = self.mAgent.find_one({"_id": "created"})
        if it is None:
            if time_label is None:
                time_label = datetime.now().isoformat()
            self.mAgent.update({"_id": "created"},
                {"$set": {"time": time_label}},
                    upsert = True)

    #===== Note
    def getNote(self):
        it = self.mAgent.find_one({"_id": "note"})
        if it is not None:
            return (it["note"].strip(),
                AnfisaConfig.normalizeTime(it.get("time")))
        return ("", None)

    def setNote(self, note):
        time_label = datetime.now().isoformat()
        self.mAgent.update({"_id": "note"},
            {"$set": {"note": note.strip(), "time": time_label}},
                upsert = True)

    #===== Filters
    def getFilters(self):
        ret = []
        for it in self.mAgent.find({"_tp": "flt"}):
            it_id = it["_id"]
            if it_id.startswith("flt-"):
                ret.append((it_id[4:], it["seq"],
                    AnfisaConfig.normalizeTime(it.get("time"))))
        return ret

    def setFilter(self, filter_name, cond_seq):
        time_label = datetime.now().isoformat()
        self.mAgent.update({"_id": "flt-" + filter_name},
            {"$set": {"seq": cond_seq, "_tp": "flt", "time": time_label}},
            upsert = True)
        return time_label

    def dropFilter(self, filter_name):
        self.mAgent.remove({"_id": "flt-" + filter_name})

#===============================================
class MongoWSAgent(MongoDSAgent):
    def __init__(self, connector, agent, name):
        MongoDSAgent.__init__(self, connector, agent, name)

    def getKind(self):
        return "WS"

    #===== RecData
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

    #===== RulesParamValues
    def getRulesParamValues(self):
        it = self.mAgent.find_one({"_id": "params"})
        if it is not None:
            return it["params"]
        return None

    def setRulesParamValues(self, param_values):
        self.mAgent.update({"_id": "params"},
            {"$set": {"params": param_values}}, upsert = True)

#===============================================
class MongoXLAgent(MongoDSAgent):
    def __init__(self, connector, agent, name):
        MongoDSAgent.__init__(self, connector, agent, name)

    def getKind(self):
        return "XL"

    #===== TreeCodeVersions
    def getTreeCodeVersions(self):
        ret = []
        for it in self.mAgent.find({"_tp": "tree"}):
            it_id = it["_id"]
            if it_id.startswith("tree-ver-"):
                ret.append((int(it_id[9:]), it["date"], it["hash"]))
        return sorted(ret)

    def getTreeCodeVersion(self, version):
        for it in self.mAgent.find(
            {"_tp": "tree", "_id": "tree-ver-" + str(version)}):
                return it["code"]
        return None

    def addTreeCodeVersion(self, version, code, hash, date = None):
        if date is None:
            date = datetime.now().isoformat()
        self.mAgent.update(
            {"_tp": "tree", "_id": "tree-ver-" + str(version)},
            {"$set": {"hash": hash, "code": code,
                "date": date, "_tp": "tree"}}, upsert = True)

    def dropTreeCodeVersion(self, version):
        self.mAgent.remove(
            {"_tp": "tree", "_id": "tree-ver-" + str(version)})

