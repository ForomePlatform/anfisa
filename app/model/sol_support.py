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

import json
from hashlib import md5

from app.config.a_config import AnfisaConfig
#===============================================
class StdNameSupport:
    sStdMark = AnfisaConfig.configOption("solution.std.mark")

    @classmethod
    def stdNm(cls, name):
        if name.startswith(cls.sStdMark):
            return name
        return cls.sStdMark + name

    @classmethod
    def isStd(cls, name):
        return name.startswith(cls.sStdMark)

    @classmethod
    def offNm(cls, name):
        if name.startswith(cls.sStdMark):
            return name[1:]
        return name

#===============================================
class SolutionKindHandler:
    sMaxSolNameLen = AnfisaConfig.configOption("sol.name.max.length")

    def __init__(self, broker, sol_kind, special_name = None):
        self.mBroker = broker
        self.mSolKind = sol_kind
        self.mSpecialName = special_name
        self.mNames = None
        self.mEntryDict = None
        self.mHashDict = None
        self.mStdNames = []
        self.mStdEntries = []
        for it in self.mBroker.iterStdItems(self.mSolKind):
            std_name = self.stdName(it.getName())
            self.mStdEntries.append(self.mBroker.makeSolEntry(
                self.mSolKind, it.getData(), std_name))
            self.mStdNames.append(std_name)
        self._setup([], [])

    def stdName(self, name):
        return StdNameSupport.stdNm(name)

    def dynName(self, name):
        if self.mSpecialName and name == self.mSpecialName:
            return self.mSpecialName
        return StdNameSupport.offNm(name)

    def offName(self, name):
        if self.mSpecialName and name == self.mSpecialName:
            return self.mSpecialName
        return StdNameSupport.offNm(name)

    def isDyn(self, name):
        if self.mSpecialName and name == self.mSpecialName:
            return True
        return not StdNameSupport.isStd(name)

    def getSpecialName(self):
        return self.mSpecialName

    def _setup(self, dyn_names, dyn_entries):
        dyn_names = [self.dynName(nm) for nm in dyn_names]
        self.mNames = self.mStdNames[:] + dyn_names[:]
        self.mEntryDict = {name: entry_h
            for name, entry_h in zip(self.mStdNames, self.mStdEntries)}
        for name, entry_h in zip(dyn_names, dyn_entries):
            self.mEntryDict[name] = entry_h
        self.mHashDict = {entry_obj.getHashCode(): entry_obj
            for entry_obj in self.mEntryDict.values()}

    def isEmpty(self):
        return len(self.mNames) == 0

    def refreshSolEntries(self):
        update = False
        with self.mBroker:
            dyn_names = []
            dyn_entries = []
            for info in self.mBroker.getSolEnv().iterEntries(self.mSolKind):
                name, entry_data, upd_time, upd_from = info
                name = self.dynName(name)
                dyn_names.append(name)
                entry_obj = self.mEntryDict.get(name)
                if (entry_obj is not None
                        and [upd_time, upd_from] != entry_obj.getUpdateInfo()):
                    entry_obj = None
                if entry_obj is None:
                    entry_obj = self.mBroker.makeSolEntry(self.mSolKind,
                        entry_data, name, upd_time, upd_from)
                    update = True
                dyn_entries.append(entry_obj)
            if (self.mSpecialName is not None
                    and self.mSpecialName not in dyn_names):
                dyn_names.append(self.mSpecialName)
                dyn_entries.append(self.mBroker.makeSolEntry(self.mSolKind,
                    [], self.mSpecialName, None, None))
            update |= len(dyn_names) + len(self.mStdNames) != len(self.mNames)
            if update:
                self._setup(dyn_names, dyn_entries)
        return update

    def getListInfo(self):
        ret_handle = []
        with self.mBroker:
            for idx, name in enumerate(self.mNames):
                if self.mSpecialName and name == self.mSpecialName:
                    continue
                entry_obj = self.mEntryDict[name]
                upd_time, upd_from = entry_obj.getUpdateInfo()
                ret_handle.append({
                    "name": name,
                    "standard": idx < len(self.mStdNames),
                    "upd-time": upd_time,
                    "upd-from": upd_from,
                    "eval-status": entry_obj.getEvalStatus()})
        return ret_handle

    def modifySolEntry(self, instr, entry_data):
        option, name = instr
        assert name and self.isDyn(name), (
            "Improper name for dynamic solution entry: " + name)
        name = self.offName(name)
        assert ((name[0].isalpha() and ' ' not in name)
            or name == self.mSpecialName), (
            "Improper name for solution entry: " + name)
        assert len(name) < self.sMaxSolNameLen, (
            "Too long name for solution entry: " + name)
        return self.mBroker.getSolEnv().modifyEntry(
            self.mBroker.getName(), self.mSolKind, option,
            self.offName(name), entry_data)

    def updateSolEntry(self, sol_obj):
        with self.mBroker:
            upd_sol_entry = self.mHashDict.get(sol_obj.getHashCode())
            if upd_sol_entry is not None:
                return upd_sol_entry
            return sol_obj

    def pickByHash(self, hash_code):
        with self.mBroker:
            return self.mHashDict.get(hash_code)

    def pickByName(self, name):
        with self.mBroker:
            return self.mEntryDict.get(name)

#===============================================
class SolPanelHandler:
    def __init__(self, tp, name, sym_list,
            updated_time = None, updated_from = None):
        self.mType = tp
        self.mName = name
        self.mSymList = sym_list
        self.mUpdatedInfo = [updated_time, updated_from]
        self.mHashCode = md5(bytes(json.dumps(sorted(set(self.mSymList)),
            sort_keys = True), encoding = "utf-8")).hexdigest()

    def getType(self):
        return self.mType

    def getName(self):
        return self.mName

    def getSymList(self):
        return self.mSymList

    def getUpdateInfo(self):
        return self.mUpdatedInfo

    def getHashCode(self):
        return self.mHashCode

    def getEvalStatus(self):
        return None

    def isDynamic(self):
        return not StdNameSupport.isStd(self.mName)
