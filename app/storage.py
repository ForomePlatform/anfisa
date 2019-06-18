import sys, gzip, codecs, json, os, shutil, re
from argparse import ArgumentParser
from StringIO import StringIO
from datetime import datetime
from subprocess import Popen, PIPE

from utils.read_json import JsonLineReader
from utils.json_conf import loadJSonConfig
from app.model.pre_fields import PresentationData
from app.prepare.v_check import ViewDataChecker
from app.prepare.druid_adm import DruidAdmin
from app.config.flt_schema import defineFilterSchema
from app.config.view_schema import defineViewSchema
#=====================================
sys.stdin  = codecs.getreader('utf8')(sys.stdin)
sys.stderr = codecs.getwriter('utf8')(sys.stderr)
sys.stdout = codecs.getwriter('utf8')(sys.stdout)

DRUID_ADM = None

#===============================================
sID_Pattern = re.compile('^\\S+$', re.U)

def checkDSName(name, kind):
    global sID_Pattern
    if not sID_Pattern.match(name) or not name[0].isalpha():
        print >> sys.stderr, "Incorrect dataset name:", name
        assert False
    if kind == "ws":
        if name.lower().startswith("xl_"):
            print >> sys.stderr, "Improper WS name:", name
            print >> sys.stderr, "(Should not have prefix XL_)"
            assert False
    elif kind == "xl":
        if not name.lower().startswith("xl_"):
            print >> sys.stderr, "Improper XL-dataset name:", name
            print >> sys.stderr, "(Should have prefix XL_ or xl_)"
            assert False
    else:
        print >> sys.stderr, "Wrong dataset kind:", kind
        assert False

#===============================================
def createDataSet(app_config, name, kind, mongo, source, report_lines):
    global DRUID_ADM
    vault_dir = app_config["data-vault"]
    if not os.path.isdir(vault_dir):
        print >> sys.stderr, "No vault directory:", vault_dir
        assert False
    checkDSName(name, kind)
    ds_dir = vault_dir + "/" + name
    if not mongo:
        mongo = name
    if os.path.exists(ds_dir):
        print >> sys.stderr, "Dataset exists:", ds_dir
        assert False
    assert (kind == "xl") == (DRUID_ADM is not None)
    os.mkdir(ds_dir)

    post_proc = None
    view_aspects = defineViewSchema()
    view_checker = ViewDataChecker(view_aspects)
    filter_set = defineFilterSchema()

    if report_lines:
        print >> sys.stderr, "Processing..."

    data_rec_no = 0
    metadata_record = None

    vdata_out = Popen(sys.executable + " -m utils.ixbz2 --calm -o " +
        ds_dir + "/vdata.ixbz2 /dev/stdin", shell = True,
        stdin = PIPE, stderr = PIPE,
        bufsize = 1, universal_newlines = True, # line buffer
        close_fds = True)

    with    gzip.open(ds_dir + "/fdata.json.gz", 'wb') as fdata_out, \
            gzip.open(ds_dir + "/pdata.json.gz", 'wb') as pdata_out, \
            JsonLineReader(source) as input:
        for inp_rec_no, record in enumerate(input):
            if post_proc is not None:
                post_proc.transform(inp_rec_no, record)
            if record.get("record_type") == "metadata":
                assert inp_rec_no == 0
                metadata_record = record
                filter_set.setMeta(metadata_record)
                continue
            flt_data = filter_set.process(data_rec_no, record)
            view_checker.regValue(data_rec_no, record)
            print >> vdata_out.stdin, (
                json.dumps(record, ensure_ascii = False).encode("utf-8"))
            pre_data = PresentationData.make(record)
            if DRUID_ADM is not None:
                DRUID_ADM.addFieldsToRec(flt_data, pre_data, data_rec_no)
            print >> fdata_out, json.dumps(flt_data, ensure_ascii = False)
            print >> pdata_out, json.dumps(pre_data, ensure_ascii = False)
            data_rec_no += 1
            if report_lines and data_rec_no % report_lines == 0:
                print >> sys.stderr, "\r%d lines..." % data_rec_no,
    if report_lines:
        print >> sys.stderr, "\nTotal lines: %d" % data_rec_no

    _, vreport_data = vdata_out.communicate()
    for line in vreport_data.splitlines():
        print >> sys.stderr, line
    vdata_out.wait()

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
            "total": data_rec_no,
            "mongo": mongo,
            "family": filter_set.getFamilyInfo().dump(),
            "meta": metadata_record}
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
if __name__ == '__main__':
    parser = ArgumentParser()
    parser.add_argument("-c", "--config", default = "anfisa.json",
        help = "Configuration file,  default=anfisa.json")
    parser.add_argument("-m", "--mode",
        help = "Mode: create/drop")
    parser.add_argument("-k", "--kind",  default = "ws",
        help = "Kind of dataset: ws/xl, default=ws")
    parser.add_argument("-s", "--source", help="Annotated json")
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

    app_config = loadJSonConfig(run_args.config)

    assert os.path.isdir(app_config["data-vault"])

    if run_args.kind == "xl":
        DRUID_ADM = DruidAdmin(app_config, run_args.nocoord)

    if run_args.mode == "create":
        if run_args.force:
            dropDataSet(app_config, run_args.name[0],
                run_args.kind, True)
        time_start = datetime.now()
        print >> sys.stderr, "Started at", time_start
        createDataSet(app_config, run_args.name[0], run_args.kind,
            run_args.mongo, run_args.source, run_args.reportlines)
        time_done = datetime.now()
        print >> sys.stderr, "Finished at", time_done, "for", \
            (time_done - time_start)
    elif run_args.mode == "drop":
        dropDataSet(app_config, run_args.name[0], run_args.kind, False)
    elif run_args.mode == "check":
        checkDataSet(app_config, run_args.name[0], run_args.kind)
    else:
        print >> sys.stderr, "Bad mode:", run_args.mode

#===============================================

