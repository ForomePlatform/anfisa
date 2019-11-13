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
    """SEQaBOO ACMG59 Rule, v.0.1"""

    # standard part of evaluation
    if ("Quality-PASS" not in rec.Rules):
        return False

    #hdmd_clinically_significant = len(set(rec.HGMD_Tags) & {"DM", "DM?"}) > 0
    hdmd_clinically_significant = len(set(rec.HGMD_Tags) & {"DM"}) > 0
    clinvar_clinically_significant = (rec.Clinvar_Benign == False)
    clinically_significant = clinvar_clinically_significant or hdmd_clinically_significant

    if (clinically_significant):
        return True

    if (rec.Severity > 2):
        return True

    return False