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

import sys, codecs, json, os, shutil, re, time, logging
from argparse import ArgumentParser

import utils.json_conf as json_conf
from app.prepare.druid_adm import DruidAdmin
from app.prepare.html_report import reportDS
from app.prepare.doc_works import prepareDocDir
from app.prepare.ds_create import (createDS,
    portionFavorDruidPush, pushDruidDataset)
from app.config.solutions import readySolutions
from app.model.mongo_db import MongoConnector
from app.model.ds_favor import FavorStorageAgent
#=====================================
try:
    sys.stdin  = codecs.getreader('utf8')(sys.stdin.detach())
    sys.stderr = codecs.getwriter('utf8')(sys.stderr.detach())
    sys.stdout = codecs.getwriter('utf8')(sys.stdout.detach())
except Exception:
    pass

if sys.version_info < (3, 7):
    from backports.datetime_fromisoformat import MonkeyPatch
    MonkeyPatch.patch_fromisoformat()

#===============================================
sID_Pattern = re.compile('^\\S+$', re.U)

def checkDSName(name, kind):
    global sID_Pattern
    if not sID_Pattern.match(name) or not name[0].isalpha():
        print("Incorrect dataset name:", name, file=sys.stderr)
        assert False
    if kind == "ws":
        if name.lower().startswith("xl_"):
            print("Improper WS name:", name, file = sys.stderr)
            print("(Should not have prefix XL_)", file = sys.stderr)
            assert False
    elif kind == "xl":
        if not name.lower().startswith("xl_"):
            print("Improper XL-dataset name:", name, file = sys.stderr)
            print("(Should have prefix XL_ or xl_)", file = sys.stderr)
            assert False
    else:
        print("Wrong dataset kind:", kind)
        assert False

#===============================================
def createDataSet(app_config, ds_entry, force_drop, druid_adm, report_lines):
    readySolutions()

    if not ds_entry.getSource():
        print("Improper creation datset",  ds_entry.getName(),  ": no source")
        sys.exit()

    vault_dir = app_config["data-vault"]
    if force_drop:
        dropDataSet(app_config, ds_entry, druid_adm, True)

    if not os.path.isdir(vault_dir):
        os.mkdir(vault_dir)
        print("Create (empty) vault directory:", vault_dir, file = sys.stderr)

    checkDSName(ds_entry.getName(), ds_entry.getDSKind())
    ds_dir = os.path.abspath(vault_dir + "/" + ds_entry.getName())
    if os.path.exists(ds_dir):
        print("Dataset exists:", ds_dir, file = sys.stderr)
        assert False
    os.mkdir(ds_dir)

    mongo_conn = MongoConnector(app_config["mongo-db"],
        app_config.get("mongo-host"), app_config.get("mongo-port"))

    createDS(ds_dir, mongo_conn, druid_adm,
        ds_entry.getName(), ds_entry.getSource(), ds_entry.getDSKind(),
        ds_entry.getInv(), report_lines)

#===============================================
def pushDruid(app_config, ds_entry, druid_adm):
    vault_dir = app_config["data-vault"]
    if not os.path.isdir(vault_dir):
        print("No vault directory:", vault_dir, file = sys.stderr)
        assert False
    if ds_entry.getDSKind() != "xl":
        print("Druid dataset %s has unexpected kind %s" %
            (ds_entry.getName(),  ds_entry.getDSKind()),
            file = sys.stderr)
        sys.exit()
    checkDSName(ds_entry.getName(), "xl")

    druid_datasets = druid_adm.listDatasets()
    if ds_entry.getName() in druid_datasets:
        druid_adm.dropDataset(ds_entry.getName())

    ds_dir = os.path.abspath(vault_dir + "/" + ds_entry.getName())
    is_ok = pushDruidDataset(ds_dir, druid_adm, ds_entry.getName())
    if is_ok:
        print("Druid dataset %s pushed" % ds_entry.getName())
    else:
        print("Process failed")

