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

from forome_tools.job_pool import ExecutionTask
from app.config.a_config import AnfisaConfig
#===============================================
class RecListTask(ExecutionTask):
    sViewCountFull = AnfisaConfig.configOption("xl.view.count.full")
    sViewCountSamples = AnfisaConfig.configOption("xl.view.count.samples")
    sViewMinSamples = AnfisaConfig.configOption("xl.view.min.samples")

    def __init__(self, ds_h, condition):
        ExecutionTask.__init__(self, "Prepare variants...")
        self.mDS = ds_h
        self.mCondition = condition
        self.mResSamples = None
        self.mResFull = None

    def getTaskType(self):
        return "rec-list"

    def _detectModes(self, rec_count):
        if rec_count > self.sViewCountFull:
            self.mResSamples = []
        elif rec_count <= self.sViewMinSamples:
            self.mResFull = []
        else:
            self.mResSamples = []
            self.mResFull = []

    def onProgressChange(self, progress, mode):
        self.setStatus("Preparation progress: %d%s" %
            (min(progress, 100), '%'))

    def collectRecords_XL(self):
        rec_no_seq = self.mDS.getEvalSpace().evalSampleList(
            self.mCondition, self.sViewCountFull + 5)
        self._detectModes(len(rec_no_seq))
        rec_no_seq = rec_no_seq[:self.sViewCountFull]

        self.setStatus("Preparation progress: 0%")
        rec_dict = self.mDS.getRecStorage().collectPReports(
            set(rec_no_seq), self)
        self.setStatus("Finishing")
        if self.mResSamples is not None:
            self.mResSamples = [rec_dict[rec_no]
                for rec_no in rec_no_seq[:self.sViewCountSamples]]
        if self.mResFull is not None:
            self.mResFull = [rec_dict[rec_no]
                for rec_no in sorted(rec_no_seq)]

    def collectRecords_WS(self):
        req_rep_seq = []
        rand_sheet = []
        for rec_no, rec_it_map in self.mCondition.iterSelection():
            req_rep_seq.append(self.mDS.reportRecord(rec_no, rec_it_map))
            rand_sheet.append((self.mDS.getRecRand(rec_no), len(rand_sheet)))
        self._detectModes(len(req_rep_seq))
        self.mResFull = req_rep_seq
        if self.mResSamples is not None:
            self.mResSamples = [req_rep_seq[idx]
                for _, idx in sorted(rand_sheet)[:self.sViewCountSamples]]

    def execIt(self):
        if self.mDS.getDSKind() == "ws":
            self.collectRecords_WS()
        else:
            self.collectRecords_XL()
        ret = dict()
        if self.mResSamples:
            ret["samples"] = self.mResSamples
        if self.mResFull:
            ret["records"] = self.mResFull
        self.mDS.visitCondition(self.mCondition, ret)
        self.setStatus("Done")
        return ret
