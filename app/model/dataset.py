import gzip, json
from threading import Lock

from .family import FamilyInfo
from utils.ixbz2 import IndexBZ2
from app.view.asp_set import AspectSetH
from app.view.attr import AttrH
#===============================================
class DataSet:
    def __init__(self, data_vault, dataset_info, dataset_path):
        self.mDataVault = data_vault
        self.mDataInfo = dataset_info
        self.mLock  = Lock()
        self.mName = dataset_info["name"]
        self.mDSKind = dataset_info["kind"]
        self.mTotal = dataset_info["total"]
        self.mMongoName = dataset_info["mongo"]
        self.mAspects = AspectSetH.load(dataset_info["view_schema"])
        self.mFltSchema = dataset_info["flt_schema"]
        self.mPath = dataset_path
        self.mVData = IndexBZ2(self.mPath + "/vdata.ixbz2")
        self.mFamilyInfo = FamilyInfo.load(dataset_info.get("family"))

    def _setFamilyInfo(self, members):
        assert self.mFamilyInfo is None
        self.mFamilyInfo = FamilyInfo(members, members, [], None)

    def __enter__(self):
        self.mLock.acquire()
        return self

    def __exit__(self, type, value, traceback):
        self.mLock.release()

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

    def getMongoName(self):
        return self.mMongoName

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
        return {"aspects": self.mAspects.dump(),
            "opts": AttrH.getJSonOptions()}

    def getViewRepr(self, rec_no, research_mode):
        rec_data = self.getRecordData(rec_no)
        return self.mAspects.getViewRepr(rec_data, research_mode)

    def getVersionData(self):
        ret = [["version", self.mDataVault.getApp().getVersionCode()]]
        if "meta" in self.mDataInfo:
            if "versions" in self.mDataInfo["meta"]:
                versions = self.mDataInfo["meta"]["versions"]
                for key in sorted(versions.keys()):
                    ret.append([key, versions[key]])
        return ret
