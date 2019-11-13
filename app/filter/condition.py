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

#===============================================
class ConditionMaker:
    @staticmethod
    def condNum(unit_name, bounds, use_undef = False):
        return ["numeric", unit_name, bounds, use_undef]

    @staticmethod
    def condEnum(unit_name, variants, join_mode = "OR"):
        assert join_mode in {"AND", "OR", "ONLY", "NOT"}
        return ["enum", unit_name, join_mode, variants]

    @staticmethod
    def condInheritance(unit_name, variants,
            join_mode = "OR", problem_group = None):
        assert join_mode in {"AND", "OR", "ONLY", "NOT"}
        if problem_group is not None:
            problem_group = sorted(problem_group)
        return ["zygosity", unit_name, problem_group, join_mode, variants]

    @staticmethod
    def importVar(unit_name):
        return ["import", unit_name]

    @staticmethod
    def isAll(cond_data):
        return not cond_data

    @staticmethod
    def condAll():
        return []

    @staticmethod
    def condNone():
        return [None]

    @staticmethod
    def joinAnd(cond_seq):
        if len(cond_seq) == 0:
            return []
        if len(cond_seq) == 1:
            return cond_seq[0]
        return ["and"] + cond_seq[:]

    @staticmethod
    def upgradeOldFormat(cond_data):
        if cond_data[0] in {"int", "float"}:
            cond_data[0] = "numeric"
        if cond_data[0] == "status":
            cond_data[0] = "enum"
        if cond_data[0] == "numeric" and len(cond_data) == 5:
            unit_name, upper_bound_mode, bound, use_undef = cond_data[1:]
            bounds = [None, bound] if upper_bound_mode else [bound, None]
            return ["numeric", unit_name, bounds, use_undef]
        return cond_data

    @classmethod
    def upgradeOldFormatSeq(cls, cond_seq):
        return [cls.upgradeOldFormat(cond_data) for cond_data in cond_seq]

#===============================================
