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

import sys, json, os, logging, shutil
from argparse import ArgumentParser
from glob import glob
from datetime import datetime

from forome_tools.json_conf import loadJSonConfig, loadCommentedJSon
from forome_tools.log_err import logException
from app.config.a_config import AnfisaConfig
from app.config.solutions import setupSolutions
from app.config.variables import anfisaVariables
from app.model.dir_entry import DirDSEntry
from app.model.data_vault import DataVault
from app.model.mongo_db import MongoConnector
from app.xl.druid_agent import DruidAgent
from app.prepare.sec_ws import SecondaryWsCreation
from app.eval.filter import FilterEval
from app.eval.dtree import DTreeEval
#=====================================
class DSScanInfo:
    def __init__(self, vault_dict, ds_path):
        self.mVaultDict = vault_dict
        self.mPath = ds_path
        self.mName = os.path.basename(self.mPath)
        self.mVaultDict[self.mName] = self
        self.mInfo = None
        self.mActive = os.path.exists(self.mPath + "/active ")
        info_path = self.mPath + "/dsinfo.json"
        self.mStatus = None
        info_fstat = DataVault.checkFileStat(info_path)
        if info_fstat is None:
            logging.error(
                "Corrupted directory %s, no dsinfo.json" % self.mPath)
        else:
            self.mTimestamp = info_fstat[1]
            try:
                with open(info_path, "r", encoding = "utf-8") as inp:
                    self.mInfo = json.loads(inp.read())
            except Exception:
                logging.error(
                    "Corrupted directory %s, bad dsinfo.json" % self.mPath)
                self.mInfo = None
                self.mStatus - "BAD"

    def getName(self):
        return self.mName

    def isOK(self):
        return self.mInfo is not None

    def getStatus(self):
        return self.mStatus

    def setStatus(self, status):
        self.mStatus = status

    def isActive(self):
        return self.mActive

    def getTimestamp(self):
        return self.mTimestamp

    def getBaseDSName(self):
        return self.mInfo.get("base")

    def getRootDSName(self):
        return self.mInfo.get("root")

    def getDerivationReceipt(self):
        if self.mInfo is None:
            return None
        receipts = self.mInfo.get("receipts")
        if receipts:
            return receipts[0]
        return None

    def makeAncestorPath(self):
        if not self.isOK():
            return ["?", self.mName]
        names = [self.mName]
        ds_name = self.getBaseDSName()
        while ds_name is not None:
            ds_info = self.mVaultDict.get(ds_name)
            if ds_info is None or not ds_info.isOK():
                break
                names.insert(0, ds_name)
            ds_name = ds_info.getBaseDSName()
        if self.getRootDSName() != names[0]:
            ds_info = self.mVaultDict.get(self.getRootDSName())
            if ds_info is None or not ds_info.isOK():
                names.insert(0, "?")
            names.insert(0, self.getRootDSName())
        return names

    def checkDirStatus(self, dir_entry):
        entry_source = dir_entry.getSource()
        if entry_source == "?":
            return None
        info_fstat = DataVault.checkFileStat(entry_source)
        if info_fstat is None:
            return "NO-SOURCE"
        if info_fstat[1] > self.mTimestamp:
            return "PRIMARY-OUT-OF-DATE"
        return None

    def checkBase(self):
        if self.getBaseDSName():
            ds_info = self.mVaultDict.get(self.getBaseDSName())
            if ds_info.isOK():
                if ds_info.getStatus() == "OK":
                    if ds_info.getTimestamp() > self.getTimestamp():
                        return "UPDATE"
                else:
                    if ds_info.getStatus().startswith("UPDATE"):
                        return "UPDATE+"
                    else:
                        return "HEAVY-BLOCK"
            else:
                return "BAD?"
        return "OK"

