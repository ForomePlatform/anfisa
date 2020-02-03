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

import sys, gzip, codecs, json, os, shutil, re,  time
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
from app.prepare.trans_prep import TransformPreparator
from app.config.a_config import AnfisaConfig
from app.config.flt_schema import defineFilterSchema
from app.config.view_schema import defineViewSchema
from app.config.solutions import readySolutions
from app.model.mongo_db import MongoConnector
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

#========================================
DRUID_ADM = None

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
def createDataSet(app_config, ds_entry, force_drop, report_lines):
    global DRUID_ADM
    readySolutions()

    if not ds_entry.getSource():
        print("Improper creation datset",  ds_entry.getName(),  ": no source")
        sys.exit()

    time_start = datetime.now()
    print("Dataset", ds_entry.getName(),
        "creation started at", time_start,
        "\tVersion: ", AnfisaConfig.getAnfisaVersion(),
        file = sys.stderr)
    date_loaded = time_start.isoformat()

    input_reader = JsonLineReader(ds_entry.getSource())
    metadata_record = input_reader.readOne()
    if metadata_record.get("record_type") != "metadata":
        print("No metadata line in", ds_entry.getSource(), file = sys.stderr)
        assert False

    if "versions" in metadata_record:
        annotation_version = metadata_record["versions"].get("annotations")
        if annotation_version:
            ver = map(int, annotation_version.split('.'))
            if list(ver) < [0,  6]:
                print("Annotation version not supported (0.6.* expected):",
                    annotation_version, file = sys.stderr)
                assert False
        metadata_record["versions"][
            "Anfisa load"] = AnfisaConfig.getAnfisaVersion()

    vault_dir = app_config["data-vault"]
    if force_drop:
        dropDataSet(app_config, ds_entry, True)

    if not os.path.isdir(vault_dir):
        os.mkdir(vault_dir)
        print("Create (empty) vault directory:", vault_dir, file = sys.stderr)

    checkDSName(ds_entry.getName(), ds_entry.getDSKind())
    ds_dir = os.path.abspath(vault_dir + "/" + ds_entry.getName())
    if os.path.exists(ds_dir):
        print("Dataset exists:", ds_dir, file = sys.stderr)
        assert False
    if ds_entry.getDSKind() == "xl":
        assert DRUID_ADM is not None
    os.mkdir(ds_dir)

    view_aspects = defineViewSchema(metadata_record)
    view_checker = ViewDataChecker(view_aspects)
    filter_set = defineFilterSchema(metadata_record)

    if ds_entry.getDSKind() == "ws":
        trans_prep = TransformPreparator(
            filter_set.getTranscriptDescrSeq(), True)
    else:
        trans_prep = None

    if report_lines:
        print("Processing...", file = sys.stderr)

    data_rec_no = 0

    vdata_out = Popen(sys.executable + " -m utils.ixbz2 --calm -o "
        + ds_dir + "/vdata.ixbz2 /dev/stdin", shell = True,
        stdin = PIPE, stderr = PIPE,
        bufsize = 1, universal_newlines = False,
        close_fds = True)

    vdata_stdin = TextIOWrapper(vdata_out.stdin, encoding = "utf-8",
        line_buffering = True)

    with gzip.open(ds_dir + "/fdata.json.gz", 'wb') as fdata_stream, \
            gzip.open(ds_dir + "/pdata.json.gz", 'wb') as pdata_stream:
        fdata_out = TextIOWrapper(fdata_stream,
            encoding = "utf-8", line_buffering = True)
        pdata_out = TextIOWrapper(pdata_stream,
            encoding = "utf-8", line_buffering = True)
        for record in input_reader:
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
        print("\nTotal lines: %d" % input_reader.getCurLineNo(),
            file = sys.stderr)
    input_reader.close()

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
    if ds_entry.getDSKind() == "xl":
        is_ok &= DRUID_ADM.uploadDataset(ds_entry.getName(), flt_schema_data,
            filter_set.getZygosityNames(),
            os.path.abspath(ds_dir + "/fdata.json.gz"),
            os.path.abspath(ds_dir + "/druid_rq.json"))

    if is_ok:
        ds_doc_dir = ds_dir + "/doc"
        ds_info = {
            "date_loaded": date_loaded,
            "doc": prepareDocDir(ds_doc_dir, ds_entry.getInv()),
            "flt_schema": flt_schema_data,
            "kind": ds_entry.getDSKind(),
            "meta": metadata_record,
            "modes": [],
            "mongo": ds_entry.getName(),
            "name": ds_entry.getName(),
            "root": ds_entry.getName(),
            "zygosity_var": filter_set.getZygosityVarName(),
            "total": data_rec_no,
            "view_schema": view_aspects.dump()}

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
        mongo_agent = mongo_conn.getDSAgent(
            ds_entry.getName(), ds_entry.getDSKind())
        mongo_agent.checkCreationDate(date_loaded, ds_entry.getSource())

        with open(ds_dir + "/doc/info.html", "w", encoding = "utf-8") as outp:
            reportDS(outp, ds_info, mongo_agent)

        with open(ds_dir + "/active", "w", encoding = "utf-8") as outp:
            print("", file = outp)
        print("Dataset %s kind=%s succesively created" % (
            ds_entry.getName(), ds_entry.getDSKind()), file = rep_out)
    else:
        print("Process terminated", file = rep_out)

    with open(ds_dir + "/create.log",
            "w", encoding = "utf-8") as outp:
        print(rep_out.getvalue(), file = outp)

    print(rep_out.getvalue())
    time_done = datetime.now()
    print("Dataset", ds_entry.getName(),
        "creation finished at", time_done, "for",
        (time_done - time_start), file = sys.stderr)

