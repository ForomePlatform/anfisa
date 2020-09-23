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
    def clear(arr):
        ret = []
        if arr:
            for val in arr:
                if val:
                    val = val.strip()
                if val:
                    ret.append(val)
        return ret

    @staticmethod
    def uniq(arr):
        if not arr:
            return []
        return sorted(set(arr))

    @staticmethod
    def values(arr):
        ret = []
        for dict in arr:
            ret += sorted(dict.values())
        return ret

    @staticmethod
    def keys(arr):
        ret = []
        for dict in arr:
            ret += sorted(dict.keys())
        return ret

    @staticmethod
    def positive(arr):
        ret = []
        for val in arr:
            if val:
                ret.append(val)
        return ret

    @staticmethod
    def negative(arr):
        ret = []
        for val in arr:
            if not val:
                ret.append(val)
        return ret

    @staticmethod
    def split(separator, arr):
        ret = []
        for val in arr:
            if not val:
                continue
            for it in val.split(separator):
                ret.append(it)
        return ret

    @staticmethod
    def split_re(pattern, arr):
        ret = []
        for val in arr:
            if not val:
                continue
            for it in re.split(pattern, val):
                ret.append(it)
        return ret

    @staticmethod
    def filter(check_f, arr):
        ret = []
        for val in arr:
            if check_f(val):
                ret.append(val)
        return ret

    @staticmethod
    def property(property, arr):
        ret = []
        for val in arr:
            ret.append(val.get(property)
                if val else None)
        return ret

    @classmethod
    def makeOne(cls, conv_item, func_registry):
        if isinstance(conv_item, str):
            if conv_item == "len":
                return lambda rec: cls.op_rec(len, 0, rec)
            if conv_item == "min":
                return lambda rec: cls.op_rec(min, 0, rec)
            if conv_item == "max":
                return lambda rec: cls.op_rec(max, 0, rec)
            if conv_item == "values":
                return lambda rec: cls.op_rec(cls.values, [], rec)
            if conv_item == "keys":
                return lambda rec: cls.op_rec(cls.keys, [], rec)
            if conv_item == "clear":
                return cls.clear
            if conv_item == "uniq":
                return cls.uniq
            if conv_item == "positive":
                return cls.positive
            if conv_item == "negative":
                return cls.negative
            conv_f = func_registry.getNamedFunction(conv_item)
            if conv_f is not None:
                return conv_f
        if isinstance(conv_item, list) and len(conv_item) == 2:
            func_name, par = conv_item
            if func_name == "property":
                return lambda rec: cls.property(par, rec)
            if func_name == "skip":
                op_f = lambda rec: rec[par:]
                return lambda rec: cls.op_rec(op_f, [], rec)
            if func_name == "split":
                return lambda rec: cls.split(par, rec)
            if func_name == "split_re":
                pattern = re.compile(par)
                return lambda rec: cls.split_re(pattern, rec)
            if func_name == "filter":
                conv_f = func_registry.getNamedFunction(par)
                assert conv_f is not None, (
                    "No named function: %s" % par)
                return lambda rec: cls.filter(conv_f, rec)
            if func_name == "min":
                return lambda rec: cls.op_rec(min, par, rec)
            if func_name == "max":
                return lambda rec: cls.op_rec(max, par, rec)
        assert False, "Bad conversion item %s" % repr(conv_item)

#===============================================
# TRF: All the code below is deprecated
#===============================================
def _conv_len(arr):
    if arr:
        return len(arr)
    return 0

def _conv_min(arr):
    if arr:
        return min(arr)
    return 0

def _conv_bool_present(val):
    if val in [True, "True"]:
        return "Present"
    elif val in [False, "False"]:
        return "Absent"
    return val

def _conv_count(arr, prop_name, value, skip = 0):
    return sum(el.get(prop_name) == value for el in arr[skip:])

def _conv_maxval(arr, prop_name):
    return max(el.get(prop_name) for el in arr)

def _conv_maxval_filter(arr, prop_name, filter_f):
    seq = []
    for el in arr:
        if filter_f(el):
            seq.append(el.get(prop_name))
    return max(seq)

def _conv_map(arr, prop_name):
    return [el.get(prop_name) for el in arr]

def _conv_values(arr):
    if not arr:
        return []
    assert len(arr) == 1
    dict_data = arr[0]
    ret = set()
    for rec in dict_data.values():
        for val in rec.split(','):
            val = val.strip()
            if val:
                ret.add(val)
    return sorted(ret)


#===============================================
sComplexConversions = {
    "count": (["property", "skip", "value"], {"skip": 0, "value": None}),
    "max": (["property", "filter"], {"filter": None}),
    "map": (["property"], dict())
}

def parseComplexConv(conversion):
    global sComplexConversions
    fields = conversion.split(',')
    func_name = fields[0].strip()
    assert func_name in sComplexConversions, (
        'Improper conversion function "%s"' % conversion)
    arg_list, arg_default_values = sComplexConversions[func_name]
    func_args = dict()
    for field in fields[1:]:
        if '=' in field:
            nm, _, val = field.partition('=')
        else:
            nm, val = "", field
        nm = nm.strip()
        assert nm in arg_list, (
            'Extra arg "%s" in conversion "%s"' % (nm, conversion))
        assert nm not in func_args, (
            'Arg "%s" duplication in conversion "%s"' % (nm, conversion))
        func_args[nm] = val.strip()
    for nm in arg_list:
        if nm in func_args:
            continue
        assert nm in arg_default_values, (
            'Arg "%s" not set in conversion "%s"' % (nm, conversion))
        func_args[nm] = arg_default_values[nm]
    return func_name, func_args

#===============================================
def makeFilterConversion(conversion, filter_set):
    if not conversion:
        return None
    if isinstance(conversion, list):
        return ListConversions.make(conversion, filter_set)
    if ',' in conversion:
        func_name, func_args = parseComplexConv(conversion)
        if func_name == "count":
            prop_name, value, skip = [func_args[key]
                for key in ("property", "value", "skip")]
            skip = int(skip)
            return lambda arr: _conv_count(arr, prop_name, value, skip)
        if func_name == "map":
            prop_name = func_args["property"]
            return lambda arr: _conv_map(arr, prop_name)
        if func_name == "max":
            prop_name, filter_name = [func_args[key]
                for key in ("property", "filter")]
            if filter_name:
                filter_f = filter_set.getNamedFunction(filter_name)
                assert filter_f is not None, (
                    "No registered annotation function: " + filter_name)
                return lambda arr: _conv_maxval_filter(
                    arr, prop_name, filter_f)
            return lambda arr: _conv_maxval(arr, prop_name)
    if conversion == "len":
        return _conv_len
    if conversion == "min":
        return _conv_min
    if conversion == "bool":
        return _conv_bool_present
    if conversion == "values":
        return _conv_values
    filter_f = filter_set.getNamedFunction(conversion)
    if filter_f is not None:
        return filter_f
    assert False, "Bad conversion: " + conversion
    return None
