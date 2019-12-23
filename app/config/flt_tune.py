# -*- coding: utf-8 -*-

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

from app.model.zygosity import ZygosityUnit
from app.model.comp_hets import CompHetsUnit
#===============================================
def tuneUnits(ds_h):
    if ds_h.testRequirements({"ZYG"}):
        ZygosityUnit.makeIt(ds_h, {
            "name": "Inheritance_Mode",
            "title": "Inheritance Mode",
            "vgroup": "Inheritance"},
            x_unit = "Chromosome", x_values = ["chrX"],
            before = "Proband_Zygosity")

    if ds_h.testRequirements({"ZYG", "WS"}):
        CompHetsUnit.makeIt(ds_h, {
            "name":   "Compound_Het_transcript",
            "title":  "Calculated Compound Hetreozygous, transcript approx",
            "vgroup": "Inheritance"},
            gene_unit = "Transcript_id")
        CompHetsUnit.makeIt(ds_h, {
            "name":   "Compound_Het_gene",
            "title":  "Calculated Compound Hetreozygous, gene approx",
            "vgroup": "Inheritance"},
            gene_unit = "Transctript_gene_id")
        CompHetsUnit.makeIt(ds_h, {
            "name":   "Compound_Het_rough",
            "title":  "Calculated Compound Hetreozygous, rough approx",
            "vgroup": "Inheritance"},
            gene_unit = "Symbol")

    if ds_h.testRequirements({"ZYG", "XL"}):
        CompHetsUnit.makeIt(ds_h, {
            "name":   "Compound_Het",
            "title":  "Calculated Compound Hetreozygous",
            "vgroup": "Inheritance"},
            gene_unit = "Symbol")
        CompHetsUnit.makeIt(ds_h, {
            "name":   "Compound_Het2",
            "title":  "Calculated Compound Hetreozygous",
            "vgroup": "Inheritance"},
            gene_unit = "Symbol")

#===============================================
