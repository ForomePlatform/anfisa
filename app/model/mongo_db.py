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
        self.mDSAgents = dict()
        self.mPlainAgents = dict()

    def close(self):
        self.mMongo.close()

    def getDSAgent(self, name, kind):
        if name not in self.mDSAgents:
            self.mDSAgents[name] = MongoDSAgent(self,
                self.mMongo[self.mPath][name], name)
        return self.mDSAgents[name]

    def getPlainAgent(self, name):
        if name not in self.mPlainAgents:
            self.mPlainAgents[name] = self.mMongo[self.mPath][name]
        return self.mPlainAgents[name]

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
