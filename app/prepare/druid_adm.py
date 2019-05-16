import os, sys, subprocess, codecs, json
from datetime import datetime, timedelta

from app.filter.druid_agent import DruidAgent
#===============================================
class DruidAdmin(DruidAgent):
    TIME_START = "2015-01-01"

    def __init__(self, config, no_coord = False):
        DruidAgent.__init__(self, config)
        self.mScpConfig = None
        self.mNoCoord = no_coord
        if "druid" in config:
            self.mScpConfig = config["druid"].get("scp")
        self.mStartTime = self.str2dt(self.TIME_START)

    @staticmethod
    def str2dt(text):
       year, month, day = map(int, text.split('-'))
       return datetime(year = year, month = month, day = day)

    def addFieldsToRec(self, rec_data, pre_data, rec_no):
        rec_data["time"] = (self.mStartTime +
            timedelta(seconds = rec_no)).isoformat()
        rec_data["_ord"]  = rec_no
        rec_data["_rand"] = pre_data["_rand"]

    #===============================================
    def uploadDataset(self, dataset_name, flt_data, fdata_name,
            report_name = None):
        druid_dataset_name = self.normDataSetName(dataset_name)
        if self.mScpConfig is not None:
            base_dir = self.mScpConfig["dir"]
            filter_name = (druid_dataset_name + "__" +
                os.path.basename(fdata_name))
            cmd = [self.mScpConfig["exe"]]
            if not cmd[0]:
                print >> sys.stderr, "Undefined parameter scp/exe"
                assert False
            if self.mScpConfig.get("key"):
                cmd += ["-i", os.path.expanduser(self.mScpConfig["key"])]
            cmd.append(fdata_name)
            cmd.append(self.mScpConfig["host"] + ':' + base_dir + "/" +
                filter_name)
            print >> sys.stderr, "Remote copying:", ' '.join(cmd)
            print >> sys.stderr, "Scp started at", datetime.now()
            subprocess.call(' '.join(cmd), shell = True)
        else:
            base_dir = os.path.dirname(fdata_name)
            filter_name = os.path.basename(fdata_name)

        dim_container = [
            {"name": "_ord", "type": "long"},
            {"name": "_rand", "type": "long"}]

        for unit_data in flt_data:
            if unit_data["kind"] in {"long", "float"}:
                dim_container.append({
                    "name": unit_data["name"],
                    "type": unit_data["kind"]})
            elif unit_data["kind"] == "zygosity":
                if unit_data["size"] < 2:
                    continue
                for idx in range(unit_data["size"]):
                    dim_container.append({
                        "name": "%s_%d" % (unit_data["name"], idx),
                        "type": "long"})
            else:
                if len(unit_data["variants"]) == 0:
                    continue
                if sum([info[1] for info in unit_data["variants"]]) == 0:
                    continue
                dim_container.append(unit_data["name"])

        schema_request = {
            "type" : "index",
            "spec" : {
                "dataSchema" : {
                    "dataSource" : druid_dataset_name,
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

        if report_name is not None:
            with codecs.open(report_name, "w", encoding="utf-8") as outp:
                outp.write(json.dumps(schema_request, ensure_ascii = False))
            print >> sys.stderr, "Report stored:", report_name

        print >> sys.stderr, "Upload to Druid", dataset_name, \
            "started at ", datetime.now()
        self.call("index", schema_request)
        return True

    def dropDataset(self, dataset_name):
        druid_dataset_name = self.normDataSetName(dataset_name)
        if not self.mNoCoord:
            self.call("coord", None, "DELETE", "/datasources/" +
                druid_dataset_name)
        self.call("index", {
            "type": "kill",
            "dataSource": druid_dataset_name,
            "interval" : self.INTERVAL})

    def listDatasets(self):
        return self.call("coord", None, "GET",
            "/metadata/datasources?includeDisabled")

#===============================================
