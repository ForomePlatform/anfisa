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
from datetime import datetime

from forome_tools.json_conf import loadJSonConfig, loadCommentedJSon
from forome_tools.inventory import loadDatasetInventory
from app.prepare.druid_adm import DruidAdmin
from app.prepare.html_report import reportDS
from app.prepare.doc_works import prepareDocDir
from app.prepare.ds_create import (createDS,
    portionFavorDruidPush, pushDruidDataset)
from app.config.solutions import readySolutions
from app.model.mongo_db import MongoConnector
from app.model.dir_entry import DirDSEntry
from app.model.ds_favor import FavorStorageAgent
#===============================================
sID_Pattern = re.compile('^\\S+$', re.U)

def checkDSName(name, kind):
    global sID_Pattern
    if not sID_Pattern.match(name) or not name[0].isalpha():
        print("Incorrect dataset name:", name, file = sys.stderr)
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
def createDataSet(app_config, ds_entry, force_drop, druid_adm,
        report_lines, no_druid_push = False):
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
        ds_entry.getInv(), report_lines, no_druid_push)
    mongo_conn.close()

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

    mongo_conn.close()
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
    mongo_conn.close()

#===============================================
def dropFavor(app_config, druid_adm, report_lines):
    vault_dir = app_config["data-vault"]
    ds_dir = os.path.abspath(vault_dir + "/xl_FAVOR")
    if not os.path.exists(ds_dir):
        print("No dataset to drop:", ds_dir)
        return
    shutil.rmtree(ds_dir)
    print("Dataset droped:", ds_dir)

#===============================================
def portionFavor(app_config, druid_adm, portion_no, report_lines,
        inside_mode = False):
    favor_storage = prepareFavorStorage(app_config)
    if not inside_mode:
        print("Favor portions:", favor_storage.getPortionCount())
    print("Push portion", portion_no)
    vault_dir = app_config["data-vault"]
    ds_dir = os.path.abspath(vault_dir + "/xl_FAVOR")
    portionFavorDruidPush(ds_dir, druid_adm, favor_storage, portion_no)
    print("Done portion", portion_no)

#===============================================
def ftuneFavor(app_config, druid_adm, report_lines):
    vault_dir = app_config["data-vault"]
    ds_name = "xl_FAVOR"
    ds_dir = os.path.abspath(vault_dir + "/" + ds_name)
    with open(ds_dir + "/dsinfo.json",
            "r", encoding = "utf-8") as inp:
        ds_info = json.loads(inp.read())
    ds_info["total"] = druid_adm.mineTotal(ds_name)
    for funit_entry in ds_info["flt_schema"]:
        if funit_entry["kind"] == "enum":
            variants = druid_adm.mineEnumVariants(
                ds_name, funit_entry["name"])
            print("Unit update: %s  %d -> %d" % (funit_entry["name"],
                len(funit_entry["variants"]), len(variants)))
            funit_entry["variants"] = variants
    with open(ds_dir + "/~dsinfo.json", "w", encoding = "utf-8") as outp:
        print(json.dumps(ds_info, sort_keys = True, indent = 4),
            file = outp)
    os.rename(ds_dir + "/dsinfo.json", ds_dir + "/dsinfo.json~")
    os.rename(ds_dir + "/~dsinfo.json", ds_dir + "/dsinfo.json")
    print("Filter variants tuning done")

#===============================================
def _favorBatch(app_config, druid_adm, batch_dir, report_lines):
    assert os.path.isdir(batch_dir), (
        "Bad batch directory: " + batch_dir)
    if os.path.exists(batch_dir + "/stop"):
        print("STOPPED")
        with open(batch_dir + "/log", "at") as outp:
            print("%s: STOPED" % str(datetime.now()), file = outp)
        return False
    assert os.path.exists(batch_dir + "/loaded.txt"), (
        "No file:" + batch_dir + "/loaded.txt")
    loaded_idxs = set()
    with open(batch_dir + "/loaded.txt", "rt") as inp:
        for line_idx, line in enumerate(inp):
            idx_str = line.strip()
            assert idx_str.isdigit(), (
                "loaded.txt at line %d: bad line" % (line_idx + 1))
            idx = int(idx_str)
            assert idx not in loaded_idxs, (
                "loaded.txt at line %d: duplicated idx %d"
                % (line_idx + 1, idx))
            loaded_idxs.add(idx)
    favor_storage = prepareFavorStorage(app_config)
    p_count = favor_storage.getPortionCount()
    next_portion = None
    for idx in range(p_count - 1):
        if idx not in loaded_idxs:
            next_portion = idx
            break
    if next_portion is None:
        print("MISSION COMPLETE (check last portion", p_count - 1)
        with open(batch_dir + "/log", "at") as outp:
            print("%s: COMPLETE" % str(datetime.now()), file = outp)
        return False
    with open(batch_dir + "/log", "at") as outp:
        print("%s: Push portion %d" % (str(datetime.now()), next_portion),
            file = outp)
    portionFavor(app_config, druid_adm, next_portion, report_lines, True)
    loaded_idxs.add(next_portion)
    with open(batch_dir + "/~loaded.txt", "wt") as outp:
        for idx in sorted(loaded_idxs):
            print(idx, file = outp)
    os.rename(batch_dir + "/loaded.txt", batch_dir + "/loaded.txt~")
    os.rename(batch_dir + "/~loaded.txt", batch_dir + "/loaded.txt")
    with open(batch_dir + "/log", "at") as outp:
        print("%s: Done portion %d" % (str(datetime.now()), next_portion),
            file = outp)
    return True

