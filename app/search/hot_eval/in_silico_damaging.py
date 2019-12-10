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
    """Has Damaging Predictions"""

    if (rec.Severity > 2):
        return True

    # 2.a.	Present in ClinVar Path, Likely Path.
    clinvar_status = None
    if (rec.Clinvar_stars in {'2', '3', '4'}  or
            rec.Clinvar_Trusted_Benign in {False, "No data"}):
        if 'pathogenic' in rec.ClinVar_Significance:
            clinvar_status = "Path"
        elif 'benign' in str(rec.ClinVar_Significance).lower():
            clinvar_status = "Benign"
    elif rec.Clinvar_Trusted_Benign in {True}:
        clinvar_status = "Benign"
    elif (rec.Clinvar_stars in {'1'}
          and 'benign' in str(rec.ClinVar_Significance).lower()):
        clinvar_status = "Benign"

    if (clinvar_status == "Path"):
        return True
    if (clinvar_status == "Benign"):
        return False

    # Include Splice Altering variants
    if (rec.splice_ai_dsmax > 0.5):
        return True

    if (len(rec.Polyphen_2_HVAR) > 0):
        return (len(rec.Polyphen_2_HVAR - {"P", "D"}) == 0)
    if (len(rec.SIFT) > 0):
        return (len(rec.SIFT - {"deleterious"}) == 0)
    if (len(rec.Polyphen_2_HDIV) > 0):
        return (len(rec.Polyphen_2_HDIV - {"P", "D"}) == 0)
    return False

