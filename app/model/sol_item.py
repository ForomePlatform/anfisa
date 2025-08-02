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

import json
from hashlib import md5

#===============================================
class SolItem:
    @classmethod
    def create(cls, kind, name, data, rubric=None,
            upd_time=None, upd_from=None,
            used_names=None, requires=None, is_std=None, use_hash=True):
        if used_names is not None:
            assert name not in used_names, "Name duplication " + name
            used_names.add(name)
        kind = cls.normKind(kind)
        descr = {"_tp": kind, "name": name, "data": data}
        for key, val in [("rubric", rubric), ("is_std", is_std),
                ("req", requires), ("time", upd_time), ("from", upd_from)]:
            if val is not None:
                descr[key] = val
        return cls(descr, use_hash=use_hash)

    @staticmethod
    def normKind(kind):
        return kind.replace('.', '_')

    def __init__(self, descr, use_hash=True):
        self.mDescr = descr
        assert "data" in self.mDescr
        self.mHashCode = (self.formItemHashCode(self.mDescr["data"])
            if use_hash else None)

    def getDescr(self):
        return self.mDescr

    def getData(self):
        return self.mDescr["data"]

    def getSolKind(self):
        return self.mDescr["_tp"]

    def getName(self):
        return self.mDescr["name"]

    def getRubric(self):
        return self.mDescr.get("rubric")

    def getHashCode(self):
        return self.mHashCode

    def getUpdateInfo(self):
        return [self.mHashCode,
            self.mDescr.get("time"), self.mDescr.get("from")]

    def get(self, key):
        return self.mDescr.get(key)

    @staticmethod
    def formItemHashCode(data):
        buf = json.dumps(data, sort_keys=True, ensure_ascii=False)
        return md5(bytes(buf, encoding = "utf-8")).hexdigest()
