import json, codecs
from xml.sax.saxutils import escape

from .record import DataRecord
#===============================================
class DataSet:
    def __init__(self, view_setup, name, fname):
        self.mViewSetup  = view_setup
        self.mName      = name
        self.mDataObjects   = []
        self.mLabelKey  = self.mViewSetup.configOption("label.key")
        self.mColorCode = self.mViewSetup.configOption("color.code")
        self.mDataKeys  = []
        uniq_keys = self.mViewSetup.configOption("uniq.keys")
        with codecs.open(fname, "r", encoding = "utf-8") as inp:
            for line in inp:
                obj = json.loads(line)
                self.mDataObjects.append(obj)
                self.mDataKeys.append(
                    '-'.join([str(obj[key]) for key in uniq_keys]))
        seed = str(self.mViewSetup.configOption("rand.seed"))
        self.mRecHash = [hash(seed + rec_key)
            for rec_key in self.mDataKeys]

    def getName(self):
        return self.mName

    def getViewSetup(self):
        return self.mViewSetup

    def reportList(self, output):
        for idx, rec in enumerate(self.mDataObjects):
            rec_key = rec[self.mLabelKey]
            rec_color = self.mViewSetup.normalizeColorCode(
                rec.get(self.mColorCode))
            print >> output, ('<div id="li--%d" class="rec-label %s" '
                'onclick="changeRec(%d)";">%s</div>' %
                (idx, rec_color, idx, rec_key))

    def getSize(self):
        return len(self.mDataObjects)

    def getRecKey(self, rec_no):
        return self.mDataKeys[rec_no]

    def getRecord(self, rec_no):
        return DataRecord(self, self.mDataObjects[int(rec_no)])

    def iterDataObjects(self):
        return iter(self.mDataObjects)

    def enumDataKeys(self):
        return enumerate(self.mDataKeys)

    def _prepareList(self, rec_no_seq, marked_set):
        ret = []
        for rec_no in rec_no_seq:
            rec = self.mDataObjects[rec_no]
            ret.append([rec_no, escape(rec[self.mLabelKey]),
                self.mViewSetup.normalizeColorCode(rec.get(self.mColorCode)),
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