#===============================================
class UpdateApp:
    def __init__(self, config, vault_info, plain_receipt_mode = False):
        setupSolutions(config)
        self.mConfig = config
        self.mVaultDict = vault_info
        self.mVaultDir = os.path.abspath(self.mConfig["data-vault"])
        self.mMongoConn = MongoConnector(self.mConfig["mongo-db"],
            self.mConfig.get("mongo-host"), self.mConfig.get("mongo-port"))
        self.mDruidAgent = DruidAgent(self.mConfig)
        self.mDataVault = DataVault(self, self.mVaultDir,
            anfisaVariables, auto_mode = False)
        self.mPlainReceiptMode = plain_receipt_mode

    def getMongoConnector(self):
        return self.mMongoConn

    def getDataVault(self):
        return self.mDataVault

    def getDruidAgent(self):
        return self.mDruidAgent

    def hasRunOption(self, name):
        run_options = self.mConfig.get("run-options")
        return run_options and name in run_options

    def getRunModes(self):
        return self.mConfig.get("run-modes", [])

    def getOption(self, name):
        return self.mConfig.get(name)

    def getVersionCode(self):
        return AnfisaConfig.getAnfisaVersion()

    def getBuildHashCode(self):
        return AnfisaConfig.getAnfisaBuildHash()

    def updateDS(self, ds_info):
        receipt = ds_info.getDerivationReceipt()
        if receipt is None:
            logging.error("No receipt?")
            return "NO-RECEIPT"
        try:
            base_info = self.mVaultDict.get(ds_info.getBaseDSName())
            if not base_info or base_info.getStatus() not in ("OK", "UPDATED"):
                logging.error("Bad base dataset status:",
                    base_info.getStatus() if base_info else None)
                return "FAILED"
            if self.mDataVault.getDS(base_info.getName()) is None:
                self.mDataVault.loadDS(base_info.getName())
            base_ds = self.mDataVault.getDS(base_info.getName())
            ds_dir_name = self.mVaultDir + "/" + ds_info.getName()
            tmp_dir_name = ds_dir_name + '~'
            if os.path.exists(tmp_dir_name):
                shutil.rmtree(tmp_dir_name)
            os.rename(ds_dir_name, tmp_dir_name)
        except Exception:
            logException("Exception on preparation for update dataset "
                + ds_info.getName())
            return "EXCEPTION"
        try:
            if receipt["kind"] == "filter":
                if not self.mPlainReceiptMode and receipt.get("filter-name"):
                    flt_name = receipt.get("filter-name")
                    eval_h = base_ds.pickSolEntry("filter", flt_name)
                    if eval_h is None:
                        logging.error("No named filter %s" % flt_name)
                        return ("NO-NAMED")
                else:
                    eval_h = FilterEval(base_ds.getEvalSpace(),
                        receipt["conditions"])
            else:
                receipt["kind"] == "dtree", (
                    "Bad receipt kind: " + receipt["kind"])
                if not self.mPlainReceiptMode and receipt.get("dtree-name"):
                    dtree_name = receipt.get("dtree-name")
                    eval_h = base_ds.pickSolEntry("dtree", dtree_name)
                    if eval_h is None:
                        logging.error("No named dtree: " + dtree_name)
                        return ("NO-NAMED")
                else:
                    eval_h = DTreeEval(base_ds.getEvalSpace(),
                        receipt["dtree-code"])
            eval_h.activate()
            task = SecondaryWsCreation(base_ds, ds_info.getName(),
                eval_h, force_mode = True)
            task.execIt()
        except Exception:
            logException("Exception on update dataset " + ds_info.getName())
            logging.warning("Restore old variant of dataset "
                + ds_info.getName())
            if os.path.exists(ds_dir_name):
                shutil.rmtree(ds_dir_name)
            os.rename(tmp_dir_name, ds_dir_name)
            return "EXCEPTION"
        return "UPDATED"

#===============================================
def reportDS(ds_info, anc_path):
    print("\t".join(["*", ds_info.getStatus(), ds_info.getName()]))
    print("\t\t\t[", "/".join(anc_path), "]")
    receipt = ds_info.getDerivationReceipt()
    if receipt:
        rep = [">receipt", "kind:", receipt["kind"]]
        if receipt["kind"] == "filter":
            if receipt.get("filter-name"):
                rep += ["name:", receipt.get("filter-name")]
            rep += ["c-count:", str(len(receipt["conditions"]))]
        else:
            assert receipt["kind"] == "dtree", (
                "Bad receipt kind: " + receipt["kind"])
            if receipt.get("dtree-name"):
                rep += ["name:", receipt.get("dtree-name")]
            rep += ["d-count:", str(len(receipt["p-presentation"]))]
        print("\t\t\t", " ".join(rep))


