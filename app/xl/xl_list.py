import json
from io import TextIOWrapper
from xml.sax.saxutils import escape

from utils.job_pool import ExecutionTask
from app.config.a_config import AnfisaConfig
#===============================================
class XlListTask(ExecutionTask):

    sViewCountFull = AnfisaConfig.configOption("xl.view.count.full")
    sViewCountSamples = AnfisaConfig.configOption("xl.view.count.samples")
    sViewMinSamples = AnfisaConfig.configOption("xl.view.min.samples")

    def __init__(self, dataset, condition):
        ExecutionTask.__init__(self, "Prepare variants...")
        self.mDS = dataset
        self.mCondition = condition

    def execIt(self):
        rec_no_seq = self.mDS.evalSampleList(
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
                rec_no_dict[rec_no] = [rec_no,
                    escape(pre_data.get("_label")),
                    AnfisaConfig.normalizeColorCode(pre_data.get("_color"))]
        self.setStatus("Finishing")
        ret = dict()
        if q_samples:
            ret["samples"] = [rec_no_dict[rec_no]
                for rec_no in rec_no_seq[:self.sViewCountSamples]]
        if q_full:
            ret["records"] = [rec_no_dict[rec_no]
                for rec_no in sorted(rec_no_seq)]
        self.setStatus("Done")
        return ret
