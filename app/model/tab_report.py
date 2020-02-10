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

from utils.path_works import AttrFuncPool
#===============================================
class VariantsTabReportSchema:
    def __init__(self, name, use_tags = False):
        self.mName = name
        self.mFields = []
        self.mUseTags = use_tags

    def addField(self, name, field_path):
        self.mFields.append(PresentationFieldPath(name, field_path))

    def getName(self):
        return self.mName

    def reportRecord(self, ds_h, rec_no):
        rec_data = ds_h.getRecordData(rec_no)
        ret_handle = {"_no": rec_no}
        if self.mUseTags and ds_h.getDSKind() == "ws":
            ret_handle["_tags"] = ds_h.getTagsMan().makeRecReport(rec_no)

        for field_h in self.mFields:
            field_h.process(rec_data, ret_handle)
        return ret_handle

#===============================================
class PresentationFieldPath:
    def __init__(self, name, field_path):
        self.mName = name
        self.mFunc = AttrFuncPool.makeFunc(field_path)
        self.mIsSeq = field_path.endswith('[]')

    def process(self, rec_data, ret_handle):
        res = self.mFunc(rec_data)
        if not self.mIsSeq:
            res = res[0] if res else None
        ret_handle[self.mName] = res
