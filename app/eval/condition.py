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
    def condFunc(unit_name, func_args, variants, join_mode = "OR"):
        assert join_mode in {"AND", "OR", "NOT"}
        return ["func", unit_name, join_mode, variants, func_args]

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
    def condNot(cond_data):
        return ["not", cond_data]

    @staticmethod
    def joinAnd(cond_seq):
        if len(cond_seq) == 0:
            return []
        if len(cond_seq) == 1:
            return cond_seq[0]
        return ["and"] + cond_seq[:]

    @staticmethod
    def joinOr(cond_seq):
        if len(cond_seq) == 0:
            return []
        if len(cond_seq) == 1:
            return cond_seq[0]
        return ["or"] + cond_seq[:]

#===============================================
def validateCondition(cond_info):
    if (isinstance(cond_info, list) and len(cond_info) > 2
            and isinstance(cond_info[1], str)):
        if cond_info[0] == "numeric":
            if (len(cond_info) == 3 and isinstance(cond_info[2], list)
                    and len(cond_info[2]) == 4):
                min_val, min_eq, max_val, max_eq = cond_info[2]
                if min_eq not in {True, False} or max_eq not in {True, False}:
                    return "Numeric condition parameters mix-up"
                return None
            return "Bad numeric condition"
        if cond_info[0] == "enum":
            if len(cond_info) == 4:
                filter_mode, variants = cond_info[2:]
                if not isinstance(variants, list):
                    return "Wrong list of enum variants"
                if filter_mode not in {"", "OR", "AND", "NOT"}:
                    return "Bad filter mode for enum condition"
                return None
            return "Bad enumerated condition"
        if cond_info[0] == "func":
            if len(cond_info) == 5:
                filter_mode, variants, func_args = cond_info[2:]
                if func_args is not None:
                    if (not isinstance(func_args, dict) or not all(
                            isinstance(key, str) for key in func_args.keys())):
                        return "Wrong function parameters"
                if not isinstance(variants, list):
                    return "Wrong list of functions variants"
                if filter_mode not in {"", "OR", "AND", "NOT"}:
                    return "Bad filter mode for function condition"
                return None
            return "Bad function condition"
    return "Improper condition"


#===============================================
ZYG_BOUNDS_VAL = {
    "0":    [None, True, 0, True],
    "0-1":  [None, True, 1, True],
    "1":    [1, True, 1, True],
    "1-2":  [1, True, None, True],
    "2":    [2, True, None, True]}
