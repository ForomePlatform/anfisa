import json, codecs
from .record import DataRecord

#===============================================
class DataSet:
    def __init__(self, view_setup, name, fname):
        self.mViewSetup  = view_setup
        self.mName      = name
        self.mDataObjects   = []
        self.mMainKey   = self.mViewSetup.configOption("main.key")
        self.mColorCode = self.mViewSetup.configOption("color.code")
        with codecs.open(fname, "r", encoding = "utf-8") as inp:
            for line in inp:
                obj = json.loads(line)
                self.mDataObjects.append(obj)
        uniq_keys = self.mViewSetup.configOption("uniq.keys")
        seed = self.mViewSetup.configOption("rand.seed")
        self.mRecHash = []
        for obj in self.mDataObjects:
            uniq_tag = tuple([seed] + [obj[key] for key in uniq_keys])
            self.mRecHash.append(hash(uniq_tag))

    def getName(self):
        return self.mName

    def getViewSetup(self):
        return self.mViewSetup

    def getFirstAspectID(self):
        return "a--" + self.mViewSetup.getAspects()[0].getName()

    def reportList(self, output):
        for idx, rec in enumerate(self.mDataObjects):
            rec_key = rec[self.mMainKey]
            rec_color = self.mViewSetup.normalizeColorCode(
                rec.get(self.mColorCode))
            print >> output, ('<div id="li--%d" class="rec-label %s" '
                'onclick="changeRec(%d)";">%s</div>' %
                (idx, rec_color, idx, rec_key))

    def getSize(self):
        return len(self.mDataObjects)

    def getRecKey(self, rec_no):
        return self.mDataObjects[rec_no][self.mMainKey]

    def getRecord(self, rec_no):
        return DataRecord(self, self.mDataObjects[int(rec_no)])

    def iterDataObjects(self):
        return iter(self.mDataObjects)

    def _prepareList(self, rec_no_seq):
        ret = []
        for rec_no in rec_no_seq:
            rec = self.mDataObjects[rec_no]
            ret.append([rec_no, rec[self.mMainKey],
                self.mViewSetup.normalizeColorCode(rec.get(self.mColorCode))])
        return ret

    def makeJSonReport(self, rec_no_seq, random_mode):
        ret = {
            "data-set": self.getName(),
            "total": len(self.mDataObjects) }
        ret["filtered"] = len(rec_no_seq)

        if (random_mode and len(rec_no_seq) >
                self.mViewSetup.configOption("rand.min.size")):
            sheet = [(self.mRecHash[rec_no], rec_no)
                for rec_no in rec_no_seq]
            sheet.sort()
            sheet = sheet[:self.mViewSetup.configOption("rand.sample.size")]
            ret["records"] = self._prepareList(
                [rec_no for hash, rec_no in sheet])
            ret["list-mode"] = "samples"
        else:
            ret["records"] = self._prepareList(rec_no_seq)
            ret["list-mode"] = "complete"
        return ret
