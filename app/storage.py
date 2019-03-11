import sys, gzip, bz2, codecs, json, os, shutil
from glob import glob
from argparse import ArgumentParser
from StringIO import StringIO
from datetime import datetime

from ixbz2.ixbz2 import FormatterIndexBZ2
from app.model.json_conf import loadJSonConfig
from app.model.pre_fields import PresentationData
from app.prepare.v_check import ViewDataChecker
from app.prepare.view_schema import defineViewSchema
from app.prepare.flt_schema import defineFilterSchema
from app.prepare.druid_adm import DruidAdmin
#=====================================
sys.stdin  = codecs.getreader('utf8')(sys.stdin)
sys.stderr = codecs.getwriter('utf8')(sys.stderr)
sys.stdout = codecs.getwriter('utf8')(sys.stdout)

DRUID_ADM = None
#===============================================
def createDataSet(app_config, name, kind, mongo, source, report_lines):
    global DRUID_ADM
    vault_dir = app_config["data-vault"]
    if not os.path.isdir(vault_dir):
        print >> sys.stderr, "No vault directory:", vault_dir
        assert False
    ds_dir = vault_dir + "/" + name
    if not mongo:
        mongo = name
    if kind not in ("ws", "xl"):
        print >> sys.stderr, "Wrong dataset kind:", kind
        assert False
    if os.path.exists(ds_dir):
        print >> sys.stderr, "Dataset exists:", ds_dir
        assert False
    assert (kind == "xl") == (DRUID_ADM is not None)
    os.mkdir(ds_dir)

    view_aspects = defineViewSchema()
    view_checker = ViewDataChecker(view_aspects)
    filter_set = defineFilterSchema()

    if report_lines:
        print >> sys.stderr, "Processing..."

    rec_no = 0
    fdata_out = gzip.open(ds_dir + "/fdata.json.gz", 'wb')
    pdata_out = gzip.open(ds_dir + "/pdata.json.gz", 'wb')
    with FormatterIndexBZ2(ds_dir + "/vdata.ixbz2") as vdata_out:
        for record in readJSonRecords(source):
            view_checker.regValue(rec_no, record)
            vdata_out.putLine(json.dumps(record, ensure_ascii = False))
            flt_data = filter_set.process(rec_no, record)
            pre_data = PresentationData.make(record)
            if DRUID_ADM is not None:
                DRUID_ADM.addFieldsToRec(flt_data, pre_data, rec_no)
            print >> fdata_out, json.dumps(flt_data, ensure_ascii = False)
            print >> pdata_out, json.dumps(pre_data, ensure_ascii = False)
            rec_no += 1
            if report_lines and rec_no % report_lines == 0:
                print >> sys.stderr, "\r%d lines..." % rec_no,
    if report_lines:
        print >> sys.stderr, "\nTotal lines: %d" % rec_no
    fdata_out.close()
    pdata_out.close()

    rep_out = StringIO()
    is_ok = view_checker.finishUp(rep_out)
    is_ok &= filter_set.reportProblems(rep_out)

    flt_data = filter_set.dump()
    if kind == "xl":
        is_ok &= DRUID_ADM.uploadDataset(name, flt_data,
            os.path.abspath(ds_dir + "/fdata.json.gz"),
            os.path.abspath(ds_dir + "/druid_rq.json"))

    if is_ok:
        ds_info = {
            "name": name,
            "kind": kind,
            "view_schema": view_aspects.dump(),
            "flt_schema": flt_data,
            "total": rec_no,
            "mongo": mongo}
        with codecs.open(ds_dir + "/dsinfo.json",
                "w", encoding = "utf-8") as outp:
            print >> outp, json.dumps(ds_info,
                sort_keys = True, indent = 4)

        with codecs.open(ds_dir + "/stat.json",
                "w", encoding = "utf-8") as outp:
            print >> outp, json.dumps(view_checker.dump(),
                sort_keys = True, indent = 4)

        with codecs.open(ds_dir + "/active",
                "w", encoding = "utf-8") as outp:
            print >> outp, ""
        print >> rep_out, "Dataset %s kind=%s succesively created" % (
            name, kind)
    else:
        print >> rep_out, "Process terminated"

    with codecs.open(ds_dir + "/create.log",
            "w", encoding = "utf-8") as outp:
        print >> outp, rep_out.getvalue()

    print >> sys.stdout, rep_out.getvalue()

