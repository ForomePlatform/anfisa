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

import sys

from forome_tools.inventory import loadDatasetInventory
#===============================================
class DirDSEntry:
    def __init__(self,  ds_name,  ds_kind,  source,  ds_inventory = None,
            entry_data = None):
        self.mName = ds_name
        self.mKind = ds_kind
        self.mSource = source
        self.mInv  = ds_inventory
        self.mEntryData = entry_data

    def getName(self):
        return self.mName

    def getDSKind(self):
        return self.mKind

    def getSource(self):
        return self.mSource

    def getInv(self):
        return self.mInv

    def dump(self):
        return {
            "name": self.mName,
            "kind": self.mKind,
            "source": self.mSource,
            "inv": self.mInv,
            "data": self.mEntryData}

    @classmethod
    def createByDirConfig(cls, ds_name, dir_config, dir_fname):
        if ds_name not in dir_config["datasets"]:
            print("Dataset %s not registered in directory file (%s)" %
                (ds_name, dir_fname), file = sys.stderr)
            sys.exit()
        ds_entry_data = dir_config["datasets"][ds_name]
        if "inv" in ds_entry_data:
            ds_inventory = loadDatasetInventory(ds_entry_data["inv"])
            return DirDSEntry(ds_name,
                ds_entry_data["kind"], ds_inventory["a-json"], ds_inventory,
                entry_data = {
                    "arg-dir": ds_entry_data, "arg-inv": ds_inventory})
        if "a-json" in ds_entry_data:
            return DirDSEntry(ds_name,  ds_entry_data["kind"],
                ds_entry_data["a-json"],
                entry_data = {"arg-dir": ds_entry_data})
        print(("Dataset %s: no correct source or inv registered "
            "in directory file (%s)") % (ds_name, dir_fname),
            file = sys.stderr)
        sys.exit()
        return None

    @classmethod
    def createByInventory(cls, ds_name, ds_kind, ds_inventory):
        return DirDSEntry(ds_name, ds_kind, ds_inventory["a-json"],
            ds_inventory, entry_data = {"arg-inv": ds_inventory})
