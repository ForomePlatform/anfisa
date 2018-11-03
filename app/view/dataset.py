import json, codecs
from xml.sax.saxutils import escape

from app.model.path_works import AttrFuncPool
from .attr import AttrH
from .checker import ViewDataChecker
#===============================================
class DataSet:
    def __init__(self, view_setup, name, fname):
        self.mViewSetup  = view_setup
        self.mName      = name
        self.mDataObjects   = []
        self.mLabelKeyF  =  AttrFuncPool.makeFunc(
            self.mViewSetup.configOption("label.key"))
        self.mColorCodeF = AttrFuncPool.makeFunc(
            self.mViewSetup.configOption("color.code"))
        self.mDataKeys  = []
        uniq_keys_f = [AttrFuncPool.makeFunc(fpath)
            for fpath in self.mViewSetup.configOption("uniq.keys")]
        with codecs.open(fname, "r", encoding = "utf-8") as inp:
            for line in inp:
                obj = json.loads(line)
                self.mDataObjects.append(obj)
                keys = [str(path_f(obj)[0]) for path_f in uniq_keys_f]
                self.mDataKeys.append('-'.join(keys))
        seed = str(self.mViewSetup.configOption("rand.seed"))
        self.mRecHash = [hash(seed + rec_key)
            for rec_key in self.mDataKeys]
        ViewDataChecker.check(self.mViewSetup, self)

    def getName(self):
        return self.mName

    def getViewSetup(self):
        return self.mViewSetup

    def getSize(self):
        return len(self.mDataObjects)

    def getRecKey(self, rec_no):
        return self.mDataKeys[rec_no]

    def getRecData(self, rec_no):
        return self.mDataObjects[int(rec_no)]

    def iterDataObjects(self):
        return iter(self.mDataObjects)

    def enumDataKeys(self):
        return enumerate(self.mDataKeys)

    def _prepareList(self, rec_no_seq, marked_set):
        ret = []
        for rec_no in rec_no_seq:
            rec = self.mDataObjects[rec_no]
            label = self.mLabelKeyF(rec)[0]
            ret.append([rec_no, escape(label),
                self.mViewSetup.normalizeColorCode(self.mColorCodeF(rec)),
                rec_no in marked_set])
        return ret

    def makeJSonReport(self, rec_no_seq, random_mode, marked_set):
        ret = {
            "data-set": self.getName(),
            "total": len(self.mDataObjects)}
        ret["filtered"] = len(rec_no_seq)

        if (random_mode and len(rec_no_seq) >
                self.mViewSetup.configOption("rand.min.size")):
            sheet = [(self.mRecHash[rec_no], rec_no)
                for rec_no in rec_no_seq]
            sheet.sort()
            sheet = sheet[:self.mViewSetup.configOption("rand.sample.size")]
            ret["records"] = self._prepareList(
                [rec_no for hash, rec_no in sheet], marked_set)
            ret["list-mode"] = "samples"
        else:
            ret["records"] = self._prepareList(rec_no_seq, marked_set)
            ret["list-mode"] = "complete"
        return ret

    def makeExportFile(self, workname, rec_no_seq, export_func):
        return export_func(workname, [self.mDataObjects[rec_no]
            for rec_no in rec_no_seq])

    def getViewSetupJSon(self):
        return {"aspects": [asp_h.getJSonObj()
            for asp_h in self.mViewSetup.iterAspects()],
            "opts": AttrH.getJSonOptions()}

    def getJSonRecRepr(self, rec_no, research_mode):
        ret = []
        rec_data = self.getRecData(rec_no)
        for aspect in self.mViewSetup.iterAspects():
            if aspect.isIgnored():
                continue
            if aspect.checkResearchBlock(research_mode):
                continue
            ret.append(aspect.getJSonRepr(rec_data, research_mode))
        return ret
