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

import json
from io import TextIOWrapper
from xml.sax.saxutils import escape

from utils.job_pool import ExecutionTask
from app.config.a_config import AnfisaConfig
#===============================================
class RecListTask(ExecutionTask):

    sViewCountFull = AnfisaConfig.configOption("xl.view.count.full")
    sViewCountSamples = AnfisaConfig.configOption("xl.view.count.samples")
    sViewMinSamples = AnfisaConfig.configOption("xl.view.min.samples")

    def __init__(self, dataset, condition, rest_backup_records = False):
        ExecutionTask.__init__(self, "Prepare variants...")
        self.mDS = dataset
        self.mCondition = condition
        self.mRestBackRec = rest_backup_records

    def execIt(self):
        if self.mDS.getDSKind() == "ws":
            q_samples, q_full = False, True
            rec_no_seq = self.mDS.getEvalSpace().evalRecSeq(self.mCondition)
        else:
            rec_no_seq = self.mDS.getEvalSpace().evalSampleList(
                self.mCondition, self.sViewCountFull + 5)
            if len(rec_no_seq) > self.sViewCountFull:
                rec_no_seq = rec_no_seq[:self.sViewCountSamples]
                q_samples, q_full = True, False
            elif len(rec_no_seq) <= self.sViewMinSamples:
                q_samples, q_full = False, True
            else:
                q_samples, q_full = True, True

        total = self.mDS.getTotal()
        step_cnt = total // 100
        cur_progress = 0
        next_cnt = step_cnt
        self.setStatus("Preparation progress: 0%")
        rec_no_dict = {rec_no: None for rec_no in rec_no_seq}
        with self.mDS._openPData() as inp:
            pdata_inp = TextIOWrapper(inp,
                encoding = "utf-8", line_buffering = True)
            for rec_no, line in enumerate(pdata_inp):
                if rec_no > next_cnt:
                    next_cnt += step_cnt
                    cur_progress += 1
                    self.setStatus("Preparation progress: %d%s" %
                        (min(cur_progress, 100), '%'))
                if rec_no not in rec_no_dict:
                    continue
                pre_data = json.loads(line.strip())
                rec_no_dict[rec_no] = {
                    "no": rec_no,
                    "lb": escape(pre_data.get("_label")),
                    "cl": AnfisaConfig.normalizeColorCode(
                        pre_data.get("_color"))}
        self.setStatus("Finishing")
        ret = dict()
        if q_samples:
            ret["samples"] = [rec_no_dict[rec_no]
                for rec_no in rec_no_seq[:self.sViewCountSamples]]
            if self.mRestBackRec:
                ret["samples"] = self.mDS._REST_BackupRecords(ret["samples"])
        if q_full:
            ret["records"] = [rec_no_dict[rec_no]
                for rec_no in sorted(rec_no_seq)]
            if self.mRestBackRec:
                ret["records"] = self.mDS._REST_BackupRecords(ret["records"])
        self.setStatus("Done")
        return ret
