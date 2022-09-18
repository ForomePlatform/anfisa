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

from .sol_support import makeSolItemInfo

#===============================================
class SolutionEnv:
    sSolKeys = ["filter", "dtree", "panel.Symbol", "tags"]

    @classmethod
    def getSolKeys(cls):
        return cls.sSolKeys

    def __init__(self, mongo_connector, name):
        self.mName = name
        self.mMongoAgent = mongo_connector.getPlainAgent(name)
        self.mBrokers = []
        self.mHandlers = {sol_kind: _SolKindMongoHandler(sol_kind, self)
            for sol_kind in self.sSolKeys}

    def getName(self):
        return self.mName

    def getAgentKind(self):
        return "SolutionEnv"

    def getMongoAgent(self):
        return self.mMongoAgent

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

    def modifyEntry(self, ds_name, sol_kind, option, name, value,
            rubric = None):
        if self.mHandlers[sol_kind].modifyEntry(
                option, name, value, rubric, ds_name):
            for broker_h in self.mBrokers:
                broker_h.refreshSolEntries(sol_kind)
            return True
        return False

    def checkEntryKind(self, name):
        for sol_kind, sol_h in self.mHandlers.items():
            if sol_h.getEntry(name) is not None:
                return sol_kind
        return None

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
    def __init__(self, sol_kind, master):
        self.mSolKind = sol_kind.replace('.', '_')
        self.mMaster = master
        self.mEntries = dict()
        self.mIntVersion = 0
        for it in self.mMaster.getMongoAgent().find({"_tp": self.mSolKind}):
            assert "data" in it, "Mongo support is out of date"
            assert it["name"] not in self.mEntries, (
                "Key duplication: " + self.mSolKind + "/" + it["name"])
            self.mEntries[it["name"]] = makeSolItemInfo(
                self.mSolKind, it["name"], it["data"], it.get("rubric"),
                it["time"], it["from"])

    def getSolKind(self):
        return self.mSolKind

    def getIntVersion(self):
        return self.mIntVersion

    def iterEntries(self):
        for name in sorted(self.mEntries.keys()):
            yield self.mEntries[name]

    def getEntry(self, name):
        return self.mEntries.get(name)

    def modifyEntry(self, option, name, value, rubric, upd_from):
        if option == "UPDATE":
            checked_kind = self.mMaster.checkEntryKind(name)
            assert checked_kind in (self.mSolKind, None), (
                "Solution kind duplication conflict: "
                + f"{checked_kind}/{self.mSolKind}")
            info = makeSolItemInfo(self.mSolKind,
                name, value, rubric,
                upd_time = datetime.now().isoformat(),
                upd_from = upd_from)
            self.mMaster.getMongoAgent().update_one(
                {"_tp": self.mSolKind, "name": name},
                {"$set": info}, upsert = True)
            self.mEntries[name] = info
            self.mIntVersion += 1
            return True
        if option == "DELETE" and name in self.mEntries:
            self.mMaster.getMongoAgent().delete_many(
                {"_tp": self.mSolKind, "name": name})
            del self.mEntries[name]
            self.mIntVersion += 1
            return True
        return False
