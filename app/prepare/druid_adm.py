import os, sys, subprocess
from datetime import datetime, timedelta

from app.model.druid_agent import DruidAgent
#===============================================
class DruidAdmin(DruidAgent):
    TIME_START = "2015-01-01"

    def __init__(self, config):
        DruidAgent.__init__(self, config)
        self.mScpConfig = None
        if "druid" in config:
            self.mScpConfig = config["druid"].get("scp")
        self.mStartTime = self.str2dt(self.TIME_START)

    @staticmethod
    def str2dt(text):
       year, month, day = map(int, text.split('-'))
       return datetime(year = year, month = month, day = day)

    def addTimeToRec(self, rec_data, rec_no):
        rec_data["time"] = (self.mStartTime +
            timedelta(seconds = rec_no)).isoformat()

    #===============================================
    def uploadDataset(self, dataset_name, flt_data, fdata_name):
        filter_name = os.path.basename(fdata_name)
        if self.mScpConfig is not None:
            base_dir = self.mScpConfig["dir"]
            cmd = [self.mScpConfig["exe"]]
            if self.mScpConfig.get("key"):
                cmd += ["-i", os.path.expanduser(self.mScpConfig["key"])]
            cmd.append(fdata_name)
            cmd.append(self.mScpConfig["host"] + ':' + base_dir)
            print >> sys.stderr, "Remote copying:", ' '.join(cmd)
            subprocess.call(' '.join(cmd), shell = True)
        else:
            base_dir = os.path.dirname(fdata_name)

        dim_container = [
            {"name": "_ord", "type": "long"},
            {"name": "_rand", "type": "long"},
            {"name": "_key", "type": "string", "createBitmapIndex": False},
            {"name": "_color", "type": "string", "createBitmapIndex": False},
            {"name": "_label", "type": "string", "createBitmapIndex": False}]

        for unit_data in flt_data:
            if unit_data["kind"] in {"long", "float"}:
                dim_container.append({
                    "name": unit_data["name"],
                    "type": unit_data["kind"]})
            else:
                if len(unit_data["variants"]) == 0:
                    continue
                dim_container.append(unit_data["name"])

        schema_request = {
            "type" : "index",
            "spec" : {
                "dataSchema" : {
                    "dataSource" : dataset_name,
                    "parser" : {
                        "type" : "string",
                        "parseSpec" : {
                            "format" : "json",
                            "dimensionsSpec" : {
                                "dimensions" : dim_container,
                                "dimensionExclusions" : [],
                                "spatialDimensions" : []},
                            "timestampSpec": {
                                "column": "time"}}},
                    "metricsSpec" : [],
                    "granularitySpec" : {
                        "type" : "uniform",
                        "segmentGranularity" : self.GRANULARITY,
                        "queryGranularity" : "none",
                        "intervals" : [self.INTERVAL],
                        "rollup" : False}},
                "ioConfig" : {
                    "type" : "index",
                    "firehose" : {
                        "type" : "local",
                        "baseDir" : base_dir,
                        "filter" : filter_name},
                    "appendToExisting" : False},
                "tuningConfig" : {
                    "type" : "index",
                    "targetPartitionSize" : 5000000,
                    "maxRowsInMemory" : 25000,
                    "forceExtendableShardSpecs" : True}}}

        print >> sys.stderr, "Upload to Druid", dataset_name
        self.call("index", schema_request)
        return True

    def dropDataset(self, dataset_name):
        self.call("coord", None, "DELETE", "/datasources/" + dataset_name)
        self.call("index", {
            "type": "kill",
            "dataSource": dataset_name,
            "interval" : self.INTERVAL})

    def listDatasets(self):
        return self.call("coord", None, "GET",
            "/metadata/datasources?includeDisabled")

#===============================================
