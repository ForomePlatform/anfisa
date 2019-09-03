import sys, gzip, codecs, json, os, shutil, re
from argparse import ArgumentParser
from io import StringIO, TextIOWrapper
from datetime import datetime
from subprocess import Popen, PIPE

import utils.json_conf as json_conf
from utils.read_json import JsonLineReader
from app.model.pre_fields import PresentationData
from app.prepare.v_check import ViewDataChecker
from app.prepare.druid_adm import DruidAdmin
from app.prepare.html_report import reportDS
from app.prepare.doc_works import prepareDocDir
from app.prepare.trans_prep import TranscriptPreparator
from app.config.a_config import AnfisaConfig
from app.config.flt_schema import defineFilterSchema
from app.config.view_schema import defineViewSchema
from app.config.solutions import prepareSolutions
from app.model.mongo_db import MongoConnector
#=====================================
sys.stdin  = codecs.getreader('utf8')(sys.stdin.detach())
sys.stderr = codecs.getwriter('utf8')(sys.stderr.detach())
sys.stdout = codecs.getwriter('utf8')(sys.stdout.detach())

if sys.version_info < (3, 7):
    from backports.datetime_fromisoformat import MonkeyPatch
    MonkeyPatch.patch_fromisoformat()

#========================================
DRUID_ADM = None

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
def createDataSet(app_config, name, kind, mongo,
        source, ds_inventory, report_lines, date_loaded):
    global DRUID_ADM
    vault_dir = app_config["data-vault"]
    if not os.path.isdir(vault_dir):
        print("No vault directory:", vault_dir, file = sys.stderr)
        assert False
    checkDSName(name, kind)
    ds_dir = os.path.abspath(vault_dir + "/" + name)
    if not mongo:
        mongo = name
    if os.path.exists(ds_dir):
        print("Dataset exists:", ds_dir, file = sys.stderr)
        assert False
    assert (kind == "xl") == (DRUID_ADM is not None)
    os.mkdir(ds_dir)

    anfisa_version = AnfisaConfig.getAnfisaVersion()
    prepareSolutions()
    post_proc = None
    view_aspects = defineViewSchema()
    view_checker = ViewDataChecker(view_aspects)
    filter_set = defineFilterSchema()

    if kind == "ws":
        trans_prep = TranscriptPreparator(
            filter_set.getTranscriptDescrSeq(), True)
    else:
        trans_prep = None

    if report_lines:
        print("Processing...", file = sys.stderr)

    data_rec_no = 0
    metadata_record = None

    vdata_out = Popen(sys.executable + " -m utils.ixbz2 --calm -o " +
        ds_dir + "/vdata.ixbz2 /dev/stdin", shell = True,
        stdin = PIPE, stderr = PIPE,
        bufsize = 1, universal_newlines = False, # line buffer
        close_fds = True)

    vdata_stdin = TextIOWrapper(vdata_out.stdin, encoding = "utf-8",
        line_buffering = True)

    with    gzip.open(ds_dir + "/fdata.json.gz", 'wb') as fdata_stream, \
            gzip.open(ds_dir + "/pdata.json.gz", 'wb') as pdata_stream, \
            JsonLineReader(source) as input:
        fdata_out = TextIOWrapper(fdata_stream,
            encoding = "utf-8", line_buffering = True)
        pdata_out = TextIOWrapper(pdata_stream,
            encoding = "utf-8", line_buffering = True)
        for inp_rec_no, record in enumerate(input):
            if post_proc is not None:
                post_proc.transform(inp_rec_no, record)
            if record.get("record_type") == "metadata":
                assert inp_rec_no == 0
                metadata_record = record
                if "versions" in metadata_record:
                    metadata_record["versions"]["Anfisa load"] = anfisa_version
                filter_set.setMeta(metadata_record)
                continue
            flt_data = filter_set.process(data_rec_no, record)
            view_checker.regValue(data_rec_no, record)
            print(json.dumps(record, ensure_ascii = False), file = vdata_stdin)
            pre_data = PresentationData.make(record)
            if DRUID_ADM is not None:
                DRUID_ADM.addFieldsToRec(flt_data, pre_data, data_rec_no)
            if trans_prep is not None:
                trans_prep.doRec(record, flt_data)
            print(json.dumps(flt_data, ensure_ascii = False), file = fdata_out)
            print(json.dumps(pre_data, ensure_ascii = False), file = pdata_out)
            data_rec_no += 1
            if report_lines and data_rec_no % report_lines == 0:
                sys.stderr.write("\r%d lines..." % data_rec_no)
    if report_lines:
        print("\nTotal lines: %d" % data_rec_no, file = sys.stderr)

    _, vreport_data = vdata_out.communicate()
    for line in str(vreport_data, encoding="utf-8").splitlines():
        print(line, file = sys.stderr)
    vdata_out.wait()

    rep_out = StringIO()
    is_ok = view_checker.finishUp(rep_out)
    is_ok &= filter_set.reportProblems(rep_out)

    if trans_prep is not None:
        total_item_count = trans_prep.finishUp()
    else:
        total_item_count = None

    flt_schema_data = filter_set.dump()
    if kind == "xl":
        is_ok &= DRUID_ADM.uploadDataset(name, flt_schema_data,
            os.path.abspath(ds_dir + "/fdata.json.gz"),
            os.path.abspath(ds_dir + "/druid_rq.json"))

    if is_ok:
        ds_doc_dir = ds_dir + "/doc"
        ds_info = {
            "name": name,
            "kind": kind,
            "view_schema": view_aspects.dump(),
            "flt_schema": flt_schema_data,
            "total": data_rec_no,
            "mongo": mongo,
            "modes": [],
            "family": filter_set.getFamilyInfo().dump(),
            "meta": metadata_record,
            "doc": prepareDocDir(ds_doc_dir, ds_inventory),
            "date_loaded": date_loaded}

        if total_item_count is not None:
            ds_info["total_items"] = total_item_count

        with open(ds_dir + "/dsinfo.json", "w", encoding = "utf-8") as outp:
            print(json.dumps(ds_info, sort_keys = True, indent = 4),
                file = outp)

        with open(ds_dir + "/stat.json", "w", encoding = "utf-8") as outp:
            print(json.dumps(view_checker.dump(), sort_keys = True,
                indent = 4), file = outp)

        mongo_conn = MongoConnector(app_config["mongo-db"],
            app_config.get("mongo-host"), app_config.get("mongo-port"))
        mongo_agent = mongo_conn.getDSAgent(name, kind)
        mongo_agent.checkCreationDate(date_loaded, source)

        with open(ds_dir + "/doc/info.html", "w", encoding = "utf-8") as outp:
            reportDS(outp, ds_info, mongo_agent)

        with open(ds_dir + "/active", "w", encoding = "utf-8") as outp:
            print("", file = outp)
        print("Dataset %s kind=%s succesively created" % (
            name, kind), file = rep_out)
    else:
        print("Process terminated", file = rep_out)

    with open(ds_dir + "/create.log",
            "w", encoding = "utf-8") as outp:
        print(rep_out.getvalue(), file = outp)

    print(rep_out.getvalue())

