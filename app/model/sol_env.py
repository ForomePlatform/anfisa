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

from datetime import datetime

from app.config.a_config import AnfisaConfig

#===============================================
class SolutionEnv:
    sSolKeys = ["filter", "dtree", "panel.symbol", "tags"]

    def __init__(self, mongo_connector, name):
        self.mName = name
        self.mMongoAgent = mongo_connector.getPlainAgent(name)
        self.mBrokers = []
        self.mHandlers = {sol_kind: _SolKindMongoHandler(
            sol_kind, self.mMongoAgent)
            for sol_kind in self.sSolKeys}

    def getName(self):
        return self.mName

    def getAgentKind(self):
        return "SolutionEnv"

    def attachBroker(self, broker_h):
        assert broker_h not in self.mBrokers
        self.mBrokers.append(broker_h)
        for sol_kind in self.mHandlers.keys():
            broker_h.refreshSolEntries(sol_kind)
        broker_h.refreshSolEntries("tags")

    def detachBroker(self, broker_h):
        assert broker_h in self.mBrokers
        self.mBrokers.remove(broker_h)

    def getIntVersion(self, sol_kind):
        return self.mHandlers[sol_kind].getIntVersion()

    def iterEntries(self, key):
        return self.mHandlers[key].iterEntries()

    def getEntry(self, key, name):
        return self.mHandlers[key].getEntry(name)

    def modifyEntry(self, ds_name, sol_kind, option, name, value):
        if self.mHandlers[sol_kind].modifyData(option, name, value, ds_name):
            for broker_h in self.mBrokers:
                broker_h.refreshSolEntries(sol_kind)
            return True
        return False

    def getTagsData(self, rec_key):
        return self.mHandlers["tags"].getData(rec_key)

    def setTagsData(self, rec_key, tags_data):
        pass

    def dumpAll(self):
        ret = []
        for rec_obj in self.mMongoAgent.find():
            if rec_obj["_tp"] in self.sSolKeys:
                rec = dict()
                for key, val in rec_obj.items():
                    if key != "_id":
                        rec[key] = val
                ret.append(rec)
        return ret

#===============================================
class _SolKindMongoHandler:
    sDefaultNone = (None, None, None)

    def __init__(self, sol_kind, mongo_agent):
        self.mSolKind = sol_kind
        self.mMongoAgent = mongo_agent
        self.mData = dict()
        self.mIntVersion = 0
        for it in self.mMongoAgent.find({"_tp": self.mSolKind}):
            name = it["name"]
            self.mData[name] = [it[self.mSolKind],
                AnfisaConfig.normalizeTime(it.get("time")), it["from"]]

    def getSolKind(self):
        return self.mSolKind

    def getIntVersion(self):
        return self.mIntVersion

    def iterEntries(self):
        ret = []
        for name in sorted(self.mData.keys()):
            value, upd_time, upd_from = self.mData[name]
            ret.append((name, value, upd_time, upd_from))
        return iter(ret)

    def getEntry(self, name):
        return self.mData.get(name, self.sDefaultNone)

    def modifyData(self, option, name, value, upd_from):
        if option == "UPDATE":
            time_label = datetime.now().isoformat()
            self.mMongoAgent.update_one({"_tp": self.mSolKind, "name": name},
                {"$set": {self.mSolKind: value, "_tp": self.mSolKind,
                    "time": time_label, "from": upd_from}},
                upsert = True)
            self.mData[name] = [value,
                AnfisaConfig.normalizeTime(time_label), upd_from]
            self.mIntVersion += 1
            return True
        if option == "DELETE" and name in self.mData:
            self.mMongoAgent.delete_many({"_tp": self.mSolKind, "name": name})
            del self.mData[name]
            self.mIntVersion += 1
            return True
        return False
