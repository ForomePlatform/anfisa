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

import os, json, logging, re, shutil
from copy import deepcopy
from datetime import datetime

from forome_tools.job_pool import ExecutionTask
from app.model.ds_disk import DataDiskStorageWriter
from app.config.a_config import AnfisaConfig
from app.config.flt_schema import defineFilterSchema
from app.config.variables import anfisaVariables
from app.prepare.prep_filters import FilterPrepareSetH
from .html_report import reportDS

_make_compiler_happy = defineFilterSchema
#===============================================
class SecondaryWsCreation(ExecutionTask):
    def __init__(self, ds_h, ws_name, eval_h, force_mode = False):
        ExecutionTask.__init__(self, "Secondary WS creation")
        self.mDS = ds_h
        self.mWSName = ws_name
        self.mEval = eval_h
        self.mReportLines = AnfisaConfig.configOption("report.lines")
        self.mForceMode = force_mode

    def getTaskType(self):
        return "sec-ws"

    sDSNamePattern = re.compile(r'^\S+$', re.U)

    @classmethod
    def correctWSName(cls, name):
        if len(name) > AnfisaConfig.configOption("ds.name.max.length"):
            return False
        if not cls.sDSNamePattern.match(name):
            return False
        return name[0].isalpha and not name.lower().startswith("xl_")

    def onProgressChange(self, progress, mode):
        if mode == "fdata":
            self.setStatus("Filtering progress %d%s"
                % (min(progress, 100), '%'))
        else:
            self.setStatus("Extraction progress %d%s"
                % (min(progress, 100), '%'))

    def execIt(self):
        if not self.correctWSName(self.mWSName):
            self.setStatus("Incorrect derived dataset name")
            return None
        self.setStatus("Preparing to create derived dataset")
        logging.info("Prepare dataset derivation: %s" % self.mWSName)
        receipt = {
            "kind": self.mEval.getSolKind(),
            "base": self.mDS.getName(),
            "root": self.mDS.getRootDSName()
        }

        if self.mEval.getSolKind() == "filter":
            if self.mEval.getName():
                receipt["filter-name"] = self.mEval.getName()
            condition = self.mEval.getCondition()
            rec_count = self.mDS.getEvalSpace().evalTotalCounts(condition)[0]
            if (rec_count < 1
                    or rec_count >= AnfisaConfig.configOption("max.ws.size")):
                self.setStatus("Size is incorrect: %d" % rec_count)
                return None
            rec_no_seq = self.mDS.getEvalSpace().evalRecSeq(
                condition, rec_count)
            receipt["f-presentation"] = self.mEval.getPresentation()
            receipt["conditions"] = self.mEval.getCondDataSeq()
        else:
            if self.mEval.getName():
                receipt["dtree-name"] = self.mEval.getName()
            rec_no_seq, point_seq = self.mEval.collectRecSeq()
            receipt["p-presentation"] = point_seq
            receipt["dtree-code"] = self.mEval.getCode()

        panels_cfg = AnfisaConfig.configOption("panels.setup")
        panels_supply = dict()
        for ptype in sorted(panels_cfg.keys()):
            pnames = self.mDS.getEvalSpace().getUsedDimValues(
                self.mEval, "panel." + ptype)
            if len(pnames) == 0:
                continue
            panel_descr = dict()
            for pname in pnames:
                p_h = self.mDS.pickSolEntry("panel." + ptype, pname)
                if p_h is not None and p_h.isDynamic():
                    panel_descr[p_h.getName()] = p_h.getSymList()
            if len(panel_descr) > 0:
                panels_supply[ptype] = panel_descr
        if len(panels_supply) > 0:
            receipt["panels-supply"] = panels_supply

        receipt["eval-update-info"] = self.mEval.getUpdateInfo()

        rec_no_seq = sorted(rec_no_seq)
        ws_dir = self.mDS.getDataVault().getDir() + "/" + self.mWSName
        if os.path.exists(ws_dir) and self.mForceMode:
            if self.mDS.getDataVault().getDS(self.mWSName):
                self.mDS.getDataVault().unloadDS(self.mWSName, "ws")
            shutil.rmtree(ws_dir)
        if os.path.exists(ws_dir):
            self.setStatus("Dataset already exists")
            return None

        view_schema = deepcopy(self.mDS.getViewSchema())
        meta_rec = deepcopy(self.mDS.getDataInfo().get("meta"))
        filter_set = FilterPrepareSetH(meta_rec, anfisaVariables,
            "ws", derived_mode = True,
            pre_flt_schema = self.mDS.getFltSchema())

        os.mkdir(ws_dir)
        logging.info("Fill dataset %s datafiles..." % self.mWSName)

        with DataDiskStorageWriter(False, ws_dir, filter_set) as ws_out:
            for _, rec_data in self.mDS.getRecStorage().iterRecords(
                    rec_no_seq):
                ws_out.saveRecord(rec_data)
                if ws_out.getTotal() % self.mReportLines == 0:
                    self.setStatus("Extracting records: %d/%d" %
                        (ws_out.getTotal(), len(rec_no_seq)))

        self.setStatus("Finishing...")
        logging.info("Finalizing derivation %s" % self.mWSName)

        date_loaded = datetime.now().isoformat()
        mongo_agent = self.mDS.getApp().getMongoConnector().getDSAgent(
            self.mWSName, "ws")
        mongo_agent.updateCreationDate(date_loaded)

        if "versions" in meta_rec:
            meta_rec["versions"][
                "Anfisa load"] = self.mDS.getApp().getVersionCode()

        receipts = self.mDS.getDataInfo().get("receipts")
        if receipts is not None:
            receipts = [receipt] + receipts[:]
        else:
            receipts = [receipt]

        ds_info = {
            "name": self.mWSName,
            "kind": "ws",
            "view_schema": view_schema,
            "flt_schema": filter_set.dump(),
            "total": len(rec_no_seq),
            "total_items": self.mDS.getTotal(),
            "mongo": self.mWSName,
            "base": self.mDS.getName(),
            "root": self.mDS.getRootDSName(),
            "modes": ["secondary"],
            "meta": meta_rec,
            "doc": [],
            "zygosity_var": self.mDS.getDataInfo()["zygosity_var"],
            "receipts": receipts,
            "date_loaded": date_loaded}

        with open(ws_dir + "/dsinfo.json", "w", encoding = "utf-8") as outp:
            print(json.dumps(ds_info, sort_keys = True, indent = 4),
                file = outp)

        os.mkdir(ws_dir + "/doc")
        with open(ws_dir + "/doc/info.html", "w", encoding = "utf-8") as outp:
            reportDS(outp, ds_info, mongo_agent, self.mDS.getDataInfo())

        with open(ws_dir + "/active", "w", encoding = "utf-8") as outp:
            print("", file = outp)

        self.mDS.getDataVault().loadDS(self.mWSName, "ws")

        self.setStatus("Done")
        return {"ws": self.mWSName}
