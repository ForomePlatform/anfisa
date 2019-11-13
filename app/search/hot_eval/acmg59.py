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
    """ACMG59"""

    return (len(set(rec.Symbol) &
        {
            "TMEM43",
            "DSP",
            "PKP2",
            "DSG2",
            "DSC2",
            "BRCA1",
            "BRCA2",
            "RYR2",
            "LMNA",
            "COL3A1",
            "GLA",
            "APC",
            "MUTYH",
            "APOB",
            "LDLR",
            "MYH7",
            "TPM1",
            "MYBPC3",
            "PRKAG2",
            "TNNI3",
            "MYL3",
            "MYL2",
            "ACTC1",
            "PCSK9",
            "BMPR1A",
            "SMAD4",
            "TNNT2",
            "TP53",
            "TGFBR1",
            "TGFBR2",
            "SMAD3",
            "KCNQ1",
            "KCNH1",
            "SCN5A",
            "MLH1",
            "MSH2",
            "MSH6",
            "PMS2",
            "RYR1",
            "CACNA1S",
            "FBN1",
            "MEN1",
            "RET",
            "NF2",
            "OTC",
            "SDHD",
            "SDHAF2",
            "SDHC",
            "SDHB",
            "STK11",
            "PTEN",
            "RB1",
            "MYH11",
            "ACTA2",
            "TSC1",
            "TSC2",
            "VHL",
            "WT1",
            "ATP7B"}) > 0)
