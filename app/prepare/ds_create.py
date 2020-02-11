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
import sys, os, logging, json, gzip
from datetime import datetime
from io import StringIO, TextIOWrapper
from subprocess import Popen, PIPE

from utils.read_json import JsonLineReader
from app.config.a_config import AnfisaConfig
from app.config.flt_schema import defineFilterSchema
from app.config.view_schema import defineViewSchema
from app.config.solutions import readySolutions
from app.model.pre_fields import PresentationData
from .html_report import reportDS
from .doc_works import prepareDocDir
from .v_check import ViewDataChecker
from .trans_prep import TransformPreparator
#=====================================
def createDS(ds_dir, mongo_conn, druid_adm,
        ds_name, ds_source, ds_kind, ds_inv = None, report_lines = False):
    readySolutions()

    time_start = datetime.now()
    logging.info("Dataset %s creation started at %s\tVersion: %s"
        % (ds_name, str(time_start), AnfisaConfig.getAnfisaVersion()))
    date_loaded = time_start.isoformat()

    input_reader = JsonLineReader(ds_source)
    metadata_record = input_reader.readOne()
    if metadata_record.get("record_type") != "metadata":
        logging.critical("No metadata line in %s" % ds_source)
        assert False

    if "versions" in metadata_record:
        annotation_version = metadata_record["versions"].get("annotations")
        if annotation_version:
            ver = map(int, annotation_version.split('.'))
            if list(ver) < [0,  6]:
                logging.critical(
                    "Annotation version not supported (0.6.* expected): %s"
                    % annotation_version)
                assert False
        metadata_record["versions"][
            "Anfisa load"] = AnfisaConfig.getAnfisaVersion()

    view_aspects = defineViewSchema(metadata_record)
    view_checker = ViewDataChecker(view_aspects)
    filter_set = defineFilterSchema(metadata_record)

    if ds_kind == "ws":
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
            if druid_adm is not None:
                druid_adm.addFieldsToRec(flt_data, pre_data, data_rec_no)
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
    if report_lines:
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
    if ds_kind == "xl":
        is_ok &= druid_adm.uploadDataset(ds_name, flt_schema_data,
            filter_set.getZygosityNames(),
            os.path.abspath(ds_dir + "/fdata.json.gz"),
            os.path.abspath(ds_dir + "/druid_rq.json"))

    if is_ok:
        ds_doc_dir = ds_dir + "/doc"
        ds_info = {
            "date_loaded": date_loaded,
            "doc": prepareDocDir(ds_doc_dir, ds_inv),
            "flt_schema": flt_schema_data,
            "kind": ds_kind,
            "meta": metadata_record,
            "modes": [],
            "mongo": ds_name,
            "name": ds_name,
            "root": ds_name,
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

        mongo_agent = mongo_conn.getDSAgent(ds_name, ds_kind)
        mongo_agent.updateCreationDate(date_loaded, ds_source)

        with open(ds_dir + "/doc/info.html", "w", encoding = "utf-8") as outp:
            reportDS(outp, ds_info, mongo_agent)

        with open(ds_dir + "/active", "w", encoding = "utf-8") as outp:
            print("", file = outp)
        print("Dataset %s kind=%s succesively created" % (
            ds_name, ds_kind), file = rep_out)
    else:
        print("Process terminated", file = rep_out)

    with open(ds_dir + "/create.log",
            "w", encoding = "utf-8") as outp:
        print(rep_out.getvalue(), file = outp)

    print(rep_out.getvalue())
    time_done = datetime.now()
    logging.info("Dataset %s creation finished at %s for %s"
        % (ds_name, str(time_done), str(time_done - time_start)))