#===============================================
def pushDruid(app_config, ds_entry):
    global DRUID_ADM
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

    druid_datasets = DRUID_ADM.listDatasets()
    if ds_entry.getName() in druid_datasets:
        DRUID_ADM.dropDataset(ds_entry.getName())

    ds_dir = os.path.abspath(vault_dir + "/" + ds_entry.getName())
    with open(ds_dir + "/dsinfo.json",
            "r", encoding = "utf-8") as inp:
        ds_info = json.loads(inp.read())
    is_ok = DRUID_ADM.uploadDataset(ds_entry.getName(),
        ds_info["flt_schema"],
        os.path.abspath(ds_dir + "/fdata.json.gz"),
        os.path.abspath(ds_dir + "/druid_rq.json"))
    if is_ok:
        print("Druid dataset %s pushed" % ds_entry.getName())
    else:
        print("Process failed")

#===============================================
def dropDataSet(app_config, ds_entry, calm_mode):
    global DRUID_ADM
    assert ds_entry.getDSKind() in ("ws", "xl")
    if ds_entry.getDSKind() == "xl":
        assert DRUID_ADM is not None
    vault_dir = app_config["data-vault"]
    ds_dir = os.path.abspath(vault_dir + "/" + ds_entry.getName())

    if ds_entry.getDSKind() == "xl":
        if calm_mode:
            druid_datasets = DRUID_ADM.listDatasets()
        else:
            druid_datasets = [ds_entry.getName()]
        if ds_entry.getName() in druid_datasets:
            DRUID_ADM.dropDataset(ds_entry.getName())
        elif not calm_mode:
            print("No dataset in Druid to drop:", ds_entry.getName())

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
    parser = ArgumentParser()
    parser.add_argument("-d", "--dir",
        help = "Storage directory control file")
    parser.add_argument("-c", "--config",
        help = "Anfisa configuration file, used only if --dir is unset, "
        "default = anfisa.json")
    parser.add_argument("-m", "--mode",
        help = "Mode: create/drop/druid-push/doc-push")
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

    if any(ds_entry.getDSKind() == "xl" for ds_entry in entries):
        DRUID_ADM = DruidAdmin(app_config, args.nocoord)

    for entry_no,  ds_entry in enumerate(entries):
        if entry_no > 0 and args.delay > 0:
            time.sleep(args.delay)
        if args.mode == "create":
            createDataSet(app_config, ds_entry, args.force, args.reportlines)
        elif args.mode == "drop":
            dropDataSet(app_config, ds_entry, False)
        elif args.mode == "druid-push":
            pushDruid(app_config, ds_entry)
        elif args.mode == "doc-push":
            pushDoc(app_config, ds_entry)
        elif args.mode == "debug-info":
            print("Info:", json.dumps(
                ds_entry.dump(), indent = 4, sort_keys = True))
        else:
            print("Bad mode:", args.mode)
            sys.exit()

#===============================================
