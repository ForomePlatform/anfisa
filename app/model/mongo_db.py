#  Copyright (c) 2019. Partners HealthCare and other members of
#  Forome Association
#
#  Developed by Sergey Trifonov based on contributions by Joel Krier,
#  Michael Bouzinier, Shamil Sunyaev and other members of Division of
#  Genetics, Brigham and Women's Hospital
#
#  Licensed under the Apache License, Version 2.0 (the "License");
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
#
#        http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.
#

import os
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

    def makeAgent(self, name):
        return self.mMongo[self.mPath][name]

#===============================================
class MongoDSAgent:
    def __init__(self, connector, agent, name):
        self.mConnector = connector
        self.mAgent = agent
        self.mName = name

    def getName(self):
        return self.mName

    def getAgentKind(self):
        assert False

    #===== CreationDate
    def getCreationDate(self):
        it = self.mAgent.find_one({"_id": "created"})
        if it is not None:
            return AnfisaConfig.normalizeTime(it.get("time"))
        return None

    def checkCreationDate(self, time_label = None, ajson_fname = None):
        to_update = dict()
        if ajson_fname is not None:
            ajson_stat = os.stat(ajson_fname)
            to_update["fstat"] = [ajson_fname,
                int(ajson_stat.st_size), int(ajson_stat.st_mtime)]
        it = self.mAgent.find_one({"_id": "created"})
        if it is None:
            to_update["time"] = (time_label if time_label is not None
                else datetime.now().isoformat())
        if len(to_update) > 0:
            self.mAgent.update({"_id": "created"}, {"$set": to_update})

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

#===============================================
class MongoWSAgent(MongoDSAgent):
    def __init__(self, connector, agent, name):
        MongoDSAgent.__init__(self, connector, agent, name)

    def getAgentKind(self):
        return "WS"

    #===== TagsData
    def getTagsData(self, rec_key):
        return self.mAgent.find_one({"_id": "rec-" + rec_key})

    def setTagsData(self, rec_key, pairs, prev_data = False):
        data = pairs.copy()
        data["_id"] = "rec-" + rec_key
        update_instr = dict()
        if len(pairs) > 0:
            update_instr["$set"] = {key: value
                for key, value in pairs.items()}
        if prev_data is False:
            prev_data = self.getTagsData(rec_key)
        unset_keys = set(prev_data.keys() if prev_data is not None else [])
        unset_keys -= set(pairs.keys())
        if "_id" in unset_keys:
            unset_keys.remove("_id")
        if len(unset_keys) > 0:
            update_instr["$unset"] = {key: "" for key in unset_keys}
        if len(update_instr) > 0:
            self.mAgent.update(
                {"_id": "rec-" + rec_key}, update_instr, upsert = True)

#===============================================
class MongoXLAgent(MongoDSAgent):
    def __init__(self, connector, agent, name):
        MongoDSAgent.__init__(self, connector, agent, name)

    def getAgentKind(self):
        return "XL"
