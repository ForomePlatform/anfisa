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
import abc
from utils.log_err import logException
from .condition import validateNumCondition, validateEnumCondition
#===============================================
class FilterBase:
    def __init__(self, cond_env,
            updated_time = None, updated_from = None):
        self.mCondEnv = cond_env
        self.mCompData = dict()
        self.mOperativeUnitSeq = []
        self.mUpdatedInfo = [updated_time, updated_from]

    @abc.abstractmethod
    def getFltKind(self):
        return None

    @abc.abstractmethod
    def noErrors(self):
        assert False
        return False

    @abc.abstractmethod
    def getHashCode(self):
        return None

    @abc.abstractmethod
    def isActive(self):
        assert False
        return False

    @abc.abstractmethod
    def activate(self):
        assert False

    @abc.abstractmethod
    def reportInfo(self):
        assert False

    def getCondEnv(self):
        return self.mCondEnv

    def getCompData(self, unit_name):
        return self.mCompData[unit_name]

    def getUpdateInfo(self):
        return self.mUpdatedInfo

    def iterActiveOperativeUnits(self, instr_no = None):
        for unit_instr_no, unit_h in self.mOperativeUnitSeq:
            if instr_no is None or instr_no >= unit_instr_no:
                yield unit_h

    def validateCondData(self, cond_data, op_units = None):
        try:
            return self._validateCondData(cond_data, op_units)
        except Exception:
            logException("Validation failure")
            return False

    def _validateCondData(self, cond_info, op_units):
        if len(cond_info) == 0:
            return True
        if cond_info[0] is None:
            if len(cond_info) != 1:
                return False
            return True
        if cond_info[0] in ("and", "or"):
            return all(self._validateCondData(cc, op_units)
                for cc in cond_info[1:])
        if cond_info[0] == "not":
            if len(cond_info) != 2:
                return False
            return self._validateCondData(cond_info[1], op_units)
        if cond_info[0] == "import":
            if len(cond_info) != 2:
                return False
            unit_name = cond_info[1]
            if unit_name in op_units:
                return False
            _, unit_h = self.mCondEnv.detectUnit(unit_name, "operational")
            if unit_h is None:
                return False
            op_units.add(unit_name)
            return True

        pre_unit_kind, unit_name = cond_info[:2]
        unit_kind, unit_h = self.mCondEnv.detectUnit(unit_name, pre_unit_kind)
        if unit_h is None:
            return False
        if unit_kind == "operational":
            if not unit_name in op_units:
                return False
            return unit_h.validateCondition(cond_info)
        if unit_kind == "reserved":
            unit_kind = cond_info[0]
        if unit_kind == "special":
            return unit_h.validateCondition(cond_info)
        if cond_info[0] == "numeric":
            return validateNumCondition(cond_info)
        if cond_info[0] == "enum":
            return validateEnumCondition(cond_info)
        return False

    def parseCondData(self, cond_info):
        if len(cond_info) == 0:
            return self.mCondEnv.getCondAll()
        if cond_info[0] is None:
            assert len(cond_info) == 1
            return self.mCondEnv.getCondNone()
        if cond_info[0] == "and":
            return self.mCondEnv.joinAnd(
                [self.parseCondData(cc) for cc in cond_info[1:]])
        if cond_info[0] == "or":
            return self.mCondEnv.joinOr(
                [self.parseCondData(cc) for cc in cond_info[1:]])
        if cond_info[0] == "not":
            assert len(cond_info) == 2
            return self.parseCondData(cond_info[1]).negative()

        pre_unit_kind, unit_name = cond_info[:2]
        unit_kind, unit_h = self.mCondEnv.detectUnit(unit_name, pre_unit_kind)
        if unit_kind == "operational":
            return unit_h.parseCondition(cond_info,
                self.mCompData[unit_name])
        if unit_kind == "reserved":
            unit_kind = cond_info[0]
        if unit_kind == "special":
            return unit_h.parseCondition(cond_info)
        if cond_info[0] == "numeric":
            bounds, use_undef = cond_info[2:]
            return self.mCondEnv.makeNumericCond(unit_h, bounds, use_undef)
        if cond_info[0] == "enum":
            filter_mode, variants = cond_info[2:]
            return self.mCondEnv.makeEnumCond(unit_h, variants, filter_mode)
        assert False
        return self.mCondEnv.getCondNone()

    def importUnit(self, instr_no, unit_name, actual_condition, hash_code):
        _, unit_h = self.mCondEnv.detectUnit(unit_name, "operational")
        if unit_h is None:
            return False
        comp_data = self.mCondEnv.getCompCache(unit_name, hash_code)
        if comp_data is None:
            comp_data = unit_h.prepareImport(actual_condition)
            self.mCondEnv.setCompCache(unit_name, hash_code, comp_data)
        self.mCompData[unit_h.getName()] = comp_data
        self.mOperativeUnitSeq.append([instr_no, unit_h])
        return True