#===============================================
def dropDataSet(app_config, name, kind, calm_mode):
    global DRUID_ADM
    assert kind in ("ws", "xl")
    assert (kind == "xl") == (DRUID_ADM is not None)
    vault_dir = app_config["data-vault"]
    ds_dir = vault_dir + "/" + name

    if kind == "xl":
        if calm_mode:
            druid_datasets = DRUID_ADM.listDatasets()
        else:
            druid_datasets = [name]
        if name in druid_datasets:
            DRUID_ADM.dropDataset(name)
        elif not calm_mode:
            print >> sys.stdout, "No dataset in Druid to drop:", name

    if not os.path.exists(ds_dir):
        if not calm_mode:
            print >> sys.stdout, "No dataset to drop:", ds_dir
        return
    shutil.rmtree(ds_dir)
    print >> sys.stdout, "Dataset droped:", ds_dir

#===============================================
def checkDataSet(app_config, name, kind):
    global DRUID_ADM
    assert kind == "ws"
    vault_dir = app_config["data-vault"]
    ds_dir = vault_dir + "/" + name

    print >> sys.stdout, "Check", ds_dir, ":", \
        os.path.exists(ds_dir), os.path.exists(ds_dir + "/active")

#===============================================
def readJSonRecords(src):
    if '*' in src:
        names = sorted(glob(src))
    else:
        names = [src]
    for nm in names:
        if nm.endswith('.gz'):
            with gzip.open(nm, 'rb') as inp:
                for line in inp:
                    yield json.loads(line.decode('utf-8'))
        elif nm.endswith('.bz2'):
            with bz2.BZ2File(nm, 'rb') as inp:
                for line in inp:
                    yield json.loads(line.decode('utf-8'))
        else:
            with codecs.open(nm, 'r', encoding = 'utf-8') as inp:
                for line in inp:
                    yield json.loads(line)

#===============================================
parser = ArgumentParser()
parser.add_argument("-c", "--config", default = "anfisa.json",
    help = "Configuration file (anfisa.json)")
parser.add_argument("-k", "--kind",  default = "ws",
    help = "Kind of dataset")
parser.add_argument("-s", "--source", help="Annotrated json")
parser.add_argument("-f", "--force", action = "store_true",
    help = "Force removal")
parser.add_argument("-C", "--nocoord", action = "store_true",
    help = "Druid: no use coordinator")
parser.add_argument("-m", "--mode",
    help = "Mode: create/drop/check")
parser.add_argument("--mongo", default = "",
    help = "Mongo name, by default = name")
parser.add_argument("--reportlines", type = int, default = 100,
    help = "Portion for report lines")
parser.add_argument("name", nargs = 1, help = "Dataset name")
run_args = parser.parse_args()

app_config = loadJSonConfig(run_args.config)

assert os.path.isdir(app_config["data-vault"])

if run_args.kind == "xl":
    DRUID_ADM = DruidAdmin(app_config, run_args.nocoord)

if run_args.mode == "create":
    if run_args.force:
        dropDataSet(app_config, run_args.name[0],
            run_args.kind, True)
    print >> sys.stderr, "Started at", datetime.now()
    createDataSet(app_config, run_args.name[0], run_args.kind,
        run_args.mongo, run_args.source, run_args.reportlines)
    print >> sys.stderr, "Finished at", datetime.now()
elif run_args.mode == "drop":
    dropDataSet(app_config, run_args.name[0], run_args.kind, False)
elif run_args.mode == "check":
    checkDataSet(app_config, run_args.name[0], run_args.kind)
else:
    print >> sys.stderr, "Bad mode:", run_args.mode

#===============================================

