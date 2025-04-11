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
class DTreeTracerTask(ExecutionTask):
    def __init__(self, ds_h, dtree_h, rq_id, use_negative=False):
        ExecutionTask.__init__(self, "Preparing...")
        self.mDS = ds_h
        self.mDTreeH = dtree_h
        self.mRqId = rq_id
        self.mUseNegative = use_negative

    def getTaskType(self):
        return "dtree-trace-report"

    def execIt(self):
        if self.mDS.getDSKind() == "ws":
            ret = self._collectInfo_WS()
        else:
            ret = self._collectInfo_XL()
        self.setStatus("Done")
        return ret

    #===============================================
    def onProgressChange(self, progress, mode):
        self.setStatus("Scanning variants progress: %d%s" %
            (min(progress, 100), '%'))

    #===============================================
    def _collectInfo_XL(self):
        ret = {}
        if self.mDTreeH.getName():
            ret["dtree-name"] = self.mDTreeH.getName()
        tab_counts, tab_rec_no = self._runDTree_XL(
            total_limit=AnfisaConfig.configOption("ws.max.count"))
        all_rec_no = set()
        for seq_rec_no in tab_rec_no.values():
            all_rec_no |= set(seq_rec_no)
        ret["status"] = "OK" if -1 not in all_rec_no else "SHORTENED"
        if -1 in all_rec_no:
            all_rec_no.remove(-1)
        rec_dict = dict()
        for rec_no, p_data in self.mDS.getRecStorage().iterPData(
                all_rec_no, self):
            rec_dict[rec_no] = {
                "label": p_data["_label"],
                "color": p_data["_color"]}

        self.setStatus("Finishing")

        steps = []
        code_lines = self.mDTreeH.getCode().split('\n')
        cur_code = []

        for point_h in self.mDTreeH.iterPoints():
            cur_code.append(point_h.getCodeFrag(code_lines))
            if point_h.getPointKind() != "Return":
                continue
            step_descr = {
                "point-no": point_h.getPointNo(),
                "counts": tab_counts[point_h.getPointNo()],
                "status": "Approved" if point_h.getDecision() else "Rejected",
                "code": '\n'.join(cur_code)
            }
            seq_rec_no = tab_rec_no.get(point_h.getPointNo())
            if seq_rec_no is not None:
                if len(seq_rec_no) == 0:
                    step_descr["variants"] = []
                elif seq_rec_no[0] == -1:
                    step_descr["variants"] = None
                else:
                    step_descr["variants"] = [rec_dict[rec_no]
                        for rec_no in sorted(seq_rec_no)]
            steps.append(step_descr)
        ret["steps"] = steps
        self.setStatus("Finished")
        return ret

    #===============================================
    def _runDTree_XL(self, total_limit=None):
        tab_counts = dict()
        tab_rec_no = dict()
        total_rec_count = 0

        for point_h in self.mDTreeH.iterPoints():
            self.setStatus("Decision evaluation progress: " +
                f"{point_h.getPointNo() + 1} of {len(self.mDTreeH)}")
            if (point_h.getPointKind() != "Return" or
                    not point_h.isActive()):
                continue
            p_count = self.mDS.getEvalSpace().evalTotalCounts(
                point_h.actualCondition())
            tab_counts[point_h.getPointNo()] = p_count
            if not self.mUseNegative and not point_h.getDecision():
                continue
            if p_count[0] == 0:
                tab_rec_no[point_h.getPointNo()] = []
                continue
            total_rec_count += p_count[0]
            if (total_limit is not None and total_rec_count > total_limit):
                tab_rec_no[point_h.getPointNo()] = [-1]
                continue
            tab_rec_no[point_h.getPointNo()] = (self.mDS.getEvalSpace().
                evalRecSeq(point_h.actualCondition(), p_count[0]))
        return tab_counts, tab_rec_no

    #===============================================
    def _collectInfo_WS(self):
        ret = {}
        self.setStatus("Preparing")
        if self.mDTreeH.getName():
            ret["dtree-name"] = self.mDTreeH.getName()
        ret["status"] = "OK"

        steps = []
        code_lines = self.mDTreeH.getCode().split('\n')
        cur_code = []

        for point_h in self.mDTreeH.iterPoints():
            cur_code.append(point_h.getCodeFrag(code_lines))
            self.setStatus("Decision evaluation progress: " +
                f"{point_h.getPointNo() + 1} of {len(self.mDTreeH)}")
            if point_h.getPointKind() != "Return":
                continue
            point_h.actualCondition()

            step_descr = {
                "point-no": point_h.getPointNo(),
                "count": point_h.actualCondition().getCounts(),
                "status": "Approved" if point_h.getDecision() else "Rejected",
                "code": '\n'.join(cur_code)
            }

            if self.mUseNegative or point_h.getDecision():
                step_descr["variants"] = list(
                    point_h.actualCondition().iterSelectionDescr())
            steps.append(step_descr)
        ret["steps"] = steps
        self.setStatus("Finished")
        return ret
