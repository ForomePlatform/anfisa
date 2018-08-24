import json, codecs, random
from .record import DataRecord
from .checker import ObjectAttributeChecker

#===============================================
class DataSet:
    def __init__(self, view_setup, name, fname):
        self.mViewSetup  = view_setup
        self.mName      = name
        self.mDataObjects   = []
        self.mRecDict   = dict()
        self.mMainKey   = self.mViewSetup.configOption("main.key")
        self.mColorCode = self.mViewSetup.configOption("color.code")
        with codecs.open(fname, "r", encoding = "utf-8") as inp:
            for line in inp:
                obj = json.loads(line)
                self.mDataObjects.append(obj)
                self.mRecDict[obj[self.mMainKey]] = obj
        ObjectAttributeChecker.check(self.mViewSetup,
            self.mDataObjects, self.mName)
        r_h = random.WichmannHill(self.mViewSetup.configOption("rand.seed"))
        hashes = range(len(self.mDataObjects))[:]
        r_h.shuffle(hashes)
        self.mRecHash = {idx: hash
            for idx, hash in enumerate(hashes)}

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

    def testLegend(self, legend):
        for rec_no in range(self.getSize()):
            legend.testObj(self.getRecord(rec_no).getObj())

    def _prepareList(self, rec_no_seq):
        ret = []
        for rec_no in rec_no_seq:
            rec = self.mDataObjects[rec_no]
            ret.append([rec_no, rec[self.mMainKey],
                self.mViewSetup.normalizeColorCode(rec.get(self.mColorCode))])
        return ret

    def makeJSonReport(self, rec_no_seq):
        ret = {
            "data-set": self.getName(),
            "total": len(self.mDataObjects) }
        ret["filtered"] = len(rec_no_seq)
        min_rand_size = self.mViewSetup.configOption("rand.min.size")
        sample_rand_size = self.mViewSetup.configOption("rand.sample.size")

        if len(rec_no_seq) <= min_rand_size:
            ret["records"] = self._prepareList(rec_no_seq)
            ret["list-mode"] = "complete"
        else:
            sheet = [(self.mRecHash[rec_no], rec_no)
                for rec_no in rec_no_seq]
            sheet.sort()
            sheet = sheet[:sample_rand_size]
            ret["records"] = self._prepareList(
                [rec_no for hash, rec_no in sheet])
            ret["list-mode"] = "samples"
        return ret
