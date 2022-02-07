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
from io import StringIO

from forome_tools.read_json import JsonLineReader
from forome_tools.log_err import logException
from app.config.a_config import AnfisaConfig
from app.config.flt_schema import defineFilterSchema
from app.config.view_schema import defineViewSchema
from app.config.solutions import solutionsAreReady
from app.model.ds_disk import DataDiskStorageWriter
from .html_report import reportDS
from .doc_works import prepareDocDir
from .v_check import ViewDataChecker
from .trans_prep import TransformPreparator_WS, TransformPreparator_XL
#=====================================
def createDS(ds_dir, mongo_conn, druid_adm, ds_name, ds_source, ds_kind,
        ds_inv = None, report_lines = False,
        favor_storage = None, no_druid_push = False):
    assert solutionsAreReady()
    assert (ds_kind == "xl") == (druid_adm is not None)

    max_ds_name_length = AnfisaConfig.configOption("ds.name.max.length")
    if len(ds_name) > max_ds_name_length:
        logging.critical(
            "Attempt to create dataset with too long (%d+) name: %s"
            % (max_ds_name_length, ds_name))
        assert False

    time_start = datetime.now()
    logging.info("Dataset %s creation started at %s\tVersion: %s"
        % (ds_name, str(time_start), AnfisaConfig.getAnfisaVersion()))
    date_loaded = time_start.isoformat()

    if ds_source is not None:
        input_reader = JsonLineReader(ds_source)
        metadata_record = input_reader.readOne()
    else:
        metadata_record = favor_storage.getMetaData()
        input_reader = None

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

    if input_reader:
        if report_lines:
            print("Processing...", file = sys.stderr)

        if ds_kind == "ws":
            trans_prep = TransformPreparator_WS(
                filter_set.getTranscriptDescrSeq(),
                filter_set, True)
        else:
            trans_prep = TransformPreparator_XL(druid_adm)

        with DataDiskStorageWriter(True, ds_dir, filter_set, trans_prep,
                view_checker, report_lines) as ds_out:
            for record in input_reader:
                ds_out.saveRecord(record)
                if report_lines and ds_out.getTotal() % report_lines == 0:
                    sys.stderr.write("\r%d lines..." % ds_out.getTotal())
            total = ds_out.getTotal()
        input_reader.close()
        if report_lines:
            print("\nTotal lines: %d" % total, file = sys.stderr)
        trans_prep.finishUp()
    else:
        record = favor_storage.getRecordData(0)
        view_checker.regValue(0, record)
        total = metadata_record["variants"]

    rep_out = StringIO()
    is_ok = view_checker.finishUp(rep_out,
        no_mode = input_reader is None)
    is_ok &= filter_set.reportProblems(rep_out)

    flt_schema_data = filter_set.dump()
    if ds_kind == "xl" and input_reader:
        is_ok &= druid_adm.uploadDataset(ds_name, flt_schema_data,
            os.path.abspath(ds_dir + "/fdata.json.gz"),
            filter_set.getZygosityNames(),
            os.path.abspath(ds_dir + "/druid_rq.json"),
            no_druid_push = no_druid_push, rep_out = rep_out)

    if is_ok:
        try:
            ds_doc_dir = prepareDocDir(ds_dir + "/doc", ds_inv)
        except Exception:
            logException("Exception on documentation build\n"
                "Ignored in create process\n"
                "Use mode doc-push to repair documentation")
            ds_doc_dir = []
        ds_info = {
            "date_loaded": date_loaded,
            "doc": ds_doc_dir,
            "flt_schema": flt_schema_data,
            "kind": ds_kind,
            "meta": metadata_record,
            "modes": [],
            "mongo": ds_name,
            "name": ds_name,
            "root": ds_name,
            "zygosity_var": filter_set.getZygosityVarName(),
            "total": total,
            "view_schema": view_aspects.dump()}

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

    with open(ds_dir + "/create.log", "w", encoding = "utf-8") as outp:
        print(rep_out.getvalue(), file = outp)

    print(rep_out.getvalue())
    time_done = datetime.now()
    ok_status = "finished" if is_ok else "FAILED"
    logging.info("Dataset %s creation %s at %s for %s"
        % (ds_name, ok_status, str(time_done), str(time_done - time_start)))

#=====================================
def pushDruidDataset(ds_dir, druid_adm, ds_name):
    assert solutionsAreReady()
    with open(ds_dir + "/dsinfo.json",
            "r", encoding = "utf-8") as inp:
        ds_info = json.loads(inp.read())
    filter_set = defineFilterSchema(ds_info["meta"])

    return druid_adm.uploadDataset(ds_name,
        ds_info["flt_schema"],
        os.path.abspath(ds_dir + "/fdata.json.gz"),
        filter_set.getZygosityNames(),
        os.path.abspath(ds_dir + "/druid_rq.json"))

#=====================================
def portionFavorDruidPush(ds_dir, druid_adm, favor_storage, portion_no):
    assert solutionsAreReady()
    filter_set = defineFilterSchema(favor_storage.getMetaData())
    fdata_path = os.path.abspath(ds_dir + "/__fdata.json.gz")

    with gzip.open(fdata_path, "wt", encoding = "utf-8") as outp:
        for rec_no, record in favor_storage.loadRecords(portion_no):
            flt_data = filter_set.process(rec_no, record)
            flt_data.update(favor_storage.internalFltData(rec_no))
            print(json.dumps(flt_data, ensure_ascii = False), file = outp)

    flt_schema_data = filter_set.dump()

    report_fname = (os.path.abspath(ds_dir + "/druid_rq.json")
        if portion_no == 0 else None)

    druid_adm.uploadDataset("xl_FAVOR", flt_schema_data, fdata_path,
            filter_set.getZygosityNames(),
            report_fname = report_fname, portion_mode = True)