#===============================================
def pushDruid(app_config, name):
    global DRUID_ADM
    vault_dir = app_config["data-vault"]
    if not os.path.isdir(vault_dir):
        print("No vault directory:", vault_dir, file = sys.stderr)
        assert False
    checkDSName(name, "xl")

    druid_datasets = DRUID_ADM.listDatasets()
    if name in druid_datasets:
        DRUID_ADM.dropDataset(name)

    ds_dir = os.path.abspath(vault_dir + "/" + name)
    with open(ds_dir + "/dsinfo.json",
            "r", encoding = "utf-8") as inp:
        ds_info = json.loads(inp.read())
    is_ok = DRUID_ADM.uploadDataset(name, ds_info["flt_schema"],
        os.path.abspath(ds_dir + "/fdata.json.gz"),
        os.path.abspath(ds_dir + "/druid_rq.json"))
    if is_ok:
        print("Druid dataset %s pushed" % name)
    else:
        print("Process failed")

#===============================================
def dropDataSet(app_config, name, kind, calm_mode):
    global DRUID_ADM
    assert kind in ("ws", "xl")
    assert (kind == "xl") == (DRUID_ADM is not None)
    vault_dir = app_config["data-vault"]
    ds_dir = os.path.abspath(vault_dir + "/" + name)

    if kind == "xl":
        if calm_mode:
            druid_datasets = DRUID_ADM.listDatasets()
        else:
            druid_datasets = [name]
        if name in druid_datasets:
            DRUID_ADM.dropDataset(name)
        elif not calm_mode:
            print("No dataset in Druid to drop:", name)

    if not os.path.exists(ds_dir):
        if not calm_mode:
            print("No dataset to drop:", ds_dir)
        return
    shutil.rmtree(ds_dir)
    print("Dataset droped:", ds_dir)

#===============================================
def checkDataSet(app_config, name, kind):
    vault_dir = app_config["data-vault"]
    ds_dir = os.path.abspath(vault_dir + "/" + name)

    print("Check", ds_dir, ":", os.path.exists(ds_dir),
        os.path.exists(ds_dir + "/active"))

