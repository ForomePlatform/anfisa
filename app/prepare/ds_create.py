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

from utils.read_json import JsonLineReader
from app.config.a_config import AnfisaConfig
from app.config.flt_schema import defineFilterSchema
from app.config.view_schema import defineViewSchema
from app.config.solutions import readySolutions
from app.model.pre_fields import PresentationData
from app.model.ds_disk import DataDiskStorageWriter
from .html_report import reportDS
from .doc_works import prepareDocDir
from .v_check import ViewDataChecker
from .trans_prep import TransformPreparator
#=====================================
def createDS(ds_dir, mongo_conn, druid_adm, ds_name, ds_source, ds_kind,
        ds_inv = None, report_lines = False, favor_storage = None):
    readySolutions()

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

    if ds_kind == "ws":
        trans_prep = TransformPreparator(
            filter_set.getTranscriptDescrSeq(), True)
    else:
        trans_prep = None

    if input_reader:
        if report_lines:
            print("Processing...", file = sys.stderr)

        with DataDiskStorageWriter(ds_dir, report_lines) as ds_out:
            for rec_no, record in enumerate(input_reader):
                flt_data = filter_set.process(rec_no, record)
                view_checker.regValue(rec_no, record)
                pre_data = PresentationData.make(record)
                if druid_adm is not None:
                    flt_data.update(
                        druid_adm.internalFltData(rec_no, pre_data))
                if trans_prep is not None:
                    trans_prep.doRec(record, flt_data)
                ds_out.putRecord(record, flt_data, pre_data)
                if report_lines and rec_no % report_lines == 0:
                    sys.stderr.write("\r%d lines..." % rec_no)
            total = ds_out.getTotal()
        if report_lines:
            print("\nTotal lines: %d" % total, file = sys.stderr)
        input_reader.close()
    else:
        total = metadata_record["variants"]

    rep_out = StringIO()
    is_ok = view_checker.finishUp(rep_out)
    is_ok &= filter_set.reportProblems(rep_out)

    if trans_prep is not None:
        total_item_count = trans_prep.finishUp()
    else:
        total_item_count = None

    flt_schema_data = filter_set.dump()
    if ds_kind == "xl" and input_reader:
        is_ok &= druid_adm.uploadDataset(ds_name, flt_schema_data,
            os.path.abspath(ds_dir + "/fdata.json.gz"),
            filter_set.getZygosityNames(),
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
            "total": total,
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

    with open(ds_dir + "/create.log", "w", encoding = "utf-8") as outp:
        print(rep_out.getvalue(), file = outp)

    print(rep_out.getvalue())
    time_done = datetime.now()
    logging.info("Dataset %s creation finished at %s for %s"
        % (ds_name, str(time_done), str(time_done - time_start)))

#=====================================
def portionFavorDruidPush(ds_dir, druid_adm, favor_storage, portion_no):
    readySolutions()
    filter_set = defineFilterSchema(favor_storage.getMetaData())
    fdata_path = os.path.abspath(ds_dir + "/__fdata.json.gz")

    with gzip.open(fdata_path, "wt", encoding = "utf-8") as outp:
        for rec_no in range(*favor_storage.getPortionDiap(portion_no)):
            record = favor_storage.getRecordData(rec_no)
            flt_data = filter_set.process(rec_no, record)
            flt_data.update(favor_storage.internalFltData(rec_no))
            print(json.dumps(flt_data, ensure_ascii = False), file = outp)

    flt_schema_data = filter_set.dump()
    druid_adm.uploadDataset("xl_FAVOR", flt_schema_data, fdata_path,
            filter_set.getZygosityNames(), portion_mode = True)
