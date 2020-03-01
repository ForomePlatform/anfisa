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

import json
from datetime import datetime, timedelta
from zlib import crc32

from utils.rest import RestAgent
#===============================================
class FavorStorage(RestAgent):
    def __init__(self, url, ds_h = None):
        RestAgent.__init__(url, "Favor")
        self.mDS = ds_h

    def hasFullSupport(self):
        return False

    def getMetaData(self):
        content = self.call("info", None, "GET")
        return json.loads(content)

    def getRecordData(self, rec_no):
        content = self.call("variant?ord=%d" % rec_no, None, "GET")
        return json.loads(content)

    @classmethod
    def getRandNo(cls, rec_no):
        return crc32(bytes("Favor-%d" % rec_no, 'utf-8'))

#===============================================
class FavorStorageAgent(FavorStorage):
    TIME_START = datetime(year = 2015, month = 1, day = 1)

    def __init__(self, url, portion_size, portion_min_delta):
        FavorStorage.__init__(url)
        self.mPortionSize = portion_size
        self.mPortionMinDelta = portion_min_delta
        self.mMetaData = FavorStorage.getMetaData(self)
        self.mTotal = self.mMetaData["variants"]
        self.mPortionCount = self.mTotal // self.mPortionSize

    def getMetaData(self):
        return self.mMetaData

    def getTotal(self):
        return self.mTotal

    def getPortionCount(self):
        return self.mPortionCount

    def getPortionDiap(self, portion_no):
        start = self.mPortionSize * portion_no
        assert start < self.mTotal
        return (start, min(self.mTotal, start + self.mPortionSize))

    def internalFltData(self, rec_no):
        portion_no = rec_no // self.mPortionSize
        dt = rec_no % self.mPortionSize
        return {
            "time": (self.TIME_START + timedelta(
                minutes = portion_no * self.mPortionMinDelta,
                microseconds = dt)).isoformat(),
            "_ord": rec_no,
            "_rand": self.getRandNo(rec_no)}
