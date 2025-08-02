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

from forome_tools.sync_obj import SyncronizedObject
from app.config.a_config import AnfisaConfig
from .sol_pack import SolutionPack
from .sol_item import SolItem
from .sol_support import SolutionKindCollection, StdNameSupport
from .family import FamilyInfo
#===============================================
class SolutionBroker(SyncronizedObject):
    def __init__(self, meta_info, ds_kind,
            derived_mode = False, zygosity_support = True):
        SyncronizedObject.__init__(self)
        self.mDataSchema = meta_info.get("data_schema", "CASE")
        self.mSolPack = SolutionPack.select(self.mDataSchema)
        self.mModes = set()
        self.mModes.add(self.mDataSchema)
        self.mDSKind = ds_kind
        assert self.mDSKind in {"ws", "xl"}
        self.mModes.add(self.mDSKind.upper())

        self.mSolRepo = None
        self.mSolKinds = None
        self.mNamedAttrs = dict()

        reference = meta_info["versions"].get("reference")
        if reference is None:
            self.mFastaBase = "hg38"
        else:
            self.mFastaBase = "hg38" if "38" in reference else "hg19"

        if derived_mode:
            self.addModes({"DERIVED"})
        else:
            self.addModes({"PRIMARY"})

        self.mFamilyInfo = FamilyInfo(meta_info)
        self.addModes(self.mFamilyInfo.prepareModes())

        if (1 <= len(self.mFamilyInfo) <= 10 and zygosity_support):
            self.addModes({"ZYG"})
        self.mZygSupport = None

    def getDSKind(self):
        return self.mDSKind

    def getSolRepo(self):
        return self.mSolRepo

    def getDataSchema(self):
        return self.mDataSchema

    def getFamilyInfo(self):
        return self.mFamilyInfo

    def getFastaBase(self):
        return self.mFastaBase

    #===============================================
    def _setupRepo(self, sol_repo, filter_maker, dtree_maker):
        assert self.mSolRepo is None, "solRepo is already set"
        with self:
            self.mSolRepo = sol_repo
            self.mSolKinds = dict()
            cache_size = AnfisaConfig.configOption("solution.pool.size")
            for sol_kind in sol_repo.getSolKinds():
                if sol_kind == "tags":
                    continue
                elif sol_kind == "filter":
                    kind_h = SolutionKindCollection(self, sol_kind,
                        filter_maker, cache_size=cache_size)
                elif sol_kind == "dtree":
                    kind_h = SolutionKindCollection(self, sol_kind,
                        dtree_maker, cache_size=cache_size)
                else:
                    kind_h = PanelSolHandler.buildCollection(
                        self, sol_kind)
                assert kind_h is not None, "Bad sol kind: " + sol_kind
                self.mSolKinds[sol_kind] = kind_h
            self.mSolRepo.attachBroker(self)

    def deactivate(self):
        if self.mSolRepo is not None:
            self.mSolRepo.detachBroker(self)

    #===============================================
    def addModes(self, modes):
        if modes:
            self.mModes |= set(modes)

    def testRequirements(self, modes):
        if not modes:
            return True
        return len(modes & self.mModes) == len(modes)

    def iterStdItems(self, item_kind):
        item_kind = SolItem.normKind(item_kind)
        for it in self.mSolPack:
            if it.getSolKind() == item_kind and self.testRequirements(it.get("req")):
                yield it

    def getStdItemData(self, item_kind, item_name):
        for it in self.iterStdItems(item_kind):
            if it.getName() == item_name:
                return it.getData()
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
    def refreshSolEntries(self, kind):
        with self:
            if kind in self.mSolKinds:
                self.mSolKinds[kind].refreshSolEntries()
            elif kind == "tags" and self.getDSKind() == "ws":
                if self.getTagsMan() is not None:
                    self.getTagsMan().refreshTags()

    def iterSolEntries(self, kind):
        sol_kind_h = self.mSolKinds[kind]
        for info in sol_kind_h.getListInfo():
            yield sol_kind_h.pickByName(info["name"])

    def getSpecialSolEntry(self, kind):
        sol_kind_h = self.mSolKinds[kind]
        return sol_kind_h.pickByName(sol_kind_h.getSpecialName())

    def noSolEntries(self, kind):
        return self.mSolKinds[kind].isEmpty()

    def pickSolEntry(self, kind, name):
        return self.mSolKinds[kind].pickByName(name)

    def remindSolEntry(self, sol_entry):
        return self.mSolKinds[sol_entry.getSolKind()].remindSolEntry(sol_entry)

    def mindSolEntry(self, sol_entry):
        return self.mSolKinds[sol_entry.getSolKind()].mindSolEntry(sol_entry)

    def modifySolEntry(self, kind, instr, entry_data):
        with self:
            return self.mSolKinds[kind].modifySolEntry(instr, entry_data)

    def getSolEntryList(self, kind):
        return self.mSolKinds[kind].getListInfo()

    #===============================================
    def iterPanels(self, panel_type):
        for it in (self.iterSolEntries("panel." + panel_type)):
            yield (it.getName(), it.getSymList())

    def getPanelList(self, panel_name, panel_type, is_optional = False):
        for pname, names in self.iterPanels(panel_type):
            if pname == panel_name:
                return names
        assert is_optional, f"{panel_type}: Panel {panel_name} not found"
        return None

    def iterSpecialPanels(self):
        for sol_kind in self.mSolRepo.getSolKinds():
            kind_h = self.mSolKinds.get(sol_kind)
            if kind_h is None:
                continue
            special_name = kind_h.getSpecialName()
            if special_name is not None:
                yield kind_h.pickByName(special_name)

    def symbolsToPanels(self, panel_type, symbols):
        symbols = set(symbols)
        ret = []
        for pname, names in self.iterPanels(panel_type):
            if len(symbols & set(names)) > 0:
                ret.append(pname)
        return ret

    #===============================================
    def reportSolutions(self):
        ret = dict()
        for kind in ("filter", "dtree", "zone", "tab-schema", "panel.Symbol"):
            ret[kind] = [it.getName() for it in self.iterStdItems(kind)]
        return ret

#===============================================
class PanelSolHandler(SolItem):
    @staticmethod
    def buildCollection(broker, sol_kind):
        if not sol_kind.startswith("panel."):
            return None
        prefix, ptype = sol_kind.split('.')
        panels_cfg = AnfisaConfig.configOption("panels.setup")
        assert ptype in panels_cfg, (
            "Panel type not supported: " + ptype)
        return SolutionKindCollection(broker, sol_kind,
            PanelSolHandler,
            special_name = panels_cfg[ptype].get("special"))

    def __init__(self, info):
        SolItem.__init__(self, info.getDescr())
        assert self.getSolKind().startswith("panel_")
        _, _, self.mType = self.getSolKind().partition('_')

    def getType(self):
        return self.mType

    def getSymList(self):
        return self.getData()

    def getEvalStatus(self):
        return None

    def isDynamic(self):
        return not StdNameSupport.isStd(self.getName())