#===============================================
def _dropDruidDataset(druid_adm, ds_name, calm_mode = False):
    if calm_mode:
        druid_datasets = druid_adm.listDatasets()
    else:
        druid_datasets = [ds_name]
    if ds_name in druid_datasets:
        druid_adm.dropDataset(ds_name)
    elif not calm_mode:
        print("No dataset in Druid to drop:", ds_name)


#===============================================
def dropDataSet(app_config, ds_entry, druid_adm, calm_mode):
    assert ds_entry.getDSKind() in ("ws", "xl")
    vault_dir = app_config["data-vault"]
    ds_dir = os.path.abspath(vault_dir + "/" + ds_entry.getName())

    if ds_entry.getDSKind() == "xl":
        _dropDruidDataset(druid_adm, ds_entry.getName(), calm_mode)

    if not os.path.exists(ds_dir):
        if not calm_mode:
            print("No dataset to drop:", ds_dir)
        return
    shutil.rmtree(ds_dir)
    print("Dataset droped:", ds_dir)

#===============================================
def pushDoc(app_config, ds_entry):
    vault_dir = app_config["data-vault"]
    ds_dir = os.path.abspath(vault_dir + "/" + ds_entry.getName())

    with open(ds_dir + "/dsinfo.json",
            "r", encoding = "utf-8") as inp:
        ds_info = json.loads(inp.read())
    ds_doc_dir = ds_dir + "/doc"
    ds_info["doc"] = prepareDocDir(ds_doc_dir, ds_entry.getInv(), reset = True)

    mongo_conn = MongoConnector(app_config["mongo-db"],
        app_config.get("mongo-host"), app_config.get("mongo-port"))
    mongo_agent = mongo_conn.getDSAgent(ds_info["name"], ds_info["kind"])
    with open(ds_dir + "/dsinfo.json", "w", encoding = "utf-8") as outp:
        print(json.dumps(ds_info, sort_keys = True, indent = 4),
            file = outp)

    with open(ds_doc_dir + "/info.html", "w", encoding = "utf-8") as outp:
        reportDS(outp, ds_info, mongo_agent)

    print("Re-doc complete:", ds_dir)

#===============================================
def prepareFavorStorage(app_config):
    portion_size, portion_fetch = app_config["favor-portions"]
    return FavorStorageAgent(app_config["favor-url"],
        portion_size, portion_fetch)

#===============================================
def initFavor(app_config, druid_adm, report_lines):
    readySolutions()

    vault_dir = app_config["data-vault"]
    if not os.path.isdir(vault_dir):
        os.mkdir(vault_dir)
        print("Create (empty) vault directory:", vault_dir, file = sys.stderr)

    ds_dir = os.path.abspath(vault_dir + "/xl_FAVOR")
    if os.path.exists(ds_dir):
        print("Dataset exists:", ds_dir, file = sys.stderr)
        assert False
    os.mkdir(ds_dir)

    mongo_conn = MongoConnector(app_config["mongo-db"],
        app_config.get("mongo-host"), app_config.get("mongo-port"))

    createDS(ds_dir, mongo_conn, druid_adm,
        "xl_FAVOR", None, "xl", report_lines = report_lines,
        favor_storage = prepareFavorStorage(app_config))

#===============================================
def dropFavor(app_config, druid_adm, report_lines):
    _dropDruidDataset(druid_adm, "xl_FAVOR")

    vault_dir = app_config["data-vault"]
    ds_dir = os.path.abspath(vault_dir + "/xl_FAVOR")
    if not os.path.exists(ds_dir):
        print("No dataset to drop:", ds_dir)
        return
    shutil.rmtree(ds_dir)
    print("Dataset droped:", ds_dir)

#===============================================
def portionFavor(app_config, druid_adm, portion_no, report_lines):
    favor_storage = prepareFavorStorage(app_config)
    print("Favor portions:", favor_storage.getPortionCount())
    vault_dir = app_config["data-vault"]
    ds_dir = os.path.abspath(vault_dir + "/xl_FAVOR")
    portionFavorDruidPush(ds_dir, druid_adm, favor_storage, portion_no)

