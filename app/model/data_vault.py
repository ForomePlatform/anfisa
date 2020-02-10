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

import os, json, logging
from glob import glob
from threading import Lock

from .rest_api import RestAPI
from .sol_env import SolutionEnv
from app.ws.workspace import Workspace
from app.xl.xl_dataset import XLDataset
from utils.log_err import logException
from utils.sync_obj import SyncronizedObject
#===============================================
class DataVault(SyncronizedObject):
    def __init__(self, application, vault_dir):
        SyncronizedObject.__init__(self)
        self.mApp = application
        self.mVaultDir = os.path.abspath(vault_dir)
        self.mLock  = Lock()
        self.mDataSets = dict()
        self.mSolEnvDict = dict()
        self.mScanModeLevel = 0
        self.mIntVersion = 0
        self.scanAll(False)

        names = [[], []]
        for ds_h in self.mDataSets.values():
            if ds_h.getDSKind() == "xl":
                names[0].append(ds_h.getName())
            else:
                names[1].append(ds_h.getName())
        logging.info("Vault %s started with %d/%d datasets" %
            (self.mVaultDir, len(names[0]), len(names[1])))
        if len(names[0]) > 0:
            logging.info("XL-datasets: " + " ".join(sorted(names[0])))
        if len(names[1]) > 0:
            logging.info("WS-datasets: " + " ".join(sorted(names[1])))

    def scanAll(self, report_it = True):
        with self:
            if self.mScanModeLevel > 0:
                self.mScanModeLevel = 2
                return False
            self.mScanModeLevel = 1
        while True:
            self._scanAll(report_it)
            with self:
                if self.mScanModeLevel < 2:
                    self.mScanModeLevel = 0
                    return True
                self.mScanModeLevel = 1

    def _scanAll(self, report_it):
        prev_set = set(self.mDataSets.keys())
        new_path_list = list(glob(self.mVaultDir + "/*/active"))
        new_set = set()
        for active_path in new_path_list:
            ds_path = os.path.dirname(active_path)
            info_path = ds_path + "/dsinfo.json"
            if not os.path.exists(info_path):
                continue
            ds_name = os.path.basename(ds_path)
            if ds_name not in prev_set:
                try:
                    self.loadDS(ds_name)
                except Exception:
                    logException("Bad dataset load: " + ds_name)
                    continue
                new_set.add(ds_name)
            else:
                prev_set.remove(ds_name)
        if len(new_set) > 0 and report_it:
            logging.info(("New loaded datasets(%d): " % len(new_set))
                + " ".join(sorted(new_set)))
        if len(prev_set) > 0:
            logging.info(("Dropped datasets(%d): " % len(prev_set))
                + " ".join(sorted(prev_set)))
            for ds_name in prev_set:
                self.unloadDS(ds_name)

    def descrContext(self, rq_args, rq_descr):
        if "ds" in rq_args:
            rq_descr.append("ds=" + rq_args["ds"])
        if "ws" in rq_args:
            rq_descr.append("ds=" + rq_args["ws"])

    def getApp(self):
        return self.mApp

    def getDir(self):
        return self.mVaultDir

    def getDS(self, ds_name, ds_kind = None):
        ds_h = self.mDataSets.get(ds_name)
        if ds_h and ds_kind is not None and ds_h.getDSKind() != ds_kind:
            assert False, "DS kinds conflicts: %s/%s" % (
                ds_h.getDSKind(), ds_kind)
        return ds_h

    def checkNewDataSet(self, ds_name):
        with self:
            return ds_name not in self.mDataSets

    def loadDS(self, ds_name, ds_kind = None):
        with self:
            assert ds_name not in self.mDataSets
        ds_path = self.mVaultDir + '/' + ds_name
        info_path = ds_path + "/dsinfo.json"
        with open(info_path, "r", encoding = "utf-8") as inp:
            ds_info = json.loads(inp.read())
        assert ds_info["name"] == ds_name
        assert not ds_kind or ds_info["kind"] == ds_kind
        if ds_info["kind"] == "xl":
            ds_h = XLDataset(self, ds_info, ds_path)
        else:
            assert ds_info["kind"] == "ws"
            ds_h = Workspace(self, ds_info, ds_path)
        with self:
            self.mDataSets[ds_info["name"]] = ds_h
        self.mIntVersion += 1
        return ds_name

    def unloadDS(self, ds_name, ds_kind = None):
        with self:
            ds_h = self.mDataSets[ds_name]
            assert not ds_kind or ds_kind == ds_h.getDSKind()
            del self.mDataSets[ds_name]
            self.mIntVersion += 1

    def getBaseDS(self, ds_h):
        return self.mDataSets.get(ds_h.getBaseDSName())

    def getSecondaryWSNames(self, ds_h):
        ret = []
        for ws_h in self.mDataSets.values():
            if ws_h.getBaseDSName() == ds_h.getName():
                ret.append(ws_h)
        return sorted(ret, key = lambda ws_h: ws_h.getName())

    def makeSolutionEnv(self, ds_h):
        root_name = ds_h.getRootDSName()
        assert root_name
        with self:
            if root_name not in self.mSolEnvDict:
                self.mSolEnvDict[root_name] = SolutionEnv(
                    self.mApp.getMongoConnector(), root_name)
            return self.mSolEnvDict[root_name]

    #===============================================
    @staticmethod
    def _emptyDSEntry(name, root = None):
        return {"name": name, "kind": None, "root": name if name else root}

    @classmethod
    def _entryPath(cls, ds_dict, ds_info):
        if not ds_info.get("base"):
            return [ds_info["name"]]
        return (cls._entryPath(ds_dict, ds_dict[ds_info["base"]])
            + [ds_info["name"]])

    @RestAPI.vault_request
    def rq__dirinfo(self, rq_args):
        ds_dict = {ds_h.getName(): ds_h.dumpDSInfo(navigation_mode = True)
            for ds_h in self.mDataSets.values()}
        for ds_info in list(ds_dict.values()):
            if ds_info.get("base") and ds_info["base"] not in ds_dict:
                ds_dict[ds_info["base"]] = self._emptyDSEntry(
                    ds_info["base"], ds_info["root"])
            if ds_info["root"] not in ds_dict:
                ds_dict[ds_info["root"]] = self._emptyDSEntry(
                    ds_info["root"])
        ds_sheet = [self._entryPath(ds_dict, ds_info)
            for ds_info in ds_dict.values()]
        ds_sheet.sort()
        ds_list = []
        for idx, ds_path in enumerate(ds_sheet):
            ds_info = ds_dict[ds_path[-1]]
            assert ds_info["name"] == ds_path[-1]
            ds_info["v-level"] = len(ds_path) - 1
            ds_info["v-idx"] = len(ds_list)
            ds_list.append(ds_path[-1])
            idx_to = idx + 1
            while (idx_to + 1 < len(ds_sheet)
                    and len(ds_sheet[idx_to + 1]) > len(ds_path)
                    and ds_sheet[idx_to + 1][:len(ds_path)] == ds_path):
                idx_to += 1
            ds_info["v-idx-to"] = idx_to
        for reserved_path in glob(self.mVaultDir + "/*"):
            name = os.path.basename(reserved_path)
            if name not in ds_dict:
                ds_dict[name] = None
        return {
            "version": self.mApp.getVersionCode(),
            "ds-list": ds_list,
            "ds-dict": ds_dict}

    #===============================================
    @RestAPI.vault_request
    def rq__single_cnt(self, rq_args):
        record = json.loads(rq_args["record"])
        return self.mApp.viewSingleRecord(record)

    #===============================================
    @RestAPI.vault_request
    def rq__job_status(self, rq_args):
        return self.mApp.askJobStatus(rq_args["task"])

    #===============================================
    # Administrator authorization required
    @RestAPI.vault_request
    def rq__adm_update(self, rq_args):
        self.scanAll()
        return "Updated"
