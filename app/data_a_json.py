#import sys
import json, codecs, logging, random
from StringIO import StringIO
from xml.sax.saxutils import escape

from .data_set import DataSet, DataRecord
from .form_tab import formAspectTable
from .cfg_a_json import CONFIG_AJson
from .cfg_data import ObjectAttributeChecker

#===============================================
RAND_SEED = 179
MAX_COMPLETE_LIST_SIZE = 100
SAMPLE_LIST_SIZE = 100

#===============================================
class DataSet_AJson(DataSet):
    sMainKey = CONFIG_AJson["main_key"]
    sColorCode = CONFIG_AJson["color_code"]
    sColors = {"red", "red-cross", "yellow", "yellow-cross", "green"}
    sDefaultColor = "grey"

    def __init__(self, name, fname):
        DataSet.__init__(self, name)
        self.mRecords = []
        self.mRecDict = dict()
        with codecs.open(fname, "r", encoding = "utf-8") as inp:
            for line in inp:
                record = json.loads(line)
                self.mRecords.append(record)
        checker = ObjectAttributeChecker(
            CONFIG_AJson["view_tabs"], CONFIG_AJson["attrs_to_ignore"])
        for rec in self.mRecords:
            self.mRecDict[rec[self.sMainKey]] = rec
            checker.checkObj(rec)
        if not checker.finishUp():
            report = StringIO()
            print >> report, "Errors in DataRecord_AJson %s" % name
            checker.reportBadAttributes(report)
            logging.error(report.getvalue())
        else:
            logging.warning("Attrs are all set for DataRecord_AJson %s"
                % name)
        global RAND_SEED
        r_h = random.WichmannHill(RAND_SEED)
        hashes = range(len(self.mRecords))[:]
        r_h.shuffle(hashes)
        self.mRecHash = {idx: hash
            for idx, hash in enumerate(hashes)}


    def getFirstAspectID(self):
        return "a--" + CONFIG_AJson["view_tabs"][0].getName()

    def reportList(self, output):
        for idx, rec in enumerate(self.mRecords):
            rec_key = rec[self.sMainKey]
            if self.sColorCode:
                rec_color = rec.get(self.sColorCode)
                if rec_color not in self.sColors:
                    rec_color = self.sDefaultColor
            print >> output, ('<div id="li--%d" class="rec-label %s" '
                'onclick="changeRec(%d)";">%s</div>' %
                (idx, rec_color, idx, rec_key))

    def getNRecords(self):
        return len(self.mRecords)

    def getRecKey(self, rec_no):
        return self.mRecords[rec_no][self.sMainKey]

    def getRecord(self, rec_no):
        return DataRecord_AJson(self.mRecords[int(rec_no)])

    def _prepareList(self, rec_no_seq):
        ret = []
        for rec_no in rec_no_seq:
            rec = self.mRecords[rec_no]
            rec_key = rec[self.sMainKey]
            rec_color = rec.get(self.sColorCode)
            if rec_color not in self.sColors:
                rec_color = self.sDefaultColor
            ret.append([rec_no, rec_key, rec_color])
        return ret

    def makeJSonReport(self, rec_no_seq):
        global MAX_COMPLETE_LIST_SIZE, SAMPLE_LIST_SIZE
        ret = {
            "data-set": self.getName(),
            "total": len(self.mRecords) }
        ret["filtered"] = len(rec_no_seq)
        if len(rec_no_seq) <= MAX_COMPLETE_LIST_SIZE:
            ret["records"] = self._prepareList(rec_no_seq)
            ret["list-mode"] = "complete"
        else:
            sheet = [(self.mRecHash[rec_no], rec_no)
                for rec_no in rec_no_seq]
            sheet.sort()
            sheet = sheet[:SAMPLE_LIST_SIZE]
            ret["records"] = self._prepareList(
                [rec_no for hash, rec_no in sheet])
            ret["list-mode"] = "samples"
        return ret

#===============================================
class DataRecord_AJson(DataRecord):
    def __init__(self, json_obj):
        self.mObj = json_obj

    def getObj(self):
        return self.mObj

    def getID(self):
        return self.mObj[self.sMainKey]

    def reportIt(self, output, hot_data):
        print >> output, '<div class="r-tab">'
        for aspect in (CONFIG_AJson["view_tabs"]):
            if aspect.isIgnored():
                continue
            print >> output, ('<button class="r-tablnk %s" id="la--%s" '
                'onclick="chooseAspect(event, \'a--%s\')">%s</button>' %
                (aspect.getAspectKind(), aspect.getName(),
                aspect.getName(), aspect.getTitle()))
        if hot_data is not None:
            asp_kind, asp_name, asp_title = "tech", "hot_data", "Hot<br/>Data"
            print >> output, ('<button class="r-tablnk %s" id="la--%s" '
                'onclick="chooseAspect(event, \'a--%s\')">%s</button>' %
                (asp_kind, asp_name, asp_name, asp_title))
        print >> output, '</div>'

        print >> output, '<div id="r-cnt-container">'
        for aspect in (CONFIG_AJson["view_tabs"]):
            if aspect.isIgnored():
                continue
            print >> output, ('<div id="a--%s" class="r-tabcnt">' %
                aspect.getName())
            if aspect.getName() == "input":
                self.reportInput(output)
            else:
                formAspectTable(output, aspect, self.mObj)
            print >> output, '</div>'
        if hot_data is not None:
            print >> output, ('<div id="a--%s" class="r-tabcnt">' % asp_name)
            self.reportHotData(output, hot_data)
            print >> output, '</div>'

        print >> output, '</div>'

    def reportInput(self, output):
        if "input" not in self.mObj:
            print >> output, '<p class="error">No input data</p>'
            return
        print >> output, '<pre>'
        collect_str = ""
        for fld in self.mObj["input"].split('\t'):
            if len(fld) < 40:
                if len(collect_str) < 60:
                    collect_str += "\t" + fld
                else:
                    print >> output, collect_str[1:]
                    collect_str = "\t" + fld
                continue
            if collect_str:
                print >> output, collect_str[1:]
                collect_str = ""
            for vv in fld.split(';'):
                var, q, val = vv.partition('=')
                if var == "CSQ":
                    print >> output, "==v====SCQ======v========"
                    for idx, dt in enumerate(val.split(',')):
                        ddd = dt.split('|')
                        print >> output, "%d:\t%s" % (idx, '|'.join(ddd[:12]))
                        print >> output, "\t|%s" % ('|'.join(ddd[12:29]))
                        print >> output, "\t|%s" % ('|'.join(ddd[28:33]))
                        print >> output, "\t|%s" % ('|'.join(ddd[33:40]))
                        print >> output, "\t|%s" % ('|'.join(ddd[40:50]))
                        print >> output, "\t|%s" % ('|'.join(ddd[50:]))
                    print >> output, "==^====SCQ======^========"
                else:
                    print >> output, vv
        if collect_str:
            print >> output, collect_str[1:]
            collect_str = ""

    def reportHotData(self, output, hot_data):
        print >> output, '<table id="rec-hot_data">'
        for data_name, data_value in hot_data:
            if (not data_value):
                continue
            print >> output, (
                '<tr><td class="title">%s</td>' % escape(data_name))
            print >> output, (
                '<td class="norm">%s</td></tr>' % ["no", "yes"][data_value])
        print >> output, '</table>'