#===============================================
def favorBatch(app_config, druid_adm, batch_dir, report_lines):
    while _favorBatch(app_config, druid_adm, batch_dir, report_lines):
        pass


#===============================================
if __name__ == '__main__':
    try:
        sys.stderr = codecs.getwriter('utf8')(sys.stderr.detach())
        sys.stdout = codecs.getwriter('utf8')(sys.stdout.detach())
    except Exception:
        pass
    logging.root.setLevel(logging.INFO)

    #========================================
    import forome_tools
    forome_tools.compatible((0, 1, 3))

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
    parser.add_argument("--nodruidpush", action = "store_true",
        help = "No push into Druid, if mode = create")
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
        dir_config = loadCommentedJSon(args.dir)
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
        app_config = loadJSonConfig(args.config,
            home_base_file = __file__, home_base_level = 1)
        druid_adm = DruidAdmin(app_config, False)
        if args.names[0] == "init":
            assert len(args.names) == 1, (
                "favor init does not require more arguments")
            initFavor(app_config, druid_adm, args.reportlines)
        elif args.names[0] == "remove":
            assert len(args.names) == 1, (
                "favor remove does not require more arguments")
            dropFavor(app_config, druid_adm, args.reportlines)
        elif args.names[0] == "ftune":
            assert len(args.names) == 1, (
                "favor ftune does not require more arguments")
            ftuneFavor(app_config, druid_adm, args.reportlines)
        elif args.names[0] == "info":
            favor_storage = prepareFavorStorage(app_config)
            print("Favor size:", favor_storage.getTotal(), "portions:",
                favor_storage.getPortionCount())
        elif args.names[0] == "batch":
            assert len(args.names) == 2, (
                "favor batch requires one more argiment: batch directory")
            batch_dir = args.names[1]
            favorBatch(app_config, druid_adm, batch_dir, args.reportlines)
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
        dir_config = loadCommentedJSon(args.dir)
        anfisa_json_file = dir_config["anfisa.json"]
        if len(set(args.names)) != len(args.names):
            dup_names = args.names[:]
            for ds_name in set(args.names):
                dup_names.remove(ds_name)
            print("Incorrect usage: ds name duplication:", " ".join(dup_names))
            sys.exit()
        entries = [DirDSEntry.createByDirConfig(ds_name, dir_config, args.dir)
            for ds_name in args.names]
    else:
        if args.source and args.inv:
            print("Incorrect usage: use either --source or --inv")
        anfisa_json_file = args.config
        if not anfisa_json_file:
            anfisa_json_file = "./anfisa.json"
        if len(args.names) != 1 and (args.source or args.inv):
            print("Incorrect usage: --source applies only to one ds")
            sys.exit()
        if args.inv:
            ds_inventory = loadDatasetInventory(args.inv)
            if len(args.names) != 1:
                print("Only one DS should be set with --inv option")
                sys.exit(1)
            entries = [DirDSEntry.createByInventory(
                args.names[0], args.kind, ds_inventory)]
        else:
            entries = [DirDSEntry(ds_name, args.kind, args.source)
                for ds_name in args.names]

    app_config = loadJSonConfig(anfisa_json_file,
        home_base_file = __file__, home_base_level = 1)

    assert os.path.isdir(app_config["data-vault"])

    druid_adm = None
    if any(ds_entry.getDSKind() == "xl" for ds_entry in entries):
        druid_adm = DruidAdmin(app_config, args.nocoord)

    for entry_no,  ds_entry in enumerate(entries):
        if entry_no > 0 and args.delay > 0:
            time.sleep(args.delay)
        if args.mode == "create":
            createDataSet(app_config, ds_entry, args.force,
                druid_adm, args.reportlines, args.nodruidpush)
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
