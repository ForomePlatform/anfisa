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
from threading import Lock
from collections import defaultdict

from forome_tools.sync_obj import SyncronizedObject
from app.config.a_config import AnfisaConfig
from .sol_pack import SolutionPack
#===============================================
class SolutionBroker(SyncronizedObject):
    def __init__(self, data_schema, modes):
        SyncronizedObject.__init__(self)
        self.mDataSchema = data_schema
        self.mSolPack = SolutionPack.select(data_schema)
        self.mLock  = Lock()
        self.mModes = set()
        self.mModes.add(self.mDataSchema)
        self.addModes(modes)
        self.mStdFilterDict = None
        self.mStdFilterList = None
        self.mFilterCache = None
        self.mSolEnv = None
        self.mSolKinds = None
        self.mNamedAttrs = dict()

    def getSolEnv(self):
        return self.mSolEnv

    def getDataSchema(self):
        return self.mDataSchema

    #===============================================
    def setSolEnv(self, sol_space):
        assert self.mSolEnv is None, "solEnv is already set"
        with self:
            self.mSolEnv = sol_space
            self.mSolKinds = {kind: _SolutionKindHandler(self, kind)
                for kind in ("filter", "dtree")}
            self.mSolEnv.attachBroker(self)

    def deactivate(self):
        if self.mSolEnv is not None:
            self.mSolEnv.detachBroker(self)

    #===============================================
    def addModes(self, modes):
        if modes:
            self.mModes |= set(modes)

    def testRequirements(self, modes):
        if not modes:
            return True
        return len(modes & self.mModes) == len(modes)

    def iterStdItems(self, item_kind):
        return self.mSolPack.iterItems(item_kind, self.testRequirements)

    def getStdItem(self, item_kind, item_name):
        for it in self.mSolPack.iterItems(item_kind, self.testRequirements):
            if it.getName() == item_name:
                return it
        return None

    #===============================================
    def regNamedAttr(self, name, attr_h):
        assert name not in self.mNamedAttrs, "Attribute duplication: " + name
        self.mNamedAttrs[name] = attr_h

    def getNamedAttr(self, name):
        return self.mNamedAttrs[name]

    #===============================================
    def getPanelNames(self, panel_type):
        ret = []
        for it in self.iterStdItems("panel"):
            if it.getData()[0] == panel_type:
                ret.append(it.getName())
        return ret

    def getPanelVariants(self, panel_name,
            panel_type = None, assert_mode = True):
        for it in self.iterStdItems("panel"):
            if it.getName() == panel_name:
                if panel_type is None or it.getData()[0] == panel_type:
                    return it.getData()[1]
        if not panel_type:
            panel_type = "?"
        if assert_mode:
            assert False, f"{panel_type}: Panel {panel_name} not found"
        else:
            logging.warning(f"{panel_type}: Panel {panel_name} not found")
        return None

    #===============================================
    def refreshSolEntries(self, kind):
        with self:
            if kind in self.mSolKinds:
                self.mSolKinds[kind].refreshSolEntries()
            elif kind == "tags" and self.getDSKind() == "ws":
                self.getTagsMan().refreshTags()

    def iterSolEntries(self, kind):
        sol_kind_h = self.mSolKinds[kind]
        for info in sol_kind_h.getList():
            yield sol_kind_h.pickByName(info["name"])

    def noSolEntries(self, kind):
        return self.mSolKinds[kind].isEmpty()

    def pickSolEntry(self, kind, name):
        return self.mSolKinds[kind].pickByName(name)

    def updateSolEntry(self, kind, sol_entry):
        return self.mSolKinds[kind].updateSolEntry(sol_entry)

    def modifySolEntry(self, kind, instr, entry_data):
        with self:
            return self.mSolKinds[kind].modifySolEntry(instr, entry_data)

    def getSolEntryList(self, kind):
        return self.mSolKinds[kind].getList()

    #===============================================
    def reportSolutions(self):
        ret = dict()
        for kind in ("filter", "dtree", "zone", "tab-schema"):
            ret[kind] = [it.getName() for it in self.iterStdItems(kind)]
        p_units = defaultdict(list)
        for it in self.iterStdItems("panel"):
            panel_type = it.getData()[0]
            p_units[panel_type].append(it.getName())
        for panel_type in p_units.keys():
            ret["panel/" + panel_type] = p_units[panel_type]
        return ret

#===============================================
class _SolutionKindHandler:
    sStdFMark = AnfisaConfig.configOption("filter.std.mark")

    def __init__(self, broker, sol_kind):
        self.mBroker = broker
        self.mSolKind = sol_kind
        self.mNames = None
        self.mEntryDict = None
        self.mHashDict = None
        self.mStdNames = []
        self.mStdEntries = []
        for it in self.mBroker.iterStdItems(self.mSolKind):
            std_name = self.sStdFMark + it.getName()
            self.mStdEntries.append(self.mBroker.makeSolEntry(
                self.mSolKind, it.getData(), std_name))
            self.mStdNames.append(std_name)
        self._setup([], [])

    def _setup(self, dyn_names, dyn_entries):
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
            if update:
                self._setup(dyn_names, dyn_entries)
        return update

    def getList(self):
        ret_handle = []
        with self.mBroker:
            for idx, name in enumerate(self.mNames):
                entry_obj = self.mEntryDict[name]
                upd_time, upd_from = entry_obj.getUpdateInfo()
                ret_handle.append({
                    "name": name,
                    "standard": idx < len(self.mStdNames),
                    "upd-time": upd_time,
                    "upd-from": upd_from,
                    "eval-status": entry_obj.getEvalStatus(),
                    "sol-version": self.mBroker.getSolEnv().getIntVersion(
                        self.mSolKind)
                })
        return ret_handle

    def modifySolEntry(self, instr, entry_data):
        option, name = instr
        assert (name and not name.startswith(self.sStdFMark)
            and name[0].isalpha() and ' ' not in name), (
            "Improper name for solution entry: " + name)
        return self.mBroker.getSolEnv().modifyEntry(
            self.mBroker.getName(), self.mSolKind, option, name, entry_data)

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
