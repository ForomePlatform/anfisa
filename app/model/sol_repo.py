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

import logging
from datetime import datetime

from .sol_item import SolItem

#===============================================
class SolutionRepo:
    sSolKinds = ["filter", "dtree", "panel.Symbol", "tags"]

    @classmethod
    def getSolKinds(cls):
        return cls.sSolKinds

    def __init__(self, mongo_connector, name):
        self.mName = name
        self.mMongoAgent = mongo_connector.getPlainAgent(name)
        self.mBrokers = []
        self.mHandlers = {sol_kind: _RepoKindHandler(self, sol_kind)
            for sol_kind in self.sSolKinds}

    def getName(self):
        return self.mName

    def getAgentKind(self):
        return "SolutionRepo"

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
        for sol_kind in self.sSolKinds:
            ret += self.mHandlers[sol_kind].dumpItems()
        return ret

#===============================================
class _RepoKindHandler:
    def __init__(self, master, sol_kind):
        self.mSolKind = sol_kind.replace('.', '_')
        self.mMaster = master
        self.mEntries = {}
        self.mHashCodes = {}
        self.mIntVersion = 0
        for descr in self._findItems():
            assert "data" in descr, "Mongo support is out of date"
            assert descr["_tp"] == self.mSolKind
            if descr["name"] in self.mEntries:
                nm = descr["name"]
                logging.error(
                    f"Kind {self.mSolKind}: name duplication {nm} ignored")
                continue
            item = SolItem(descr)
            if item.getHashCode() in self.mHashCodes:
                nm1 = descr["name"]
                nm2 = self.mHashCodes[item.getHashCode()]["name"]
                logging.error(
                    f"Kind {self.mSolKind}: hashcode duplication with {nm1}" +
                    f" {nm2} ignored")
                continue
            self.mEntries[descr["name"]] = item
            self.mHashCodes[item.getHashCode()] = item

    def _findItems(self):
        return self.mMaster.getMongoAgent().find({"_tp": self.mSolKind})

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
            pre_item = self.mEntries.get("name")
            item = SolItem.create(self.mSolKind,
                name, value, rubric,
                upd_time = datetime.now().isoformat(),
                upd_from = upd_from)
            self.mMaster.getMongoAgent().update_one(
                {"_tp": self.mSolKind, "name": name},
                {"$set": item.getDescr()}, upsert = True)
            self.mEntries[name] = item
            if pre_item is not None:
                del self.mHashCodes[pre_item.getHashCode()]
            self.mHashCodes[item.getHashCode()] = item
            self.mIntVersion += 1
            return True
        if option == "DELETE" and name in self.mEntries:
            self.mMaster.getMongoAgent().delete_many(
                {"_tp": self.mSolKind, "name": name})
            pre_item = self.mEntries.get("name")
            del self.mEntries[name]
            if pre_item is not None:
                del self.mHashCodes[pre_item.getHashCode()]
            self.mIntVersion += 1
            return True
        return False

    def _dumpItems(self):
        ret = []
        for descr in self.mMongoAgent.find():
            assert descr["_tp"] == self.mSolKind
            rec = dict()
            for key, val in descr.items():
                if key != "_id":
                    rec[key] = val
            ret.append(rec)
        return ret

