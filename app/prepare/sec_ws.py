import os, json, gzip, logging, re, shutil
from copy import deepcopy
from io import TextIOWrapper
from datetime import datetime

from utils.ixbz2 import FormatterIndexBZ2
from utils.job_pool import ExecutionTask
from app.config.a_config import AnfisaConfig
from app.filter.tree_parse import ParsedDecisionTree
from app.filter.decision import DecisionTree
from .html_report import reportDS

#===============================================
class SecondaryWsCreation(ExecutionTask):
    def __init__(self, dataset, ws_name, base_version = None,
            op_cond = None, std_name = None,
            markup_batch = None, force_mode = False):
        ExecutionTask.__init__(self, "Secondary WS creation")
        self.mDS = dataset
        self.mWSName = ws_name
        self.mBaseVersion = base_version
        self.mOpCond = op_cond
        self.mStdName = std_name
        self.mMarkupBatch = markup_batch
        self.mReportLines = AnfisaConfig.configOption("report.lines")
        self.mForceMode = force_mode

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
        if self.mBaseVersion is not None:
            tree = DecisionTree(ParsedDecisionTree(self.mDS.getCondEnv(),
                self.mDS.getMongoAgent().getTreeCodeVersion(
                self.mBaseVersion)))
            rec_no_seq, point_seq = tree.collectRecSeq(self.mDS)
            receipt = {
                "kind": "tree",
                "version": self.mBaseVersion,
                "points": point_seq}
        elif self.mStdName is not None:
            tree = DecisionTree(ParsedDecisionTree(self.mDS.getCondEnv(),
                self.mDS.getCondEnv().getStdTreeCode(self.mStdName)))
            rec_no_seq, point_seq = tree.collectRecSeq(self.mDS)
            receipt = {
                "kind": "tree",
                "std": self.mStdName,
                "points": point_seq}
        else:
            condition = self.mOpCond.getResult()
            rec_count = self.mDS.evalTotalCount(condition)
            if (rec_count < 1 or
                    rec_count >= AnfisaConfig.configOption("max.ws.size")):
                self.setStatus("Size is incorrect: %d" % rec_count)
                return None
            rec_no_seq = self.mDS.evalRecSeq(condition, rec_count)
            receipt = {
                "kind": "filter",
                "seq": self.mOpCond.getPresentation()}

        rec_no_seq = sorted(rec_no_seq)
        rec_no_set = set(rec_no_seq)
        ws_dir = self.mDS.getDataVault().getDir() + "/" + self.mWSName
        if os.path.exists(ws_dir) and self.mForceMode:
            if self.mDS.getDataVault().getWS(self.mWSName):
                self.mDS.getDataVault().unloadDS(self.mWSName, "ws")
            shutil.rmtree(ws_dir)
        if os.path.exists(ws_dir):
            self.setStatus("Dataset already exists")
            return None

        fdata_seq = []
        with self.mDS._openFData() as inp:
            fdata_inp = TextIOWrapper(inp,
                encoding = "utf-8", line_buffering = True)
            for rec_no, line in enumerate(fdata_inp):
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
        with gzip.open(ws_dir + "/fdata.json.gz", 'wb') as fdata_stream:
            fdata_out = TextIOWrapper(fdata_stream,
                encoding = "utf-8", line_buffering = True)
            for fdata in fdata_seq:
                print(json.dumps(fdata, ensure_ascii = False),
                    file = fdata_out)

        self.setStatus("Prepare pdata")
        with self.mDS._openPData() as inp, \
                gzip.open(ws_dir + "/pdata.json.gz", 'wb') as outp:
            pdata_inp = TextIOWrapper(inp,
                encoding = "utf-8", line_buffering = True)
            pdata_outp = TextIOWrapper(outp,
                encoding = "utf-8", line_buffering = True)
            for rec_no, line in enumerate(pdata_inp):
                if rec_no in rec_no_set:
                    print(line.rstrip(), file = pdata_outp)

        self.setStatus("Finishing...")
        logging.info("Finishing up workspace %s" % self.mWSName)

        date_loaded = datetime.now().isoformat()
        ds_info = {
            "name": self.mWSName,
            "kind": "ws",
            "view_schema": view_schema,
            "flt_schema": flt_schema,
            "total": len(rec_no_seq),
            "mongo": self.mWSName,
            "modes": ["secondary"],
            "family": (self.mDS.getFamilyInfo().dump()
                if self.mDS.getFamilyInfo() is not None else None),
            "meta": self.mDS.getDataInfo().get("meta"),
            "date_loaded": date_loaded}

        with open(ws_dir + "/dsinfo.json", "w", encoding = "utf-8") as outp:
            print(json.dumps(ds_info, sort_keys = True, indent = 4),
                file = outp)

        mongo_agent = self.mDS.getApp().getMongoConnector().getWSAgent(
            self.mWSName)
        mongo_agent.checkCreationDate(date_loaded)
        date_created = mongo_agent.getCreationDate()
        if date_created == date_loaded:
            date_loaded = None

        os.mkdir(ws_dir + "/doc")
        with open(ws_dir + "/doc/info.html", "w", encoding = "utf-8") as outp:
            reportDS(outp, {
                "name": self.mWSName,
                "kind": "WS",
                "count": len(rec_no_seq),
                "date-created": date_created,
                "date-reloaded": date_loaded,
                "base-ds": self.mDS.getName(),
                "base-count": self.mDS.getTotal(),
                "date-base": self.mDS.getDataInfo().get("date_loaded"),
                "receipt": receipt})

        with open(ws_dir + "/active", "w", encoding = "utf-8") as outp:
            print("", file = outp)

        self.mDS.getDataVault().loadDS(self.mWSName, "ws")

        self.setStatus("Done")
        return {"ws": self.mWSName}
