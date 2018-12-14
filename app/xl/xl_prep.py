import os, random
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
        self.mIntSchema = {
            "datasource": self.mDataSource,
            "units": []}

        ext_dim_container = self.mExtSchema["spec"]["dataSchema"]\
            ["parser"]["parseSpec"]["dimensionsSpec"]["dimensions"]

        for f_unit in self.mFltLegend.iterUnits():
            int_entry = {
                "name": f_unit.getName(),
                "title": f_unit.getTitle(),
                "no": f_unit.getUnitIdx(),
                "type": f_unit.getType()}
            if f_unit.getVGroup() is not None:
                int_entry["vgroup"] = f_unit.getVGroup().getTitle()
            if f_unit.getType() in {"long", "float"}:
                ext_dim_container.append({
                    "name": f_unit.getName(),
                    "type": f_unit.getType()})
            else:
                ext_dim_container.append(f_unit.getName())
                int_entry["variants"] = f_unit.getVariantSet().getVariants()
            self.mIntSchema["units"].append(int_entry)

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

    def getIntSchema(self):
        return self.mIntSchema

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
            elif value is None:
                continue
            out_rec[f_unit.getName()] = value
        self.mCurTime += self.sTimeStep
        self.mCurOrd += 1
        return out_rec