#===============================================
class DSEntry:
    def __init__(self,  ds_name,  ds_kind,  source,  ds_inventory = None,
            entry_data = None):
        self.mName = ds_name
        self.mKind = ds_kind
        self.mSource = source
        self.mInv  = ds_inventory
        self.mEntryData = entry_data

    def getName(self):
        return self.mName

    def getDSKind(self):
        return self.mKind

    def getSource(self):
        return self.mSource

    def getInv(self):
        return self.mInv

    def dump(self):
        return {
            "name": self.mName,
            "kind": self.mKind,
            "source": self.mSource,
            "inv": self.mInv,
            "data": self.mEntryData}

    @classmethod
    def createByDirConfig(cls, ds_name,  dir_config,  dir_fname):
        if ds_name not in dir_config["datasets"]:
            print("Dataset %s not registered in directory file (%s)" %
                (ds_name, dir_fname), file = sys.stderr)
            sys.exit()
        ds_entry_data = dir_config["datasets"][ds_name]
        if "inv" in ds_entry_data:
            ds_inventory = json_conf.loadDatasetInventory(ds_entry_data["inv"])
            return DSEntry(ds_name,
                ds_entry_data["kind"], ds_inventory["a-json"], ds_inventory,
                entry_data = {
                    "arg-dir": ds_entry_data, "arg-inv": ds_inventory})
        if "a-json" in ds_entry_data:
            return DSEntry(ds_name,  ds_entry_data["kind"],
                ds_entry_data["a-json"],
                entry_data = {"arg-dir": ds_entry_data})
        print(("Dataset %s: no correct source or inv registered "
            "in directory file (%s)") % (ds_name, dir_fname),
            file = sys.stderr)
        sys.exit()
        return None


