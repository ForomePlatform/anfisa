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


sFilterConversions = {
    "len": _conv_len,
    "min": _conv_min,
    "bool": _conv_bool_present,
    "transcript_id": _conv_transcript_id
}
