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

from threading import Lock

from forome_tools.sync_obj import SyncronizedObject
from .sol_pack import SolutionPack
from .sol_support import SolutionKindHandler
from .family import FamilyInfo
#===============================================
class SolutionBroker(SyncronizedObject):
    def __init__(self, meta_info, ds_kind,
            derived_mode = False, zygosity_support = True):
        SyncronizedObject.__init__(self)
        self.mDataSchema = meta_info.get("data_schema", "CASE")
        self.mSolPack = SolutionPack.select(self.mDataSchema)
        self.mLock  = Lock()
        self.mModes = set()
        self.mModes.add(self.mDataSchema)
        ds_kind = ds_kind.upper()
        assert ds_kind in {"WS", "XL"}
        self.mModes.add(ds_kind)

        self.mStdFilterDict = None
        self.mStdFilterList = None
        self.mFilterCache = None
        self.mSolEnv = None
        self.mSolKinds = None
        self.mNamedAttrs = dict()

        reference = meta_info["versions"].get("reference")
        self.mFastaBase = "hg38" if reference and "38" in reference else "hg19"

        if derived_mode:
            self.addModes({"DERIVED"})
        else:
            self.addModes({"PRIMARY"})

        self.mFamilyInfo = FamilyInfo(meta_info)
        self.addModes(self.mFamilyInfo.prepareModes())

        if (1 <= len(self.mFamilyInfo) <= 10 and zygosity_support):
            self.addModes({"ZYG"})
        self.mZygSupport = None

    def getSolEnv(self):
        return self.mSolEnv

    def getDataSchema(self):
        return self.mDataSchema

    def getFamilyInfo(self):
        return self.mFamilyInfo

    def getFastaBase(self):
        return self.mFastaBase

    #===============================================
    def setSolEnv(self, sol_space):
        assert self.mSolEnv is None, "solEnv is already set"
        with self:
            self.mSolEnv = sol_space
            self.mSolKinds = {kind: SolutionKindHandler(self, kind)
                for kind in ("filter", "dtree")}
            self.mSolKinds["panel.Symbol"] = SolutionKindHandler(
                self, "panel.Symbol", False, "__Symbol__")
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

    def getModes(self):
        return self.mModes

    #===============================================
    def regNamedAttr(self, name, attr_h):
        assert name not in self.mNamedAttrs, "Attribute duplication: " + name
        self.mNamedAttrs[name] = attr_h

    def getNamedAttr(self, name):
        return self.mNamedAttrs[name]

    #===============================================
    def iterPanels(self, panel_type):
        for it in self.iterStdItems("panel." + panel_type):
            yield (it.getName(), it.getData())

    def getPanelList(self, panel_name, panel_type):
        for pname, names in self.iterPanels(panel_type):
            if pname == panel_name:
                return names
        assert False, f"{panel_type}: Panel {panel_name} not found"
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
        for kind in ("filter", "dtree", "zone", "tab-schema", "panel.Symbol"):
            ret[kind] = [it.getName() for it in self.iterStdItems(kind)]
        return ret