#===============================================
def pushDoc(app_config, name, ds_inventory):
    vault_dir = app_config["data-vault"]
    ds_dir = os.path.abspath(vault_dir + "/" + name)

    with open(ds_dir + "/dsinfo.json",
            "r", encoding = "utf-8") as inp:
        ds_info = json.loads(inp.read())
    ds_doc_dir = ds_dir + "/doc"
    ds_info["doc"] = prepareDocDir(ds_doc_dir, ds_inventory, reset = True)

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
if __name__ == '__main__':
    parser = ArgumentParser()
    parser.add_argument("-d", "--dir",
        help = "Storage directory control file")
    parser.add_argument("-c", "--config",
        help = "Anfisa configuration file,  default = anfisa.json")
    parser.add_argument("-m", "--mode",
        help = "Mode: create/drop/druid-push/doc-push")
    parser.add_argument("-k", "--kind",  default = "ws",
        help = "Kind of dataset: ws/xl, default=ws")
    parser.add_argument("-s", "--source", help="Annotated json")
    parser.add_argument("-i", "--inv", help="Annotation inventory")
    parser.add_argument("-f", "--force", action = "store_true",
        help = "Force removal")
    parser.add_argument("-C", "--nocoord", action = "store_true",
        help = "Druid: no use coordinator")
    parser.add_argument("--mongo", default = "",
        help = "Mongo name, default=name")
    parser.add_argument("--reportlines", type = int, default = 100,
        help = "Portion for report lines, default=100")
    parser.add_argument("name", nargs = 1, help = "Dataset name")
    run_args = parser.parse_args()

    ds_name =  run_args.name[0]
    config_file = run_args.config
    ds_source = run_args.source
    ds_inv = run_args.inv
    ds_kind = run_args.kind

    if run_args.dir is not None:
        if config_file or ds_source:
            print("Incorrect usage: use --dir or (--config, --source)")
            sys.exit()
        dir_config = json.loads(
            json_conf.readCommentedJSon(run_args.dir))
        config_file = dir_config["anfisa.json"]
        if ds_name not in dir_config["datasets"]:
            print("Dataset %s not registered in directory file (%s)" %
                (ds_name, run_args.dir), file = sys.stderr)
            sys.exit()
        ds_entry = dir_config["datasets"][ds_name]
        ds_kind = ds_entry["kind"]
        if "inv" in ds_entry and "a-json" not in ds_entry:
            ds_inv = ds_entry["inv"]
        elif "a-json" in ds_entry:
            ds_source = ds_entry["a-json"]
        else:
            print(("Dataset %s: no correct source or inv registered "
                "in directory file (%s)") % (ds_name, run_args.dir),
                file = sys.stderr)
            sys.exit()

    ds_inventory = None
    if ds_inv:
        if ds_source:
            print("Incorrect usage: use a-json or inventory "
                "(--source or --inv)")
            sys.exit()
        ds_inventory = json_conf.loadDatasetInventory(ds_inv)
        ds_source = ds_inventory["a-json"]

    print("Anfisa config:", config_file, file = sys.stderr)
    print("DS source:", ds_source, file = sys.stderr)

    if not config_file:
        config_file = "anfisa.json"
    app_config = json_conf.loadJSonConfig(config_file)

    assert os.path.isdir(app_config["data-vault"])

    if ds_kind == "xl" or run_args.mode == "druid-push":
        DRUID_ADM = DruidAdmin(app_config, run_args.nocoord)

    if run_args.mode == "druid-push":
        pushDruid(app_config, ds_name)
        sys.exit()

    if run_args.mode == "doc-push":
        pushDoc(app_config, ds_name, ds_inventory)
        sys.exit()

    if run_args.mode == "create":
        if run_args.force:
            dropDataSet(app_config, ds_name, ds_kind, True)
        time_start = datetime.now()
        print("Started at", time_start, file = sys.stderr)
        createDataSet(app_config, ds_name, ds_kind,
            run_args.mongo, ds_source, ds_inventory,
            run_args.reportlines, time_start.isoformat())
        time_done = datetime.now()
        print("Finished at", time_done, "for", (time_done - time_start),
            file = sys.stderr)
    elif run_args.mode == "drop":
        dropDataSet(app_config, ds_name, ds_kind, False)
    elif run_args.mode == "check":
        checkDataSet(app_config, ds_name, ds_kind)
    else:
        print("Bad mode:", run_args.mode)

#===============================================

