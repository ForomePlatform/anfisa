import os, json, gzip, codecs, logging, re
from copy import deepcopy

from utils.ixbz2 import FormatterIndexBZ2
from app.config.a_config import AnfisaConfig
from app.model.job_pool import ExecutionTask
from app.filter.decision import DecisionTree
#===============================================
class SecondaryWsCreation(ExecutionTask):
    def __init__(self, dataset, ws_name,
            base_version = None, condition = None, markup_batch = None):
        ExecutionTask.__init__(self, "Secondary WS creation")
        self.mDS = dataset
        self.mWSName = ws_name
        self.mBaseVersion = base_version
        self.mCondition = condition
        self.mMarkupBatch = markup_batch
        self.mReportLines = AnfisaConfig.configOption("report.lines")

    sID_Pattern = re.compile('^\\S+$', re.U)
    @classmethod
    def correctWSName(cls, name):
        if not cls.sID_Pattern.match(name):
            return False
        return name[0].isalpha and not name.lower().startswith("xl_")

    def execIt(self):
        if not self.correctWSName(self.mWSName):
            self.setStatus("Incorrect workspace name")
            return None
        self.setStatus("Prepare creation")
        logging.info("Prepare workspace creation: %s" % self.mWSName)
        if (self.mBaseVersion is not None):
            tree = DecisionTree.parse(self.mDS.getCondEnv(),
                self.mDS.getMongoDS().getVersionTree(self.mBaseVersion))
            rec_no_seq = tree.collectRecSeq(self.mDS)
        else:
            rec_count = self.mDS.evalTotalCount(self.mCondition)
            if (rec_count < 1 or
                    rec_count >= AnfisaConfig.configOption("max.ws.size")):
                self.setStatus("Size is incorrect: %d" % rec_count)
                return None
            rec_no_seq = self.mDS.evalRecSeq(self.mCondition, rec_count)

        rec_no_seq = sorted(rec_no_seq)
        rec_no_set = set(rec_no_seq)
        ws_dir = self.mDS.getDataVault().getDir() + "/" + self.mWSName
        if os.path.exists(ws_dir):
            self.setStatus("Dataset already exists")
            return None

        fdata_seq = []
        with self.mDS._openFData() as inp:
            for rec_no, line in enumerate(inp):
                if rec_no in rec_no_set:
                    fdata_seq.append(json.loads(line.rstrip()))
        assert len(fdata_seq) == len(rec_no_seq)

        view_schema = deepcopy(self.mDS.getViewSchema())
        flt_schema  = deepcopy(self.mDS.getFltSchema())
        if self.mMarkupBatch is not None:
            self.setStatus("Markup evaluation")
            for rec_no, fdata in zip(rec_no_seq, fdata_seq):
                self.mMarkupBatch.feed(rec_no, fdata)
            self.mMarkupBatch.finishUp(view_schema, flt_schema)
            for rec_no, fdata in zip(rec_no_seq, fdata_seq):
                self.mMarkupBatch.transformFData(rec_no, fdata)

        os.mkdir(ws_dir)
        logging.info("Fill workspace %s datafiles..." % self.mWSName)
        with FormatterIndexBZ2(ws_dir + "/vdata.ixbz2") as vdata_out:
            for out_rec_no, rec_no in enumerate(rec_no_seq):
                if out_rec_no > 0 and (out_rec_no % self.mReportLines) == 0:
                    self.setStatus("Prepare records: %d/%d" %
                        (out_rec_no, len(rec_no_seq)))
                rec_data = self.mDS.getRecordData(rec_no)
                if self.mMarkupBatch is not None:
                    self.mMarkupBatch.transformRecData(rec_no, rec_data)
                vdata_out.putLine(json.dumps(rec_data, ensure_ascii = False))

        self.setStatus("Prepare fdata")
        with gzip.open(ws_dir + "/fdata.json.gz", 'wb') as fdata_out:
            for fdata in fdata_seq:
                print >> fdata_out, json.dumps(fdata, ensure_ascii = False)

        self.setStatus("Prepare pdata")
        with gzip.open(ws_dir + "/pdata.json.gz", 'wb') as fdata_out:
            with self.mDS._openPData() as inp:
                for rec_no, line in enumerate(inp):
                    if rec_no in rec_no_set:
                        print >> fdata_out, line.rstrip()

        self.setStatus("Finishing...")
        logging.info("Finishing up workspace %s" % self.mWSName)

        ds_info = {
            "name": self.mWSName,
            "kind": "ws",
            "view_schema": view_schema,
            "flt_schema": flt_schema,
            "total": len(rec_no_seq),
            "mongo": self.mWSName,
            "family": (self.mDS.getFamilyInfo().dump()
                if self.mDS.getFamilyInfo() is not None else None),
            "meta": self.mDS.getDataInfo().get("meta")}

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