#===============================================
if __name__ == '__main__':
    logging.root.setLevel(logging.INFO)

    #========================================
    import forome_tools
    forome_tools.compatible((0, 1, 9))

    #========================================
    if sys.version_info < (3, 7):
        from backports.datetime_fromisoformat import MonkeyPatch
        MonkeyPatch.patch_fromisoformat()

    #========================================
    parser = ArgumentParser()
    parser.add_argument("-d", "--dir",
        help = "Storage directory control file")
    parser.add_argument("-c", "--config",
        help = "Anfisa configuration file, used only if --dir is unset, "
        "default = anfisa.json")
    parser.add_argument("-m", "--mode", default = "scan",
        help = "Mode: scan/update")
    parser.add_argument("-f", "--force", action = "store_true",
        help = "Force update")
    parser.add_argument("-p", "--plainreceipt", action = "store_true",
        help = "Plain receipt in restore, solution names are ignored")
    parser.add_argument("names", nargs = "*", help = "Dataset name(s)")
    args = parser.parse_args()

    if args.force and len(args.names) == 0:
        args.force = False
        logging.warning(
            "Since there is no explicit datasets given --force is set to "
            + str(args.force))

    if args.mode not in ("scan", "update"):
        logging.error("Incorrect mode %s" % args.mode)
        sys.exit()
    entries = None

    if args.dir:
        if args.config:
            logging.error("Incorrect usage: use --dir or --config")
            sys.exit()
        dir_config = loadCommentedJSon(args.dir)
        anfisa_json_file = dir_config["anfisa.json"]
        if len(set(args.names)) != len(args.names):
            dup_names = args.names[:]
            for ds_name in set(args.names):
                dup_names.remove(ds_name)
            logging.error("Incorrect usage: ds name duplication: "
                + " ".join(dup_names))
            sys.exit()
        if len(args.names) > 0:
            entries = []
            for ds_name in args.names:
                if ds_name in dir_config["datasets"]:
                    entries.append(DirDSEntry.createByDirConfig(
                        ds_name, dir_config, args.dir))
                else:
                    entries.append(DirDSEntry(ds_name, "?", "?"))
    else:
        dir_config = None
        anfisa_json_file = args.config
        if not anfisa_json_file:
            anfisa_json_file = "./anfisa.json"
        if len(args.names) > 0:
            entries = [DirDSEntry(ds_name, "?", "?")
                for ds_name in args.names]

    app_config = loadJSonConfig(anfisa_json_file,
        home_base_file = __file__, home_base_level = 1)

    vault_dir = app_config["data-vault"]

    vault_info = dict()
    for info_path in glob(vault_dir + "/*/dsinfo.json"):
        if DataVault.excludeDSDir(os.path.dirname(info_path)):
            continue
        DSScanInfo(vault_info, os.path.dirname(info_path))

    sheet_ds = [(ds_info.makeAncestorPath(), ds_info)
        for ds_info in vault_info.values()]
    sheet_ds.sort(key = lambda rec: rec[0])

    dict_entries = ({entry.getName(): entry for entry in entries}
        if entries is not None else None)

    for anc_path, ds_info in sheet_ds:
        if not ds_info.isOK():
            assert ds_info.getStatus() is not None, (
                "Dataset: " + ds_info.getName() + " has improper status")
            continue
        assert ds_info.getStatus() is None, (
            "Dataset: " + ds_info.getName() + " has empty status")
        if "?" in anc_path:
            ds_info.setStatus("BLOCKED")
            continue
        if dict_entries and ds_info.getName() in dict_entries:
            status = ds_info.checkDirStatus(dict_entries[ds_info.getName()])
            if status:
                ds_info.setStatus(status)
                continue
        ds_info.setStatus(ds_info.checkBase())

    if args.mode == "scan":
        for anc_path, ds_info in sheet_ds:
            if dict_entries and ds_info.getName() not in dict_entries:
                continue
            reportDS(ds_info, anc_path)
        sys.exit()

    if args.mode == "update":
        update_app = UpdateApp(app_config, vault_info, args.plainreceipt)

        for anc_path, ds_info in sheet_ds:
            if dict_entries and ds_info.getName() not in dict_entries:
                continue
            reportDS(ds_info, anc_path)
            if not ds_info.isOK():
                print("Skipped: dataset is bad")
                continue
            if not ds_info.getBaseDSName():
                print("Skipped: dataset is root")
                continue
            if ds_info.getStatus() == "OK":
                if not args.force:
                    print("Skipped: use --force to force update")
                    continue
            elif not ds_info.getStatus().startswith("UPDATE"):
                print("Skipped because of status")
                continue
            dt_start = datetime.now()
            print("Update of", ds_info.getName(), "starts at", dt_start)
            upd_status = update_app.updateDS(ds_info)
            dt_end = datetime.now()
            print("Update of", ds_info.getName(), "ends at", dt_end,
                "for", (dt_end - dt_start))
            print("Status:", upd_status)
            if upd_status == "UPDATED":
                ds_info.setStatus(upd_status)
            else:
                print("Terminated because of failures")
                break
        sys.exit()

    print("Bad mode:", args.mode())
