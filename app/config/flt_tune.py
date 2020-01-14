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

from app.model.zygosity import InheritanceUnit
from app.model.comp_hets import CompHetsUnit
#===============================================
def tuneUnits(ds_h):
    if ds_h.testRequirements({"ZYG"}):
        InheritanceUnit.makeIt(ds_h, {
            "name": "Inheritance_Mode",
            "title": "Inheritance Mode",
            "vgroup": "Inheritance"},
            x_unit = "Chromosome", x_values = ["chrX"],
            before = "Proband_Zygosity")

    if ds_h.testRequirements({"ZYG", "WS"}):
        CompHetsUnit.makeIt(ds_h, {
            "name":   "Compound_Het",
            "title":  "Calculated Compound Heterozygous",
            "vgroup": "Inheritance"},
            gene_levels = [
                ["transcript", "Transcript_id", "shared transcript"],
                ["gene", "Transctript_gene_id", "shared gene"],
                ["rough", "Symbol", "non-intersecting transcripts"]])

    if ds_h.testRequirements({"ZYG", "XL"}):
        CompHetsUnit.makeIt(ds_h, {
            "name":   "Compound_Het",
            "title":  "Calculated Compound Hetreozygous",
            "vgroup": "Inheritance"},
            gene_levels = [
                ["rough", "Symbol", "rough approx"]])

#===============================================
