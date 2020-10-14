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
import csv
from io import StringIO

from forome_tools.path_works import AttrFuncHelper
#===============================================
class ReportTabSchema:
    def __init__(self, name, use_tags = False):
        self.mName = name
        self.mFields = []
        self.mUseTags = use_tags

    def addField(self, name, field_path):
        self.mFields.append((name,
            AttrFuncHelper.getter(field_path)))

    def addMustiStrField(self, name, separator, field_path_seq):
        self.mFields.append((name,
            AttrFuncHelper.multiStrGetter(separator, field_path_seq)))

    def getName(self):
        return self.mName

    def getFieldNames(self):
        ret = [name for name, _ in self.mFields]
        if self.mUseTags:
            ret.append("_tags")
        return ret

    def reportRecord(self, ds_h, rec_no):
        rec_data = ds_h.getRecordData(rec_no)
        ret_handle = {"_no": rec_no}
        if self.mUseTags:
            if ds_h.getDSKind() == "ws":
                ret_handle["_tags"] = (ds_h.getTagsMan().
                    makeRecReport(rec_no)["rec-tags"])
            else:
                ret_handle["_tags"] = None

        for name, field_f in self.mFields:
            ret_handle[name] = field_f(rec_data)
        return ret_handle

#===============================================
def reportCSV(ds_h, tab_schema, rec_no_seq):
    output = StringIO()
    writer = csv.writer(output)
    fld_names = tab_schema.getFieldNames()
    writer.writerow(fld_names)
    for rec_no in rec_no_seq:
        rec_descr = tab_schema.reportRecord(ds_h, rec_no)
        row = []
        for fld in fld_names:
            val = rec_descr[fld]
            if fld == "_tags":
                val = sorted(val.keys())
            if isinstance(val, list):
                row.append('|'.join(map(str, val)))
            else:
                row.append(str(val))
        writer.writerow(row)
    return output.getvalue()
