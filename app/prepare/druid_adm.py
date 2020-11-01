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

import os, sys, subprocess, json, logging
from datetime import datetime, timedelta
from time import sleep

from app.xl.druid_agent import DruidAgent
#===============================================
class DruidAdmin(DruidAgent):
    TIME_START = "2015-01-01"
    LOAD_GRANULATITY = "minute"

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
            zygosity_names, report_fname = None,
            no_druid_push = False, portion_mode = False, rep_out = None):
        druid_dataset_name = self.normDataSetName(dataset_name)
        if self.mScpConfig is not None:
            base_dir = self.mScpConfig["dir"]
            filter_name = (druid_dataset_name + "__"
                + os.path.basename(fdata_name))
            cmd_copy = [self.mScpConfig["exe"]]
            if not cmd_copy[0]:
                print("Undefined parameter scp/exe", file = sys.stderr)
                assert False
            if self.mScpConfig.get("key"):
                cmd_copy += ["-i", os.path.expanduser(self.mScpConfig["key"])]
            cmd_copy.append(fdata_name)
            cmd_copy.append(self.mScpConfig["host"] + ':' + base_dir + "/"
                + filter_name)
            cmd_copy = ' '.join(cmd_copy)
            print("Remote copying:", cmd_copy, file = sys.stderr)
            print("Scp started at", datetime.now(), file = sys.stderr)
            subprocess.call(cmd_copy, shell = True)
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
            "type": "index_parallel",
            "spec": {
                "dataSchema": {
                    "dataSource": druid_dataset_name,
                    "timestampSpec": {
                        "column": "time",
                        "format": "auto"
                    },
                    "dimensionsSpec": {
                        "dimensions": dim_container},
                    "metricsSpec": [{
                        "type": "count",
                        "name": "count"
                    }],
                    "granularitySpec": {
                        "segmentGranularity":  self.LOAD_GRANULATITY,
                        "queryGranularity": "none",
                        "intervals": None}},
                "ioConfig": {
                    "type": "index_parallel",
                    "inputSource": {
                        "type": "local",
                        "baseDir": base_dir,
                        "filter": filter_name},
                    "inputFormat": {
                        "type": "json"}},
                "tuningConfig": {
                    "type": "index_parallel"}}}

        if report_fname is not None:
            with open(report_fname, "w", encoding="utf-8") as outp:
                outp.write(json.dumps(schema_request,
                    sort_keys = True, indent = 4, ensure_ascii = False))
            print("Report stored:", report_fname, file = sys.stderr)
            if rep_out:
                print("Report stored:", report_fname, file = rep_out)

        if no_druid_push:
            print("Skipped push to Druid")
            return True

        dt_start = datetime.now()
        print("Upload to Druid", dataset_name,
            "started at ", dt_start, file = sys.stderr)
        resp_h = self.call("index", schema_request)
        task_id = resp_h["task"]
        while True:
            resp_h = self.call("index", [task_id],
                add_path = "Status", calm_mode = True)
            if resp_h[task_id]["status"] != "RUNNING":
                break
            sys.stderr.write('.')
            sleep(1)
            continue

        dt_end = datetime.now()
        print("\nUpload to Druid", dataset_name,
            "finished at ", dt_end, "for", dt_end - dt_start,
            file = sys.stderr)
        print("Upload status:", resp_h[task_id]["status"], file = sys.stderr)
        if (resp_h[task_id].get("status") != "SUCCESS"
                or resp_h[task_id].get("errorMsg")):
            print("Error on upload:",
                json.dumps(resp_h, indent = 4), file = sys.stderr)
            if rep_out:
                print("Error on upload:",
                    json.dumps(resp_h, indent = 4), file = rep_out)

            return False
        return True

    def dropDataset(self, dataset_name):
        if dataset_name.startswith("xl_FAVOR"):
            validated = input("\nAre yout sure to drop dataset "
                + dataset_name + "? (.../Yes)")
            assert validated == "Yes", "Drop not accepted"

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

    def mineEnumVariants(self, dataset_name, unit_name):
        logging.info("Mine enum unit: " + unit_name)
        var_size = 100
        while True:
            query = {
                "queryType": "topN",
                "dataSource": self.normDataSetName(dataset_name),
                "dimension": unit_name,
                "threshold": var_size,
                "metric": "count",
                "granularity": self.GRANULARITY,
                "aggregations": [{
                    "type": "count", "name": "count",
                    "fieldName": unit_name}],
                "intervals": [self.INTERVAL]}
            rq = self.call("query", query)
            if len(rq) != 1:
                logging.error(
                    "Got problem with xl_unit %s: %d expect_size=%d"
                    % (unit_name, len(rq), var_size))
                assert False
            if len(rq[0]["result"]) >= var_size:
                var_size *= 10
                continue
            ret = [[str(rec[unit_name]), rec["count"]]
                for rec in rq[0]["result"]]
            return sorted(ret)

    def mineTotal(self, dataset_name):
        query = {
            "queryType": "timeseries",
            "dataSource": self.normDataSetName(dataset_name),
            "granularity": self.GRANULARITY,
            "descending": "true",
            "aggregations": [
                {"type": "count", "name": "count",
                    "fieldName": "_ord"}],
            "filter": None,
            "intervals": [self.INTERVAL]}
        ret = self.call("query", query)
        assert len(ret) == 1
        return int(ret[0]["result"]["count"])


#===============================================
