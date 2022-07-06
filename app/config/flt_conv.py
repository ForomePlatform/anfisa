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
import re

#===============================================
class ListConversions:
    @staticmethod
    def apply_chain(chain, rec):
        for conv_f in chain:
            rec = conv_f(rec)
        return rec

    @classmethod
    def make(cls, conversion, func_registry = None):
        chain = [cls.makeOne(conv_item, func_registry)
            for conv_item in conversion]
        assert len(chain) > 0
        if len(chain) == 1:
            return chain[0]
        return lambda rec: cls.apply_chain(chain, rec)

    @staticmethod
    def op_rec(op_f, default, rec):
        if rec:
            return op_f(rec)
        return default

    @staticmethod
    def c_len(arr):
        if arr:
            return len(arr)
        return 0

    @staticmethod
    def c_min(arr):
        if arr:
            return min(arr)
        return 0

    @staticmethod
    def c_max(arr):
        if arr:
            return max(arr)
        return 0

    @staticmethod
    def c_clear(arr):
        ret = []
        if arr:
            for val in arr:
                if val:
                    val = val.strip()
                if val:
                    ret.append(val)
        return ret

    @staticmethod
    def c_uniq(arr):
        if not arr:
            return []
        return sorted(set(arr))

    @staticmethod
    def c_values(arr):
        ret = []
        if arr:
            for dict_entry in arr:
                ret += sorted(dict_entry.values())
        return ret

    @staticmethod
    def c_keys(arr):
        ret = []
        if arr:
            for dict_entry in arr:
                ret += sorted(dict_entry.keys())
        return ret

    @staticmethod
    def c_positive(arr):
        ret = []
        for val in arr:
            if val:
                ret.append(val)
        return ret

    @staticmethod
    def c_negative(arr):
        ret = []
        for val in arr:
            if not val:
                ret.append(val)
        return ret

    @staticmethod
    def c_split(separator, arr):
        ret = []
        for val in arr:
            if not val:
                continue
            for it in val.split(separator):
                ret.append(it)
        return ret

    @staticmethod
    def c_split_re(pattern, arr):
        ret = []
        for val in arr:
            if not val:
                continue
            for it in re.split(pattern, val):
                ret.append(it)
        return ret

    @staticmethod
    def c_filter(check_f, arr):
        ret = []
        for val in arr:
            if check_f(val):
                ret.append(val)
        return ret

    @staticmethod
    def c_property(attr_name, arr):
        ret = []
        for val in arr:
            ret.append(val.get(attr_name)
                if val else None)
        return ret

    sStrConv = None

    @classmethod
    def makeOne(cls, conv_item, func_registry):
        if cls.sStrConv is None:
            cls.sStrConv = {
                "len": cls.c_len,
                "min": cls.c_min,
                "max": cls.c_max,
                "values": cls.c_values,
                "keys": cls.c_keys,
                "clear": cls.c_clear,
                "uniq": cls.c_uniq,
                "positive": cls.c_positive,
                "negative": cls.c_negative
            }
        if isinstance(conv_item, str):
            if conv_item in cls.sStrConv:
                return cls.sStrConv[conv_item]
            conv_f = func_registry.getNamedFunction(conv_item)
            if conv_f is not None:
                return conv_f
        if isinstance(conv_item, list) and len(conv_item) == 2:
            func_name, par = conv_item
            if func_name == "property":
                return lambda rec: cls.c_property(par, rec)
            if func_name == "skip":
                def op_f(rec):
                    return rec[par:]
                return lambda rec: cls.op_rec(op_f, [], rec)
            if func_name == "split":
                return lambda rec: cls.c_split(par, rec)
            if func_name == "split_re":
                pattern = re.compile(par)
                return lambda rec: cls.c_split_re(pattern, rec)
            if func_name == "filter":
                conv_f = func_registry.getNamedFunction(par)
                assert conv_f is not None, (
                    "No named function: %s" % par)
                return lambda rec: cls.c_filter(conv_f, rec)
            if func_name == "min":
                return lambda rec: cls.op_rec(min, par, rec)
            if func_name == "max":
                return lambda rec: cls.op_rec(max, par, rec)
        assert False, "Bad conversion item: " + repr(conv_item)
        return None

#===============================================
def makeFilterConversion(conversion, filter_set):
    if not conversion:
        return None
    assert isinstance(conversion, list), (
        "Deprecated conversion logic, reload dataset")
    return ListConversions.make(conversion, filter_set)
