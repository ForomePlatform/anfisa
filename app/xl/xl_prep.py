import sys, os, random
from datetime import datetime, timedelta
from copy import deepcopy
from .json_proto import DRUID_LOAD_TEMPLATE

#===============================================
class XL_Preparator:
    def __init__(self, flt_legend, datasource,
            work_dir, start_time):
        self.mFltLegend = flt_legend
        self.mDataSource = datasource
        self.mWorkDir = os.path.abspath(work_dir)
        self.mExtSchema = deepcopy(DRUID_LOAD_TEMPLATE)
        self.mEnumStat = dict()
        self.mVarStat  = dict()

        ext_dim_container = self.mExtSchema["spec"]["dataSchema"]\
            ["parser"]["parseSpec"]["dimensionsSpec"]["dimensions"]

        for f_unit in self.mFltLegend.iterUnits():
            if f_unit.getType() in {"long", "float"}:
                ext_dim_container.append({
                    "name": f_unit.getName(),
                    "type": f_unit.getType()})
                self.mVarStat[f_unit.getName()] = [0, 0]
            else:
                ext_dim_container.append(f_unit.getName())
                self.mEnumStat[f_unit.getName()] = set()
                if f_unit.getType() == "status":
                    self.mVarStat[f_unit.getName()] = [0, 0]

        ext_spec = self.mExtSchema["spec"]
        ext_spec["dataSchema"]["dataSource"] = self.mDataSource
        ext_io = ext_spec["ioConfig"]["firehose"]
        ext_io["baseDir"] = self.mWorkDir
        ext_io["filter"] = "xl.data.json"
        self.mOutFileName = self.mWorkDir + "/xl.data.json"
        self.mCurOrd = 0
        self.mCurTime = self.str2dt(start_time)
        self.mRandH = random.WichmannHill(179)

    def getOutFileName(self):
        return self.mOutFileName

    def getExtSchema(self):
        return self.mExtSchema

    def makeIntSchema(self):
        int_schema = {
            "datasource": self.mDataSource,
            "units": []}

        for f_unit in self.mFltLegend.iterUnits():
            int_entry = {
                "name": f_unit.getName(),
                "title": f_unit.getTitle(),
                "no": f_unit.getUnitIdx(),
                "type": f_unit.getType()}
            if f_unit.getVGroup() is not None:
                int_entry["vgroup"] = f_unit.getVGroup().getTitle()
            var_stat = self.mVarStat.get(f_unit.getName())
            if var_stat is not None and var_stat[0] == 0:
                print >> sys.stderr, "Dummy unit:", f_unit.getName()
                int_entry["type"] = "dummy " + int_entry["type"]
            enum_stat = self.mEnumStat.get(f_unit.getName())
            if enum_stat is not None:
                variants = []
                for var in f_unit.getExtractor().getVariantSet().getVariants():
                    if var in enum_stat:
                        variants.append(var)
                if var_stat is not None:
                    if var_stat[1] > 0:
                        variants.append(None)
                    if len(variants) < 2:
                        print >> sys.stderr, "Dummy status unit:", \
                            f_unit.getName()
                        int_entry["type"] = "dummy status"
                elif len(variants) == 0:
                    print >> sys.stderr, "Dummy enum unit:", \
                        f_unit.getName()
                    int_entry["type"] = "dummy " + int_entry["type"]
                int_entry["variants"] = variants
            int_schema["units"].append(int_entry)
        return int_schema

    sTimeStep = timedelta(seconds = 1)

    @staticmethod
    def str2dt(text):
       year, month, day = map(int, text.split('-'))
       return datetime(year = year, month = month, day = day)

    def procRecord(self, rec_data):
        rec_values = self.mFltLegend.getColCount() * [None]
        self.mFltLegend.fillRecord(rec_data, rec_values)
        out_rec = {
            "time": self.mCurTime.isoformat(),
            "_ord": self.mCurOrd,
            "_rand": self.mRandH.getrandbits(32)}
        for f_unit in self.mFltLegend.iterUnits():
            value = f_unit.ruleValue(rec_values)
            if f_unit.getType() in {"bool-set", "multi-set"}:
                if not value:
                    continue
                value = sorted(value)
                self.mEnumStat[f_unit.getName()] |= set(value)
            else:
                if value is None:
                    self.mVarStat[f_unit.getName()][1] += 1
                    continue
                self.mVarStat[f_unit.getName()][0] += 1
                if f_unit.getType() == "status":
                    self.mEnumStat[f_unit.getName()].add(value)
            out_rec[f_unit.getName()] = value
        self.mCurTime += self.sTimeStep
        self.mCurOrd += 1
        return out_rec

