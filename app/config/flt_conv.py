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

def _conv_transcript_id(arr):
    return [el["transcript_id"] for el in arr] if arr else []

def _conv_nullcount(arr, the_field, skip):
    return sum(el.get(the_field) is None for el in arr[skip:])

def makeFilterConversion(conversion):
    if not conversion:
        return None
    if conversion == "len":
        return _conv_len
    if conversion == "min":
        return _conv_min
    if conversion == "bool":
        return _conv_bool_present
    if conversion == "transcript_id":
        return _conv_transcript_id
    if conversion.startswith("nullcount("):
        assert conversion.endswith(')')
        fields = conversion[conversion.find('(') + 1 : -1].split(',')
        assert 1 <= len(fields) <= 2
        the_field = fields[0].strip()
        skip = 0
        if len(fields) > 1:
            skip = int(fields[1].strip())
        return lambda arr: _conv_nullcount(arr, the_field, skip)
    assert False, "Bad conversion: " + conversion
