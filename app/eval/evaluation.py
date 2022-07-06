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
import abc, json
from .visitor import EnumUnitConditionVisitor

#===============================================
class Evaluation:
    def __init__(self, eval_space, hash_code,
            updated_time = None, updated_from = None):
        self.mEvalSpace = eval_space
        self.mHashCode = hash_code
        self.mUpdatedInfo = [updated_time, updated_from]
        self.mPointNo = 0
        self.mLabels = dict()
        self.mErrors = dict()
        self.mEvalStatus = "ok"

    def getEvalSpace(self):
        return self.mEvalSpace

    def getUpdateInfo(self):
        return self.mUpdatedInfo

    def getHashCode(self):
        return self.mHashCode

    def getLabelCondition(self, label, point_no):
        if label not in self.mLabels or self.mLabels[label] > point_no:
            return None
        return self.getActualCondition(self.mLabels[label])

    def getLabelPoints(self, point_no = None):
        ret = []
        for label, p_no in self.mLabels.items():
            if point_no is None or p_no <= point_no:
                ret.append(label)
        return sorted(ret)

    def getPointError(self, point_no):
        if point_no in self.mErrors:
            return self.mErrors[point_no]
        return None

    def getEvalStatus(self):
        return self.mEvalStatus

    @abc.abstractmethod
    def getSolKind(self):
        return None

    @abc.abstractmethod
    def isActive(self):
        assert False
        return False

    @abc.abstractmethod
    def activate(self):
        assert False

    @abc.abstractmethod
    def getActualCondition(self, point_no):
        assert False

    @abc.abstractmethod
    def getActiveUnitSet(self):
        assert False

    @abc.abstractmethod
    def visitAll(self, visitor):
        assert False

    def operationError(self, cond_data, err_msg):
        if self.mEvalStatus == "ok":
            self.mEvalStatus = "runtime"

    def getCurPointNo(self):
        return self.mPointNo

    def inRuntime(self):
        return self.mPointNo is not None

    def pointError(self, err_msg, point_no = None):
        if point_no is None:
            point_no = self.mPointNo
        assert point_no is not None
        assert point_no not in self.mErrors
        self.mEvalStatus = "fatal"
        self.mErrors[point_no] = err_msg

    def finishRuntime(self):
        assert self.mPointNo is not None
        self.mPointNo = None

    def runNextPoint(self, p_no = None, label = None):
        if p_no is None:
            self.mPointNo += 1
        else:
            assert p_no >= self.mPointNo, (
                f"Point order collision: {p_no} < {self.mPointNo}")
            self.mPointNo = p_no
        if label is not None:
            assert label not in self.mLabels, (
                "Label duplication: " + label)
            self.mLabels[label] = self.mPointNo

    def buildCondition(self, cond_data):
        if len(cond_data) == 0:
            return self.mEvalSpace.getCondAll()
        if cond_data[0] is None:
            assert len(cond_data) == 1, (
                "Bad None condition: " + json.dumps(cond_data))
            return self.mEvalSpace.getCondNone()
        if cond_data[0] == "error":
            return self.buildCondition(cond_data[1])
        if cond_data[0] in {"and", "or"}:
            seq = []
            for cc in cond_data[1:]:
                cond = self.buildCondition(cc)
                if cond is None:
                    return None
                seq.append(cond)
            if cond_data[0] == "and":
                return self.mEvalSpace.joinAnd(seq)
            else:
                return self.mEvalSpace.joinOr(seq)
        if cond_data[0] == "not":
            assert len(cond_data) == 2, (
                "Bad NOT condition: " + json.dumps(cond_data))
            cond = self.buildCondition(cond_data[1])
            if cond is None:
                return None
            return cond.negative()
        unit_h = self.mEvalSpace.getUnit(cond_data[1])
        if unit_h is None:
            self.pointError("Field nof found: %s" % cond_data[1])
            return None
        if unit_h.getUnitKind() != cond_data[0]:
            self.pointError("Field type conflict: %s/%s"
                % (cond_data[0], unit_h.getUnitKind()))
            return None
        if unit_h.getUnitKind() == "func":
            extra_params = (set(cond_data[4].keys())
                - set(unit_h.getParameters()))
            if len(extra_params) > 0:
                self.pointError("Function extra parameters: "
                    + ' '.join(sorted(extra_params)))
                return None
            err_msg = unit_h.validateArgs(cond_data[4])
            if err_msg:
                self.pointError(err_msg)
                return None
        return unit_h.buildCondition(cond_data, self)

    def getUsedEnumValues(self, unit_name):
        visitor = EnumUnitConditionVisitor(unit_name)
        self.visitAll(visitor)
        return visitor.makeResult()
