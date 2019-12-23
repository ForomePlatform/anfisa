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

from utils.log_err import logException
from .evaluation import Evaluation
from .code_repr import formatConditionCode

#===============================================
class FilterEval(Evaluation):
    def __init__(self, eval_space, cond_data, name = None,
            updated_time = None, updated_from = None):
        Evaluation.__init__(self, eval_space, updated_time, updated_from)
        self.mFilterName = name
        self.mBadIdxs = set()
        self.mCondData = cond_data
        self.mUsedOpUnits = set()
        self.mCondition = None
        hash_h = md5()
        for idx, cond_data in enumerate(self.mCondData):
            hash_h.update(bytes(json.dumps(cond_data) + "\n", 'utf-8'))
            if not self.validateCondData(cond_data, self.mUsedOpUnits):
                self.mBadIdxs.add(idx)
        self.mHashCode = hash_h.hexdigest()

    def activate(self):
        if self.mCondition is not None:
            return
        hash_h = md5()
        cond_seq = []
        for idx, cond_data in enumerate(self.mCondData):
            if idx in self.mBadIdxs:
                continue
            hash_h.update(bytes(json.dumps(cond_data) + "\n", 'utf-8'))
            if cond_data[0] == "import":
                self.importUnit(idx, cond_data[1],
                    self.getEvalSpace().joinAnd(cond_seq),
                    hash_h.hexdigest())
                continue
            try:
                cond_seq.append(self.parseCondData(cond_data))
            except Exception:
                logException("Bad instruction after validation: %r, ds=%s"
                    % (cond_data, self.getEvalSpace().getName()))
                self.mBadIdxs.add(idx)
        with self.getEvalSpace().getDS():
            self.mCondition = self.getEvalSpace().joinAnd(cond_seq)

    def getSolKind(self):
        return "filter"

    def noErrors(self):
        return len(self.mBadIdxs) == 0

    def getHashCode(self):
        return self.mHashCode

    def isActive(self):
        return self.mCondition is not None

    def getFilterName(self):
        return self.mFilterName

    def getPresentation(self):
        return [formatConditionCode(instr) for instr in self.mCondData]

    def getCondition(self):
        return self.mCondition

    def getCondData(self):
        return self.mCondData

    def reportInfo(self):
        return {
            "conditions": self.mCondData,
            "bad-idxs": sorted(self.mBadIdxs),
            "hash": self.mHashCode}
