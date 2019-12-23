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

from .var_unit import VarUnit
#===============================================
class OperativeUnit(VarUnit):
    def __init__(self, actual_unit_h):
        VarUnit.__init__(self, actual_unit_h.getEvalSpace(),
            actual_unit_h.getDescr(),
            unit_kind = "operative", sub_kind = actual_unit_h.getUnitKind())
        self.mActualUnit = actual_unit_h

    def getActualUnit(self):
        return self.mActualUnit

    def validateCondition(self, cond_info, op_units):
        if op_units is None:
            return False
        if self.getName() in op_units:
            return self.mActualUnit.validateCondition(cond_info, op_units)
        if cond_info[0] != "import" or len(cond_info) != 2:
            return False
        op_units.add(self.getName())
        return True

    def parseCondition(self, cond_info, eval_h):
        assert eval_h.getImportSupport(self.getName()) is not None
        return self.mActualUnit.parseCondition(cond_info, eval_h)

    def prepareStat(self, incomplete_eval_h):
        if incomplete_eval_h.getImportSupport(
                self.getName()) is not None:
            return self.mActualUnit.prepareStat(incomplete_eval_h)

        ret_handle = VarUnit.prepareStat(self)
        ret_handle["kind"] = "inactive"
        return ret_handle

    def makeStat(self, condition, repr_context):
        eval_h = repr_context["eval"]
        if eval_h.getImportSupport(self.getName()) is not None:
            return self.mActualUnit.makeStat(condition, repr_context)
        return self.prepareStat(eval_h)

#===============================================
