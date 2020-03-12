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

from datetime import datetime, timedelta
from zlib import crc32

from utils.rest import RestAgent
#===============================================
class FavorStorage(RestAgent):
    def __init__(self, url, ds_h = None):
        RestAgent.__init__(self, url, "Favor", header_type = "www")
        self.mDS = ds_h

    def getKind(self):
        return "favor"

    def getMetaData(self):
        return self.call(None, "GET", "info")

    def getRecordData(self, rec_no):
        return self.call(None, "GET", "variant?ord=%d" % rec_no)

    FETCH_SIZE = 100
    def iterRecords(self, rec_no_set):
        rec_no_seq = rec_no_set[:]
        while len(rec_no_seq) > 0:
            seq_rec = self.call("seq=[%s]"
                % ','.join(map(str, rec_no_seq[:self.FETCH_SIZE])),
                "POST", "variants", json_rq_mode = False)
            for idx, rec_data in enumerate(seq_rec):
                yield rec_no_seq[idx], rec_data
            del rec_no_seq[:self.FETCH_SIZE]

    def collectPReports(self, rec_no_seq, notifier = None):
        seq_rec = self.call("seq=[%s]" % ','.join(map(str, rec_no_seq)),
            "POST", "titles", json_rq_mode = False)
        return {it_data["no"]: it_data for it_data in seq_rec}

    @classmethod
    def getRandNo(cls, rec_no):
        return crc32(bytes("Favor-%d" % rec_no, 'utf-8'))

#===============================================
class FavorStorageAgent(FavorStorage):
    TIME_START = datetime(year = 2015, month = 1, day = 1)

    def __init__(self, url, portion_size, portion_fetch):
        FavorStorage.__init__(self, url)
        self.mPortionSize = portion_size
        self.mPortionFetch = portion_fetch
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

    def loadRecords(self, portion_no, portion_fetch = None):
        if portion_fetch is None:
            portion_fetch = self.mPortionFetch
        start_no, end_no = self.getPortionDiap(portion_no)
        if portion_fetch < 2:
            for rec_no in range(start_no, end_no):
                yield rec_no, self.getRecordData(rec_no)
            return
        while start_no < end_no:
            seq_no = list(range(start_no,
                min(start_no + portion_fetch, end_no)))
            seq_rec = self.call("seq=[%s]" % ','.join(map(str, seq_no)),
                "POST", "variants", json_rq_mode = False)
            for rec_no, record in zip(seq_no, seq_rec):
                yield (rec_no, record)
            start_no = seq_no[-1] + 1

    def internalFltData(self, rec_no):
        portion_no = rec_no // self.mPortionSize
        dt = rec_no % self.mPortionSize
        return {
            "time": (self.TIME_START + timedelta(
                minutes = portion_no,
                microseconds = dt)).isoformat(),
            "_ord": rec_no,
            "_rand": self.getRandNo(rec_no)}
