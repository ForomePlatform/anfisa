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

from datetime import datetime, timedelta

from forome_tools.job_pool import ExecutionTask
#===============================================
class VariantTracerTask(ExecutionTask):
    def __init__(self, ds_h, rec_no, dtree_h, rq_id):
        ExecutionTask.__init__(self, "Preparing...")
        self.mDS = ds_h
        self.mRecNo = rec_no
        self.mDTreeH = dtree_h
        self.mRqId = rq_id

    def getTaskType(self):
        return "rec-list"

    def onProgressChange(self, progress, mode):
        self.setStatus("Preparation progress: %d%s" %
            (min(progress, 100), '%'))

    def collectInfo_XL(self):
        assert False, "Not properly implemented yet"
        ret = {}
        if self.mDTreeH.getName():
            ret["dtree-name"] = self.mDTreeH.getName()
        self.setStatus("Preparation progress: 0%")
        rec_dict = self.mDS.getRecStorage().collectPReports(
            {self.mRecNo}, self)
        ret["variant"] = rec_dict[self.mRecNo]

        self.setStatus("Tree evaluation")
        point_counts = self.mDS.prepareDTreePointCounts(
            self.mDTreeH, rq_id=None,
            time_end=datetime.now() + timedelta(minutes=60))
        self.setStatus("Finishing")

        steps = []
        code_lines = self.mDTreeH.getCode().split('\n')
        cur_code = []
        final_status = None

        for point_h in self.mDTreeH.iterPoints():
            cur_code.append(point_h.getCodeFrag(code_lines))
            if point_h.getPointKind() == "If":
                continue
            status = "N/A"
            if point_h.getPointKind() == "Terminal":
                count = point_counts[point_h.getPointNo()]
                if count is not None and count > 0:
                    status = ["Rejected", "Approved"][
                        point_h.getDecision() is True]
                    assert final_status is None
                    final_status = status
                else:
                    status = ["N/A", "Passed"][final_status is None]
            steps.append({"code": '\n'.join(cur_code), "status": status,
                "no": point_h.getPointNo() - 1})
            cur_code = []

        ret["steps"] = steps
        #assert final_status is not None
        ret["status"] = final_status
        ret["counts"] = point_counts
        return ret

    def collectInfo_WS(self):
        assert False, "Not implemented yet"

    def execIt(self):
        if self.mDS.getDSKind() == "ws":
            ret = self.collectInfo_WS()
        else:
            ret = self.collectInfo_XL()
        self.setStatus("Done")
        return ret
