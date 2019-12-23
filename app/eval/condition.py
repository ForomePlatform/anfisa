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
    def condNum(unit_name,
            min_val = None, min_eq = True, max_val = None, max_eq = True):
        assert min_val is not None or max_val is not None
        return ["numeric", unit_name, [min_val, min_eq, max_val, max_eq]]

    @staticmethod
    def condEnum(unit_name, variants, join_mode = "OR"):
        assert join_mode in {"AND", "OR", "NOT"}
        return ["enum", unit_name, join_mode, variants]

    @staticmethod
    def condTrioInheritanceZ(unit_name, variants,
            join_mode = "OR", problem_group = None):
        assert join_mode in {"AND", "OR", "NOT"}
        if problem_group is not None:
            problem_group = sorted(problem_group)
        return ["func", unit_name, {
            "type": "trio-inheritance-z",
            "problem-group": problem_group}, join_mode, variants]

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

#===============================================
def validateNumCondition(cond_info):
    if cond_info[0] != "numeric" or len(cond_info[2]) != 4:
        return False
    min_val, min_eq, max_val, max_eq = cond_info[2]
    if min_eq not in {True, False} or max_eq not in {True, False}:
        return False
    return True

#===============================================
def validateEnumCondition(cond_info):
    if cond_info[0] != "enum":
        return False
    filter_mode, variants = cond_info[2:]
    return (filter_mode in {"", "OR", "AND", "NOT"}
        and len(variants) > 0)


#===============================================
ZYG_BOUNDS_VAL = {
    "0":    [None, True, 0, True],
    "0-1":  [None, True, 1, True],
    "1":    [1, True, 1, True],
    "1-2":  [1, True, None, True],
    "2":    [2, True, None, True]}
