import gzip, json
from threading import Lock

from .family import FamilyInfo
from utils.ixbz2 import IndexBZ2
from app.view.asp_set import AspectSetH
from app.config.view_tune import tuneAspects
#===============================================
class DataSet:
    def __init__(self, data_vault, dataset_info, dataset_path):
        self.mDataVault = data_vault
        self.mDataInfo = dataset_info
        self.mLock  = Lock()
        self.mName = dataset_info["name"]
        self.mDSKind = dataset_info["kind"]
        self.mTotal = dataset_info["total"]
        self.mMongoAgent = (data_vault.getApp().getMongoConnector().
            getDSAgent(dataset_info["mongo"], dataset_info["kind"]))
        self.mAspects = AspectSetH.load(dataset_info["view_schema"])
        self.mFltSchema = dataset_info["flt_schema"]
        self.mPath = dataset_path
        self.mVData = IndexBZ2(self.mPath + "/vdata.ixbz2")
        self.mFamilyInfo = FamilyInfo.load(dataset_info.get("family"))
        tuneAspects(self, self.mAspects)

    def _setFamilyInfo(self, members):
        assert self.mFamilyInfo is None
        self.mFamilyInfo = FamilyInfo(members, members, [], None)

    def __enter__(self):
        self.mLock.acquire()
        return self

    def __exit__(self, type, value, traceback):
        self.mLock.release()

    def descrContext(self, rq_args, rq_descr):
        rq_descr.append("kind=" + self.mDSKind)
        rq_descr.append("dataset=" + self.mName)

    def getApp(self):
        return self.mDataVault.getApp()

    def getDataVault(self):
        return self.mDataVault

    def getName(self):
        return self.mName

    def getDSKind(self):
        return self.mDSKind

    def getTotal(self):
        return self.mTotal

    def getMongoAgent(self):
        return self.mMongoAgent

    def getFltSchema(self):
        return self.mFltSchema

    def getDataInfo(self):
        return self.mDataInfo

    def getFamilyInfo(self):
        return self.mFamilyInfo

    def getViewSchema(self):
        return self.mAspects.dump()

    def _openFData(self):
        return gzip.open(self.mPath + "/fdata.json.gz", "rb")

    def _openPData(self):
        return gzip.open(self.mPath + "/pdata.json.gz", "rb")

    def getRecordData(self, rec_no):
        assert 0 <= rec_no < self.mTotal
        return json.loads(self.mVData[rec_no])

    def getFirstAspectID(self):
        return self.mAspects.getFirstAspectID()

    def getViewSetupReport(self):
        return {"aspects": self.mAspects.dump()}

    def getViewRepr(self, rec_no, research_mode):
        rec_data = self.getRecordData(rec_no)
        return self.mAspects.getViewRepr(rec_data, research_mode)

    def getSourceVersions(self):
        if "meta" in self.mDataInfo:
            if "versions" in self.mDataInfo["meta"]:
                versions = self.mDataInfo["meta"]["versions"]
                return [[key, versions[key]]
                    for key in sorted(versions.keys())]
        return []

    def getBaseDSName(self):
        return self.mDataInfo.get("base")

    def dumpDSInfo(self, navigation_mode = False):
        note, time_label = self.getMongoAgent().getNote()
        ret = {
            "name": self.mName,
            "kind": self.mDSKind,
            "note": note,
            "date-note": time_label}
        base_h = self.mDataVault.getBaseDS(self)
        if base_h is not None:
            ret["base"] = base_h.getName()
        if navigation_mode:
            secondary_seq = self.mDataVault.getSecondaryWS(self)
            if secondary_seq:
                ret["secondary"] = [ws_h.getName() for ws_h in secondary_seq]
            ret["doc-support"] = "doc" in self.mDataInfo
        else:
            ret["src-versions"] = self.getSourceVersions()
        if "doc" in self.mDataInfo:
            ret["doc"] = self.mDataInfo["doc"]
            if base_h is not None and "doc" in base_h.getDataInfo():
                ret["doc-base"] = base_h.getDataInfo()["doc"]
        return ret
