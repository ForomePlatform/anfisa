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
#===============================================
class VariantTracerTask(ExecutionTask):
    def __init__(self, ds_h, dtree_h, variant, rq_id, transcript = None):
        ExecutionTask.__init__(self, "Preparing...")
        self.mDS = ds_h
        self.mDTreeH = dtree_h
        self.mVariant = variant
        self.mTranscript = transcript
        self.mRqId = rq_id

    def getTaskType(self):
        return "dtree-variant-trace"

    def execIt(self):
        ret = {"variant" : self.mVariant}
        if self.mDTreeH.getName():
            ret["dtree-name"] = self.mDTreeH.getName()
        if self.mTranscript is not None:
            ret["transcript-id"] = self.mTranscript
            if self.mDS.getDSKind() != "ws":
                ret["status"] = "Failed"
                ret["error"] = "Transcript option is not provided"
                return ret
        the_rec_no = None
        for rec_no, p_data in self.mDS.getRecStorage().iterPData(
                notifier = self):
            label = p_data["_label"]
            if ']' in label:
                _, _, variant = label.partition(']')
            else:
                variant = label
            if (variant.strip() + " ").startswith(self.mVariant + " "):
                the_rec_no = rec_no
                break
        if the_rec_no is None:
            ret["status"] = "Failed"
            ret["error"] = "Variant not found in dataset"
            return ret

        self.setStatus("Decision evaluation")
        if self.mDS.getDSKind() == "ws":
            return self._collectInfo_WS(the_rec_no, ret)
        else:
            return self._collectInfo_XL(the_rec_no, ret)

    #===============================================
    def _collectInfo_XL(self, rec_no, descr):
        trace_condition = self.mDS.getEvalSpace().makeRecNoCond(rec_no)
        for point_h in self.mDTreeH.iterPoints():
            self.setStatus("Decision evaluation progress: " +
                f"{point_h.getPointNo() + 1} of {len(self.mDTreeH)}")
            if (point_h.getPointKind() != "Return" or
                    not point_h.isActive()):
                continue
            point_cond = trace_condition.addAnd(point_h.actualCondition())
            p_counts = self.mDS.getEvalSpace().evalTotalCounts(point_cond)
            assert p_counts[0] < 2
            if p_counts[0] == 1:
                descr["trace"] = {
                    "point-no": point_h.getPointNo(),
                    "status": "Approved" if point_h.getDecision()
                        else "Rejected"}
                self.setStatus("Finished")
                return descr
        descr["error"] = "Variant lost?"
        self.setStatus("Finished")
        return descr

    #===============================================
    def onProgressChange(self, progress, mode):
        self.setStatus("Scanning variants progress: %d%s" %
            (min(progress, 100), '%'))

    #===============================================
    def _collectInfo_WS(self, rec_no, descr):
        trace_condition = self.mDS.getEvalSpace().makeRecNoCond(
            rec_no, self.mTranscript)
        if trace_condition is None:
            descr["error"] = "Trancript not found"
            return descr
        traces = []
        for point_h in self.mDTreeH.iterPoints():
            self.setStatus("Decision evaluation progress: " +
                f"{point_h.getPointNo() + 1} of {len(self.mDTreeH)}")
            if (point_h.getPointKind() != "Return" or
                    not point_h.isActive()):
                continue
            point_cond = trace_condition.addAnd(point_h.actualCondition())
            p_counts = point_cond.getCounts()
            if p_counts[0] > 0:
                if self.mTranscript is not None:
                    descr["trace"] = {
                        "point-no": point_h.getPointNo(),
                        "status": "Approved" if point_h.getDecision()
                            else "Rejected"}
                    self.setStatus("Finished")
                    return descr
                seq_descr = list(point_cond.iterSelectionDescr())
                assert len(seq_descr) == 1
                traces.append({
                    "point-no": point_h.getPointNo(),
                    "status": "Approved" if point_h.getDecision()
                        else "Rejected",
                    "transcripts": seq_descr[0]["transcripts"]})
        if len(traces) == 0:
            descr["error"] = "Lost transcripts?"
        else:
            descr["traces"] = traces
        self.setStatus("Finished")
        return descr
