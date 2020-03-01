#  Copyright (c) 2019. Partners HealthCare and other members of
#  Forome Association
#
#  Developed by Sergey Trifonov based on contributions by Joel Krier,
#  Michael Bouzinier, Shamil Sunyaev and other members of Division of
#  Genetics, Brigham and Women's Hospital
#
#  Licensed under the Apache License, Version 2.0 (the "License");
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
#
#        http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.
#

import os, sys, subprocess, json
from datetime import datetime, timedelta

from app.xl.druid_agent import DruidAgent
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

    def internalFltData(self, rec_no, pre_data):
        return {
            "time": (self.mStartTime
                + timedelta(microseconds = rec_no)).isoformat(),
            "_ord": rec_no,
            "_rand": pre_data["_rand"]}

    #===============================================
    def uploadDataset(self, dataset_name, flt_data, fdata_name,
            zygosity_names, report_fname = None, portion_mode = False):
        druid_dataset_name = self.normDataSetName(dataset_name)
        if self.mScpConfig is not None:
            base_dir = self.mScpConfig["dir"]
            filter_name = (druid_dataset_name + "__"
                + os.path.basename(fdata_name))
            cmd = [self.mScpConfig["exe"]]
            if not cmd[0]:
                print("Undefined parameter scp/exe", file = sys.stderr)
                assert False
            if self.mScpConfig.get("key"):
                cmd += ["-i", os.path.expanduser(self.mScpConfig["key"])]
            cmd.append(fdata_name)
            cmd.append(self.mScpConfig["host"] + ':' + base_dir + "/"
                + filter_name)
            print("Remote copying:", ' '.join(cmd), file = sys.stderr)
            print("Scp started at", datetime.now(), file = sys.stderr)
            subprocess.call(' '.join(cmd), shell = True)
        else:
            base_dir = os.path.dirname(fdata_name)
            filter_name = os.path.basename(fdata_name)

        dim_container = [
            {"name": "_ord", "type": "long"},
            {"name": "_rand", "type": "long"}]

        for unit_data in flt_data:
            if unit_data["kind"] == "func":
                continue
            if (unit_data["kind"] == "enum"
                    and unit_data["sub-kind"].startswith("transcript-")):
                continue
            if unit_data["kind"] == "numeric":
                dim_container.append({
                    "name": unit_data["name"],
                    "type": ("float" if unit_data["sub-kind"] == "float"
                        else "long")})
            else:
                if len(unit_data["variants"]) == 0:
                    continue
                if sum(info[1] for info in unit_data["variants"]) == 0:
                    continue
                dim_container.append(unit_data["name"])

        if zygosity_names is not None:
            for name in zygosity_names:
                dim_container.append({
                    "name": name,
                    "type": "long"})

        schema_request = {
            "type": "index",
            "spec": {
                "dataSchema": {
                    "dataSource": druid_dataset_name,
                    "parser": {
                        "type": "string",
                        "parseSpec": {
                            "format": "json",
                            "dimensionsSpec": {
                                "dimensions": dim_container,
                                "dimensionExclusions": [],
                                "spatialDimensions": []},
                            "timestampSpec": {
                                "column": "time"}}},
                    "metricsSpec": [{
                        "type": "count",
                        "name": "count"
                    }],
                    "granularitySpec": {
                        "type": "uniform",
                        "segmentGranularity": self.GRANULARITY,
                        "queryGranularity": "none",
                        "intervals": [self.INTERVAL],
                        "rollup": False}},
                "ioConfig": {
                    "type": "index",
                    "firehose": {
                        "type": "local",
                        "baseDir": base_dir,
                        "filter": filter_name},
                    "appendToExisting": portion_mode},
                "tuningConfig": {
                    "type": "index",
                    "targetPartitionSize": 5000000,
                    "maxRowsInMemory": 25000,
                    "forceExtendableShardSpecs": True}}}

        if report_fname is not None:
            with open(report_fname, "w", encoding="utf-8") as outp:
                outp.write(json.dumps(schema_request, ensure_ascii = False))
            print("Report stored:", report_fname, file = sys.stderr)

        print("Upload to Druid", dataset_name,
            "started at ", datetime.now(), file = sys.stderr)
        self.call("index", schema_request)
        return True

    def dropDataset(self, dataset_name):
        druid_dataset_name = self.normDataSetName(dataset_name)
        if not self.mNoCoord:
            self.call("coord", None, "DELETE", "/datasources/"
                + druid_dataset_name)
        self.call("index", {
            "type": "kill",
            "dataSource": druid_dataset_name,
            "interval": self.INTERVAL})

    def listDatasets(self):
        return self.call("coord", None, "GET",
            "/metadata/datasources?includeDisabled")

#===============================================
