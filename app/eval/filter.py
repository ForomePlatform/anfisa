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

from forome_tools.log_err import logException
from .evaluation import Evaluation
from .condition import validateCondition, condDataUnits
from .code_repr import formatConditionCode

#===============================================
class FilterEval(Evaluation):
    def __init__(self, eval_space, cond_data_seq, name = None,
            updated_time = None, updated_from = None):
        Evaluation.__init__(self, eval_space,
            md5(bytes(json.dumps(cond_data_seq, sort_keys = True),
                encoding = "utf-8")).hexdigest(),
            updated_time, updated_from)
        self.mFilterName = name
        self.mCondDataSeq = cond_data_seq
        self.mPresentation = []
        self.mConditions = None
        self.mOperationErrors = None
        for idx, cond_data in enumerate(cond_data_seq):
            err_msg = validateCondition(cond_data)
            if err_msg:
                self.pointError(err_msg, point_no = idx)
                self.mPresentation.append("#? "
                    + json.dumps(cond_data, sort_keys = True))
            else:
                self.mPresentation.append(formatConditionCode(cond_data))
        self.mCondition = None

    def activate(self):
        if self.mConditions is not None:
            return
        self.mConditions = []
        self.mOperationErrors = dict()
        for idx, cond_data in enumerate(self.mCondDataSeq):
            if self.getPointError(idx) is not None:
                self.mConditions.append(self.getEvalSpace().getCondAll())
                continue
            self.runNextPoint(idx)
            try:
                cond = self.buildCondition(cond_data)
            except Exception:
                logException("On build condition: "
                    + json.dumps(cond_data, sort_keys = True))
                self.pointError("Runtime error")
                cond = None
            if cond is None:
                assert self.getPointError(idx) is not None
                self.mConditions.append(self.getEvalSpace().getCondAll())
            else:
                assert self.getPointError(idx) is None
                self.mConditions.append(cond)
        self.finishRuntime()
        self.mCondition = self.getEvalSpace().joinAnd(self.mConditions)

    def operationError(self, cond_data, err_msg):
        Evaluation.operationError(self, cond_data, err_msg)
        assert cond_data is self.mCondDataSeq[self.getCurPointNo()]
        self.mOperationErrors[self.getCurPointNo()] = err_msg

    def locateCondData(self, the_cond_data):
        for idx, cond_data in enumerate(self.mCondDataSeq):
            if the_cond_data is cond_data:
                return idx, self.mOperationErrors.get(idx)
        assert False, "Condition not found: " + json.dumps(the_cond_data,
            sort_keys = True)
        return None

    def getSolKind(self):
        return "filter"

    def isActive(self):
        return self.mConditions is not None

    def getFilterName(self):
        return self.mFilterName

    def getCondition(self):
        return self.mCondition

    def getCondDataSeq(self):
        return self.mCondDataSeq

    def getActualCondition(self, point_no):
        if point_no is None:
            point_no = len(self.mConditions)
        assert point_no <= len(self.mConditions), (
            f"Improper point no: {point_no}, pcount={len(self.mConditions)}")
        return self.getEvalSpace().joinAnd(self.mConditions[:point_no])

    def getPresentation(self):
        return self.mPresentation

    def visitAll(self, visitor):
        self.mCondition.visit(visitor)

    def reportInfo(self):
        cond_seq = []
        for idx, cond_data in enumerate(self.mCondDataSeq):
            cond_info = {"repr": self.mPresentation[idx]}
            err_msg = self.getPointError(idx)
            if err_msg:
                cond_info["err"] = err_msg
            else:
                cond_info["unit"] = cond_data[1]
                err_msg = self.mOperationErrors.get(idx)
                if err_msg:
                    cond_info["err"] = err_msg
            cond_seq.append(cond_info)
        return {
            "conditions": self.mCondDataSeq,
            "cond-seq": cond_seq,
            "eval-status": self.getEvalStatus(),
            "hash": self.mHashCode}

    def getActiveUnitSet(self):
        ret = set()
        for cond_data in self.mCondDataSeq:
            ret |= condDataUnits(cond_data)
        return ret
