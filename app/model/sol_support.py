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
def makeSolItemInfo(kind, name, data, rubric,
        upd_time = None, upd_from = None,
        used_names = None, requires = None, is_std = None):
    if used_names is not None:
        assert name not in used_names, "Name duplication " + name
        used_names.add(name)
    ret = {"_tp": kind, "name": name, "data": data}
    for key, val in [("rubric", rubric), ("is_std", is_std), ("req", requires),
            ("time", upd_time), ("from", upd_from)]:
        if val is not None:
            ret[key] = val
    return ret

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
class SolutionKindHandler:
    def __init__(self, broker, sol_kind, sol_maker, special_name = None):
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
        self._setup([], [])

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
        self.mNames = self.mStdNames[:] + dyn_names[:]
        self.mEntryDict = {name: entry_h
            for name, entry_h in zip(self.mStdNames, self.mStdEntries)}
        for name, entry_h in zip(dyn_names, dyn_entries):
            assert self.isDyn(name), "Not a dyn name: " + name
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
                name = info["name"]
                dyn_names.append(name)
                entry_obj = self.mEntryDict.get(name)
                upd_info = [info.get("time"), info.get("from")]
                if (entry_obj is not None
                        and upd_info != entry_obj.getUpdateInfo()):
                    entry_obj = None
                if entry_obj is None:
                    entry_obj = self.mSolMaker(makeSolItemInfo(
                        self.mSolKind, name, info["data"], info.get("rubric"),
                        info.get("time"), info.get("from")))
                    update = True
                dyn_entries.append(entry_obj)
            if (self.mSpecialName is not None
                    and self.mSpecialName not in dyn_names):
                dyn_names.append(self.mSpecialName)
                dyn_entries.append(self.mSolMaker(makeSolItemInfo(
                    self.mSolKind, self.mSpecialName, [], None)))
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
                    "rubric": entry_obj.getRubric(),
                    "eval-status": entry_obj.getEvalStatus()})
        return ret_handle

    def modifySolEntry(self, instr, entry_data):
        option, name = instr[:2]
        assert name and self.isDyn(name), (
            "Improper name for dynamic solution entry: " + name)
        if name != self.mSpecialName:
            AnfisaConfig.assertGoodSolutionName()
        if len(instr) > 2:
            rubric = instr[2]
        else:
            prev_entry = self.pickByName(name)
            rubric = (prev_entry.getRubric()
                if prev_entry is not None else None)

        return self.mBroker.getSolEnv().modifyEntry(
            self.mBroker.getName(), self.mSolKind, option,
            name, entry_data, rubric)

    def normalizeSolEntry(self, sol_obj):
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
class SolutionBaseInfo:
    def __init__(self, kind, name = None, rubric = None,
            updated_time = None, updated_from = None):
        self.mKind = kind
        self.mName = name
        self.mRubric = rubric
        self.mUpdatedInfo = [updated_time, updated_from]

        if self.mRubric is not None:
            assert isinstance(self.mRubric, str), (
                "Rubric is not string: " + str(self.mRubric))

    def getSolKind(self):
        return self.mKind

    def getName(self):
        return self.mName

    def getRubric(self):
        return self.mRubric

    def getUpdateInfo(self):
        return self.mUpdatedInfo

#===============================================
class SolPanelHandler(SolutionBaseInfo):
    def __init__(self, tp, name, sym_list, rubric = None,
            updated_time = None, updated_from = None):
        SolutionBaseInfo.__init__(self, "panel." + tp,
            name, rubric, updated_time, updated_from)
        self.mType = tp
        self.mSymList = sym_list
        self.mHashCode = md5(bytes(json.dumps(sorted(set(self.mSymList)),
            sort_keys = True), encoding = "utf-8")).hexdigest()

    @staticmethod
    def makeSolEntry(info):
        prefix, tp = info["_tp"].split('.')
        assert prefix == "panel"
        return SolPanelHandler(tp,
            StdNameSupport.normNm(info["name"], info.get("is_std")),
            info["data"],
            rubric = info.get("rubric"),
            updated_time = info.get("time"),
            updated_from = info.get("from"))

    def getType(self):
        return self.mType

    def getSymList(self):
        return self.mSymList

    def getHashCode(self):
        return self.mHashCode

    def getEvalStatus(self):
        return None

    def isDynamic(self):
        return not StdNameSupport.isStd(self.mName)
