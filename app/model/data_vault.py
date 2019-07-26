import os, json, logging
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
            with open(info_path, "r", encoding = "utf-8") as inp:
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

    def loadDS(self, ds_name, ds_kind = None):
        ds_path = self.mVaultDir + '/' + ds_name
        info_path =  ds_path + "/dsinfo.json"
        with open(info_path, "r", encoding = "utf-8") as inp:
            ds_info = json.loads(inp.read())
        assert ds_info["name"] == ds_name
        assert not ds_kind or ds_info["kind"] == "ws"
        with self:
            assert ds_info["name"] not in self.mDataSets
            if ds_info["kind"] == "xl":
                ds = XLDataset(self, ds_info, ds_path)
            else:
                assert ds_info["kind"] == "ws"
                ds = Workspace(self, ds_info, ds_path)
            self.mDataSets[ds_info["name"]] = ds
        return ds_name

    def unloadDS(self, ds_name, ds_kind = None):
        with self:
            ds = self.mDataSets[ds_name]
            assert not ds_kind or (
                ds_kind == "ws" and isinstance(ds, Workspace)) or (
                ds_kind == "xl" and isinstance(ds, XLDataset))
            del self.mDataSets[ds_name]

    def _prepareDS(self, rq_args):
        kind = "ws" if "ws" in rq_args else "ds"
        ds = self.mDataSets[rq_args[kind]]
        assert kind == "ds" or ds.getKind().lower() == "ws"
        return ds


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
                rep["workspaces"].append(ds_h.getDSInfo())
            else:
                rep["xl-datasets"].append(ds_h.getDSInfo())
        for reserved_path in glob(self.mVaultDir + "/*"):
            rep["reserved"].append(os.path.basename(reserved_path))
        return rep

    #===============================================
    @RestAPI.vault_request
    def rq__recdata(self, rq_args):
        ds = self._prepareDS(rq_args)
        return ds.getRecordData(int(rq_args.get("rec")))

    #===============================================
    @RestAPI.vault_request
    def rq__reccnt(self, rq_args):
        ds = self._prepareDS(rq_args)
        modes = rq_args.get("m", "").upper()
        return ds.getViewRepr(int(rq_args.get("rec")),
            'R' in modes or ds.getKind().lower == "xl")

    #===============================================
    @RestAPI.vault_request
    def rq__dsinfo(self, rq_args):
        ds = self._prepareDS(rq_args)
        note = rq_args.get("note")
        if note is not None:
            with ds:
                ds.getMongoAgent().setNote(note)
        return ds.getDSInfo()

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

    #===============================================
    @RestAPI.vault_request
    def rq__solutions(self, rq_args):
        ds = self.mDataSets[rq_args["ds"]]
        return ds.getIndex().getCondEnv().reportSolutions()

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
