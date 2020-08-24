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


#===============================================
sComplexConversions = {
    "count": (["property", "skip", "value"], {"skip": 0, "value": None}),
    "max": (["property", "filter"], {"filter": None}),
    "select": (["property"], dict())
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
        func_args[nm] = arg_default_values
    return func_name, func_args

#===============================================
def makeFilterConversion(conversion, sol_broker):
    if not conversion:
        return None
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
                filter_f = sol_broker.pickAnnotationFunction(filter_name)
                assert filter_f is not None, (
                    "No annotation function: " + filter_name)
                return lambda arr: _conv_maxval_filter(
                    arr, prop_name, filter_f)
            return lambda arr: _conv_maxval(arr, prop_name)
    if conversion == "len":
        return _conv_len
    if conversion == "min":
        return _conv_min
    if conversion == "bool":
        return _conv_bool_present
    assert False, "Bad conversion: " + conversion
    return None
