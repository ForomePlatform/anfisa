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

def evalRec(env, rec):
    """BGM Acceptance Filter"""

    # standard part of evaluation
    if ("Quality-PASS" not in rec.Rules):
        return False

    p = [s for s in rec.Has_Variant if s and "proband" in s]
    if (not p):
        return False

    known = len(rec.Presence_in_Databases & {"ClinVar", "HGMD"}) > 0

    if (known):
        min_frequency = env.af_in_db
    else:
        min_frequency = env.af
    return rec.gnomAD_AF_Proband < min_frequency
