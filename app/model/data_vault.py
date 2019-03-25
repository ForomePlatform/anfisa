import os, codecs, json, logging
from glob import glob
from threading import Lock

from .workspace import Workspace
from .rest_api import RestAPI
from app.xl.xl_dataset import XLDataset

#===============================================
class DataVault:
    def __init__(self, application, vault_dir):
        self.mApp = application
        self.mVaultDir = os.path.abspath(vault_dir)
        self.mLock  = Lock()
        self.mDataSets = dict()

        workspaces = []
        for active_path in glob(self.mVaultDir + "/*/active"):
            ds_path = os.path.dirname(active_path)
            info_path =  ds_path + "/dsinfo.json"
            if not os.path.exists(info_path):
                continue
            with codecs.open(info_path, "r", encoding = "utf-8") as inp:
                ds_info = json.loads(inp.read())
            if ds_info["kind"] == "xl":
                assert ds_info["name"] not in self.mDataSets
                self.mDataSets[ds_info["name"]] = XLDataset(
                    self, ds_info, ds_path)
            else:
                assert ds_info["kind"] == "ws"
                workspaces.append((ds_info, ds_path))
        for ds_info, ds_path in workspaces:
            assert ds_info["name"] not in self.mDataSets
            self.mDataSets[ds_info["name"]] = Workspace(
                    self, ds_info, ds_path)
        logging.info("Vault %s started with %d datasets" %
            (self.mVaultDir, len(self.mDataSets)))

    def __enter__(self):
        self.mLock.acquire()
        return self

    def __exit__(self, type, value, traceback):
        self.mLock.release()

    def getApp(self):
        return self.mApp

    def getDir(self):
        return self.mVaultDir

    def getWS(self, ws_name):
        ds = self.mDataSets.get(ws_name)
        return ds if ds and ds.getDSKind() == "ws" else None

    def getXL(self, ds_name):
        ds = self.mDataSets.get(ds_name)
        return ds if ds and ds.getDSKind() == "xl" else None

    def checkNewDataSet(self, ds_name):
        with self:
            return ds_name not in self.mDataSets

    def loadNewWS(self, wsname):
        ds_path = self.mVaultDir + '/' + wsname
        info_path =  ds_path + "/dsinfo.json"
        with codecs.open(info_path, "r", encoding = "utf-8") as inp:
            ds_info = json.loads(inp.read())
        assert ds_info["kind"] == "ws" and ds_info["name"] == wsname
        with self:
            assert ds_info["name"] not in self.mDataSets
            self.mDataSets[ds_info["name"]] = Workspace(
                self, ds_info, ds_path)
        return wsname

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
                rep["workspaces"].append(ds_h.dump())
            else:
                rep["xl-datasets"].append(ds_h.dump())
        for reserved_path in glob(self.mVaultDir + "/*"):
            rep["reserved"].append(os.path.basename(reserved_path))
        return rep

    #===============================================
    @RestAPI.vault_request
    def rq__single_cnt(self, rq_args):
        record = json.loads(rq_args["record"])
        modes = rq_args.get("m", "").upper()
        return self.mApp.viewSingleRecord(record, 'R' in modes)

    #===============================================
    @RestAPI.vault_request
    def rq__job_status(self, rq_args):
        return self.mApp.askJobStatus(rq_args["task"])