#===============================================
if __name__ == '__main__':
    logging.root.setLevel(logging.INFO)

    parser = ArgumentParser()
    parser.add_argument("-d", "--dir",
        help = "Storage directory control file")
    parser.add_argument("-c", "--config",
        help = "Anfisa configuration file, used only if --dir is unset, "
        "default = anfisa.json")
    parser.add_argument("-m", "--mode",
        help = "Mode: create/drop/druid-push/doc-push/register/favor")
    parser.add_argument("-k", "--kind",  default = "ws",
        help = "Kind of dataset: ws/xl, default = ws, "
        "actual if --dir is unset")
    parser.add_argument("-s", "--source", help="Annotated json, "
        "actual if --dir is unset and mode = create")
    parser.add_argument("-i", "--inv", help="Annotation inventory")
    parser.add_argument("-f", "--force", action = "store_true",
        help = "Force removal, actual if mode = create")
    parser.add_argument("-C", "--nocoord", action = "store_true",
        help = "Druid: no use coordinator")
    parser.add_argument("--reportlines", type = int, default = 100,
        help = "Portion for report lines, default = 100")
    parser.add_argument("--delay",  type = int,  default = 0,
        help = "Delay between work with multiple datasets, in seconds")
    parser.add_argument("names", nargs = "+", help = "Dataset name(s)")
    args = parser.parse_args()

    if args.mode == "register":
        if (not args.dir or (not args.source and not args.inv)
                or (args.source and args.inv)):
            print("Improper arguments: mode register requires "
                "--dir and (--source or --inv)")
            sys.exit()
        if len(args.names) != 1:
            print("Only one dataset can be registered")
            sys.exit(1)
        dir_config = json.loads(
            json_conf.readCommentedJSon(args.dir))
        new_descr = {"kind": args.kind}
        if args.source:
            new_descr["a-json"] = args.source
        else:
            new_descr["inv"] = args.inv
        dir_config["datasets"][args.names[0]] = new_descr
        tmp_name = '~' + args.dir + '.tmp'
        with open(tmp_name, "w", encoding = "utf-8") as outp:
            outp.write(json.dumps(dir_config,
                indent = 4, sort_keys = True, ensure_ascii = False))
        os.rename(args.dir, args.dir + '~')
        os.rename(tmp_name, args.dir)
        print("Directory file", args.dir, "updated")
        sys.exit()

    if args.mode == "favor":
        app_config = json_conf.loadJSonConfig(args.config)
        druid_adm = DruidAdmin(app_config, False)
        if args.names[0] == "init":
            assert len(args.names) == 1, (
                "favor init does not require more arguments")
            initFavor(app_config, druid_adm, args.reportlines)
        elif args.names[0] == "remove":
            assert len(args.names) == 1, (
                "favor remove does not require more arguments")
            dropFavor(app_config, druid_adm, args.reportlines)
        elif args.names[0] == "info":
            favor_storage = prepareFavorStorage(app_config)
            print("Favor size:", favor_storage.getTotal(), "portions:",
                favor_storage.getPortionCount())
        else:
            assert args.names[0] == "portion", (
                "favor options: init/remove/info/portion <no>")
            assert len(args.names) == 2, (
                "favor portion requires one more argiment: portion no")
            portion_no = int(args.names[1])
            portionFavor(app_config, druid_adm, portion_no, args.reportlines)
        sys.exit()

    if args.dir:
        if args.config or args.source or args.inv:
            print("Incorrect usage: use --dir or "
                "(--config, [--source, --inv])")
            sys.exit()
        dir_config = json.loads(
            json_conf.readCommentedJSon(args.dir))
        service_config_file = dir_config["anfisa.json"]
        if len(set(args.names)) != len(args.names):
            dup_names = args.names[:]
            for ds_name in set(args.names):
                dup_names.remove(ds_name)
            print("Incorrect usage: ds name duplication:", " ".join(dup_names))
            sys.exit()
        entries = [DSEntry.createByDirConfig(ds_name,  dir_config, args.dir)
            for ds_name in args.names]
    else:
        if args.source and args.inv:
            print("Incorrect usage: use either --source or --inv")
        service_config_file = args.config
        if not service_config_file:
            service_config_file = "./anfisa.json"
        if len(args.names) != 1 and (args.source or args.inv):
            print("Incorrect usage: --source applies only to one ds")
            sys.exit()
        if args.inv:
            ds_inventory = json_conf.loadDatasetInventory(args.inv)
            ds_name = args.names[0]
            entries = [DSEntry(ds_name, args.kind, ds_inventory["a-json"],
                ds_inventory, entry_data = {"arg-inv": ds_inventory})]
        else:
            entries = [DSEntry(ds_name,  args.kind,  args.source)
                for ds_name in args.names]

    app_config = json_conf.loadJSonConfig(service_config_file)

    assert os.path.isdir(app_config["data-vault"])

    druid_adm = None
    if any(ds_entry.getDSKind() == "xl" for ds_entry in entries):
        druid_adm = DruidAdmin(app_config, args.nocoord)

    for entry_no,  ds_entry in enumerate(entries):
        if entry_no > 0 and args.delay > 0:
            time.sleep(args.delay)
        if args.mode == "create":
            createDataSet(app_config, ds_entry, args.force,
                druid_adm, args.reportlines)
        elif args.mode == "drop":
            dropDataSet(app_config, ds_entry, druid_adm, False)
        elif args.mode == "druid-push":
            pushDruid(app_config, ds_entry, druid_adm)
        elif args.mode == "doc-push":
            pushDoc(app_config, ds_entry)
        elif args.mode == "register":
            pushDoc(app_config, ds_entry)
        elif args.mode == "debug-info":
            print("Info:", json.dumps(
                ds_entry.dump(), indent = 4, sort_keys = True))
        else:
            print("Bad mode:", args.mode)
            sys.exit()

#===============================================
