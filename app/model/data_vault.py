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

        workspaces = []
        names = [[], []]
        for active_path in glob(self.mVaultDir + "/*/active"):
            ds_path = os.path.dirname(active_path)
            info_path = ds_path + "/dsinfo.json"
            if not os.path.exists(info_path):
                continue
            with open(info_path, "r", encoding = "utf-8") as inp:
                ds_info = json.loads(inp.read())
            if ds_info["kind"] == "xl":
                assert ds_info["name"] not in self.mDataSets
                try:
                    ds_h = XLDataset(self, ds_info, ds_path)
                except Exception:
                    logException("Bad XL-dataset load: " + ds_info["name"])
                    continue
                self.mDataSets[ds_info["name"]] = ds_h
                names[0].append(ds_info["name"])
            else:
                assert ds_info["kind"] == "ws"
                workspaces.append((ds_info, ds_path))
        for ds_info, ds_path in workspaces:
            assert ds_info["name"] not in self.mDataSets
            try:
                ws_h = Workspace(self, ds_info, ds_path)
            except Exception:
                logException("Bad WS-dataset load: " + ds_info["name"])
                continue
            self.mDataSets[ds_info["name"]] = ws_h
            names[1].append(ds_info["name"])
        logging.info("Vault %s started with %d/%d datasets" %
            (self.mVaultDir, len(names[0]), len(names[1])))
        if len(names[0]) > 0:
            logging.info("XL-datasets: " + " ".join(names[0]))
        if len(names[1]) > 0:
            logging.info("WS-datasets: " + " ".join(names[1]))

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
            assert False, "DS kinds conflictsL %s/%s" % (
                ds_h.getDSKind(), ds_kind)
        return ds_h

    def checkNewDataSet(self, ds_name):
        with self:
            return ds_name not in self.mDataSets

    def loadDS(self, ds_name, ds_kind = None):
        ds_path = self.mVaultDir + '/' + ds_name
        info_path = ds_path + "/dsinfo.json"
        with open(info_path, "r", encoding = "utf-8") as inp:
            ds_info = json.loads(inp.read())
        assert ds_info["name"] == ds_name
        assert not ds_kind or ds_info["kind"] == "ws"
        with self:
            if ds_info["name"] not in self.mDataSets:
                if ds_info["kind"] == "xl":
                    ds_h = XLDataset(self, ds_info, ds_path)
                else:
                    assert ds_info["kind"] == "ws"
                    ds_h = Workspace(self, ds_info, ds_path)
                self.mDataSets[ds_info["name"]] = ds_h
        return ds_name

    def unloadDS(self, ds_name, ds_kind = None):
        with self:
            ds_h = self.mDataSets[ds_name]
            assert not ds_kind or (
                ds_kind == "ws" and isinstance(ds_h, Workspace)) or (
                ds_kind == "xl" and isinstance(ds_h, XLDataset))
            del self.mDataSets[ds_name]

    def getBaseDS(self, ws_h):
        return self.mDataSets.get(ws_h.getBaseDSName())

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
    @RestAPI.vault_request
    def rq__dirinfo(self, rq_args):
        rep = {
            "version": self.mApp.getVersionCode(),
            "workspaces": [],
            "xl-datasets": [],
            "reserved": []}
        for ds_name in sorted(self.mDataSets.keys()):
            ds_h = self.mDataSets[ds_name]
            if ds_h.getDSKind() == "ws":
                rep["workspaces"].append(
                    ds_h.dumpDSInfo(navigation_mode = True))
            else:
                rep["xl-datasets"].append(
                    ds_h.dumpDSInfo(navigation_mode = True))
        for reserved_path in glob(self.mVaultDir + "/*"):
            rep["reserved"].append(os.path.basename(reserved_path))
        return rep

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
    def rq__adm_ds_on(self, rq_args):
        self.loadDS(rq_args["ds"])
        return []

    #===============================================
    @RestAPI.vault_request
    def rq__adm_ds_off(self, rq_args):
        self.unloadDS(rq_args["ds"])
        return []
