#import sys
import json, codecs, logging
from StringIO import StringIO
from .data_set import DataSet, DataRecord
from .form_tab import formAspectTable
from .cfg_a_json import CONFIG_AJson
from .cfg_data import ObjectAttributeChecker
#===============================================
class DataSet_AJson(DataSet):
    sMainKey = CONFIG_AJson["main_key"]
    def __init__(self, name, fname):
        DataSet.__init__(self, name)
        self.mRecords = []
        self.mRecDict = dict()
        with codecs.open(fname, "r", encoding = "utf-8") as inp:
            for line in inp:
                record = json.loads(line)
                record["_no"] = len(self.mRecords)
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

    def getFirstAspectID(self):
        return "a--" + CONFIG_AJson["view_tabs"][0].getName()

    def reportList(self, output):
        for idx, rec in enumerate(self.mRecords):
            rec_key = rec[self.sMainKey]
            print >> output, ('<div id="li--%d" class="rec-label" '
                'onclick="changeRec(%d)";">%s</div>' %
                (idx, idx, rec_key))

    def getRecKey(self, rec_no):
        return self.mRecords[rec_no][self.sMainKey]

    def getRecord(self, rec_no):
        return DataRecord_AJson(self.mRecords[int(rec_no)])

#===============================================
class DataRecord_AJson(DataRecord):
    def __init__(self, json_obj):
        self.mObj = json_obj

    def getID(self):
        return self.mObj[self.sMainKey]

    def reportIt(self, output):
        print >> output, '<div class="r-tab">'
        for aspect in (CONFIG_AJson["view_tabs"]):
            if aspect.isIgnored():
                continue
            print >> output, ('<button class="r-tablnk %s" id="la--%s" '
                'onclick="chooseAspect(event, \'a--%s\')">%s</button>' %
                (aspect.getAspectKind(), aspect.getName(),
                aspect.getName(), aspect.getTitle()))
        print >> output, '</div>'

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
                        print >> output, "%d:\t%s" % (idx, '|'.join(ddd[:17]))
                        print >> output, "\t|%s" % ('|'.join(ddd[17:37]))
                        print >> output, "\t|%s" %  ('|'.join(ddd[37:]))
                    print >> output, "==^====SCQ======^========"
                else:
                    print >> output, vv
        if collect_str:
            print >> output, collect_str[1:]
            collect_str = ""
