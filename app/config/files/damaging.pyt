#  Copyright (c) 2019. Partners HealthCare and other members of
#  Forome Association
#
#  Developed by Michael Bouzinier and Sergey Trifonov based on contributions by
#  Joel Krier, Shamil Sunyaev and other members of Division of
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

if (Most_Severe_Consequence in {
            'transcript_ablation',
            'splice_acceptor_variant',
            'splice_donor_variant',
            'stop_gained',
            'frameshift_variant',
            'CNV: deletion',
            'start_lost'
        }):
    return True

if (Clinvar_stars in {'2', '3', '4'} and
        ClinVar_Significance in {
            'Likely pathogenic',
            'Pathogenic',
            'Pathogenic, Affects',
            'Pathogenic, other',
            'Pathogenic, protective',
            'Pathogenic, association, protective',
            'Pathogenic, drug response',
            'Pathogenic, other, risk factor',
            'Pathogenic, risk factor',
            'Pathogenic/Likely pathogenic',
            'Pathogenic/Likely pathogenic, drug response',
            'Pathogenic/Likely pathogenic, risk factor',
            'Pathogenic/Likely pathogenic, other',
            'Likely pathogenic, drug response',
            'Likely pathogenic, risk factor',
            'Likely pathogenic, other',
            'Likely pathogenic, association'
        }):
    return True

if (Clinvar_stars in {'2', '3', '4'} and
        ClinVar_Significance in {
            'Benign',
            'Benign, association',
            'Benign, drug response',
            'Benign, other','Benign, risk factor',
            'Benign/Likely benign',
            'Benign/Likely benign, Affects',
            'Benign/Likely benign, association',
            'Benign/Likely benign, drug response',
            'Benign/Likely benign, drug response, risk factor',
            'Benign/Likely benign, other','Benign/Likely benign, protective',
            'Benign/Likely benign, protective, risk factor',
            'Benign/Likely benign, risk factor'
        }):
    return False

if splice_ai_dsmax > 0.5:
    return True

if Polyphen_2_HVAR in {"P", "D"}:
    return True

if Polyphen_2_HDIV in {"B"}:
    return False

if SIFT in {"deleterious", "deleterious_low_confidence"}:
    return True

if SIFT in {"tolerated", "tolerated_low_confidence"}:
    return False

if Polyphen_2_HDIV in {"P", "D"}:
    return True

if Polyphen_2_HVAR in {"B"}:
    return False

return False
