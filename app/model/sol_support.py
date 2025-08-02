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
from cachetools import LRUCache

from .sol_item import SolItem
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

    @classmethod
    def normNm(cls, name, is_std):
        if is_std:
            return cls.stdNm(name)
        return cls.offNm(name)

#===============================================
class SolutionKindCollection:
    def __init__(self, broker, sol_kind, sol_maker,
            cache_size=0, special_name=None):
        self.mBroker = broker
        self.mSolKind = sol_kind
        self.mSolMaker = sol_maker
        self.mSpecialName = special_name
        self.mNames = None
        self.mEntryDict = None
        self.mHashDict = None
        self.mStdEntries = [self.mSolMaker(info)
            for info in self.mBroker.iterStdItems(self.mSolKind)]
        self.mStdNames = [entry_h.getName()
            for entry_h in self.mStdEntries]
        if cache_size > 0:
            self.mCache = LRUCache(cache_size)
        else:
            self.mCache = None
        self._setup([])

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

    def _setup(self, dyn_entries):
        self.mEntryDict = {name: entry_h
            for name, entry_h in zip(self.mStdNames, self.mStdEntries)}
        self.mNames = self.mStdNames[:]
        for entry_h in dyn_entries:
            name = entry_h.getName()
            assert self.isDyn(name), "Not a dyn name: " + name
            self.mNames.append(name)
            if name not in self.mEntryDict:
                self.mEntryDict[name] = entry_h
            else:
                logging.warning(
                    f"Kind {self.mKind} collection name duplication: {name}")
        self.mHashDict = {}
        for name in self.mNames:
            entry_h = self.mEntryDict[name]
            hash_code = entry_h.getHashCode()
            if hash_code not in self.mHashDict:
                self.mHashDict[hash_code] = entry_h
            else:
                nm1 = self.mHashDict[hash_code].getName()
                logging.warning(
                    f"Kind {self.mKind} collection hashcode conflict:" +
                    f"for {nm1} and ignored {name}")

    def isEmpty(self):
        return len(self.mNames) == 0

    def refreshSolEntries(self):
        update = False
        with self.mBroker:
            dyn_entries = []
            for item in self.mBroker.getSolRepo().iterEntries(self.mSolKind):
                cur_entry = self.mEntryDict.get(item.getName())
                if (cur_entry is not None and
                        cur_entry.getUpdateInfo() != item.getUpdateInfo()):
                    cur_entry = None
                if cur_entry is None:
                    cur_entry = self.mSolMaker(item)
                    cur_entry.activate()
                    update = True
                dyn_entries.append(cur_entry)
            if (self.mSpecialName and not any(
                    entry_h.getName() == self.mSpecialName
                    for entry_h in dyn_entries)):
                dyn_entries.append(self.mSolMaker(SolItem.create(
                    self.mSolKind, self.mSpecialName, [], None)))
            if (update or len(dyn_entries) + len(self.mStdNames) !=
                    len(self.mNames)):
                self._setup(dyn_entries)
                return True
        return False

    def getListInfo(self):
        ret_handle = []
        with self.mBroker:
            for idx, name in enumerate(self.mNames):
                if self.mSpecialName and name == self.mSpecialName:
                    continue
                entry_h = self.mEntryDict[name]
                ret_handle.append({
                    "name": name,
                    "standard": idx < len(self.mStdNames),
                    "upd-time": entry_h.get("upd-time"),
                    "upd-from": entry_h.get("upd_from"),
                    "rubric": entry_h.get("rubric")})
        return ret_handle

    def modifySolEntry(self, instr, entry_data):
        option, name = instr[:2]
        assert name and self.isDyn(name), (
            "Improper name for dynamic solution entry: " + name)
        if name != self.mSpecialName:
            AnfisaConfig.assertGoodSolutionName(name)
        prev_entry = self.pickByName(name)
        if prev_entry and prev_entry.getHashCode() in self.mCache:
            del self.mCache[prev_entry.getHashCode()]
        if len(instr) > 2:
            rubric = instr[2]
        else:
            rubric = (prev_entry.getRubric()
                if prev_entry is not None else None)

        return self.mBroker.getSolRepo().modifyEntry(
            self.mBroker.getName(), self.mSolKind, option,
            name, entry_data, rubric)

    def remindSolEntry(self, entry_h):
        with self.mBroker:
            hash_code = entry_h.getHashCode()
            if hash_code in self.mHashDict:
                return self.mHashDict[hash_code]
            if self.mCache is not None and hash_code in self.mCache:
                return self.mCache[hash_code]
        return None

    def mindSolEntry(self, entry_h):
        if self.mCache is None:
            return
        with self.mBroker:
                self.mCache[entry_h.getHashCode()] = entry_h

    def pickByHash(self, hash_code):
        with self.mBroker:
            return self.mHashDict.get(hash_code)

    def pickByName(self, name):
        with self.mBroker:
            return self.mEntryDict.get(name)
