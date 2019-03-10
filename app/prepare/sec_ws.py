import os, json, gzip, codecs, logging, re

from ixbz2.ixbz2 import FormatterIndexBZ2
from app.model.a_config import AnfisaConfig
from app.model.job_pool import ExecutionTask
from app.xl.decision import DecisionTree
from app.xl.xl_cond import XL_Condition
#===============================================
class SecondaryWsCreation(ExecutionTask):
    def __init__(self, dataset, ws_name,
            base_version = None, conditions = None):
        ExecutionTask.__init__(self, "Secondary WS creation")
        self.mDS = dataset
        self.mWSName = ws_name
        self.mBaseVersion = base_version
        self.mConditions = conditions
        self.mReportLines = AnfisaConfig.configOption("report.lines")

    sID_Pattern = re.compile('^[a-z][\\w\-\_]+$', re.I)

    def execIt(self):
        if not self.sID_Pattern.match(self.mWSName):
            self.setStatus("Incorrect workspace name")
            return None
        self.setStatus("Prepare creation")
        logging.info("Prepare workspace creation: %s" % self.mWSName)
        if (self.mBaseVersion is not None):
            tree = DecisionTree.parse(
                self.mDS.getMongoDS().getVersionTree(self.mBaseVersion))
            rec_no_seq = tree.collectRecSeq(self.mDS)
        else:
            context = {"cond":XL_Condition.parseSeq(
                json.loads(self.mConditions))}
            rec_count = self.mDS.evalTotalCount(context)
            assert rec_count <= AnfisaConfig.configOption("max.ws.size")
            rec_no_seq = self.mDS.evalRecSeq(context, rec_count)

        rec_no_seq = sorted(rec_no_seq)
        ws_dir = self.mDS.getDataVault().getDir() + "/" + self.mWSName
        if os.path.exists(ws_dir):
            self.setStatus("Dataset already exists")
            return None
        os.mkdir(ws_dir)

        logging.info("Fill workspace %s datafiles..." % self.mWSName)
        with FormatterIndexBZ2(ws_dir + "/vdata.ixbz2") as vdata_out:
            for out_rec_no, rec_no in enumerate(rec_no_seq):
                if out_rec_no > 0 and (out_rec_no % self.mReportLines) == 0:
                    self.setStatus("Prepare records: %d/%d" %
                        (out_rec_no, len(rec_no_seq)))
                rec_data = self.mDS.getRecordData(rec_no)
                vdata_out.putLine(json.dumps(rec_data, ensure_ascii = False))

        rec_no_set = set(rec_no_seq)
        cnt_done = 0
        with gzip.open(ws_dir + "/fdata.json.gz", 'wb') as fdata_out:
            with self.mDS._openFData() as inp:
                for rec_no, line in enumerate(inp):
                    if rec_no in rec_no_set:
                        print >> fdata_out, line.rstrip()
                        cnt_done += 1
                        if (cnt_done % self.mReportLines) == 0:
                            self.setStatus("Prepare fdata: %d/%d" %
                                (cnt_done, len(rec_no_seq)))

        cnt_done = 0
        with gzip.open(ws_dir + "/pdata.json.gz", 'wb') as fdata_out:
            with self.mDS._openPData() as inp:
                for rec_no, line in enumerate(inp):
                    if rec_no in rec_no_set:
                        print >> fdata_out, line.rstrip()
                        cnt_done += 1
                        if (cnt_done % self.mReportLines) == 0:
                            self.setStatus("Prepare fdata: %d/%d" %
                                (cnt_done, len(rec_no_seq)))

        self.setStatus("Finishing...")
        logging.info("Finishing up workspace %s" % self.mWSName)

        ds_info = {
            "name": self.mWSName,
            "kind": "ws",
            "view_schema": self.mDS.getViewSchema(),
            "flt_schema": self.mDS.getFltSchema(),
            "total": len(rec_no_seq),
            "mongo": self.mWSName}

        with codecs.open(ws_dir + "/dsinfo.json",
                "w", encoding = "utf-8") as outp:
            print >> outp, json.dumps(ds_info,
                sort_keys = True, indent = 4)

        with codecs.open(ws_dir + "/active",
                "w", encoding = "utf-8") as outp:
            print >> outp, ""

        self.mDS.getDataVault().loadNewWS(self.mWSName)

        self.setStatus("Done")
        return {"ws": self.mWSName}
