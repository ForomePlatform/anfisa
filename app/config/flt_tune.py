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

from app.model.inheritance import InheritanceUnit, CustomInheritanceUnit
from app.model.comp_hets import CompHetsUnit, CompoundRequestUnit
from app.model.region_func import RegionFuncUnit
from .favor import FavorSchema

#===============================================
def tuneUnits(ds_h):
    if ds_h.getDataSchema() == "FAVOR":
        FavorSchema.tuneUnits(ds_h)
        return

    RegionFuncUnit.makeIt(ds_h,
        {
            "name":     "GeneRegion",
            "title":    "Gene Region",
            "vgroup":   "Coordinates"},
        {
            "chrom":    "Chromosome",
            "start":    "Start_Pos",
            "end":      "End_Pos",
            "symbol":   "Symbol"
        }, before = "Chromosome")

    zyg_support = ds_h.getZygositySupport()
    zyg_support.setupX(x_unit = "Chromosome", x_values = ["chrX"])

    if ds_h.testRequirements({"WS"}):
        zyg_support.regGeneApprox("transcript",
            "Transcript_id", "shared transcript")
        zyg_support.regGeneApprox("gene",
            "Transctript_gene_id", "shared gene")
    zyg_support.regGeneApprox("rough",
        "Symbol", "non-intersecting transcripts")

    if ds_h.testRequirements({"ZYG"}):
        InheritanceUnit.makeIt(ds_h, {
            "name": "Inheritance_Mode",
            "title": "Inheritance Mode",
            "vgroup": "Inheritance"},
            before = "Proband_Zygosity")

    if (ds_h.testRequirements({"ZYG"})
            or len(ds_h.getFamilyInfo()) == 1):
        CustomInheritanceUnit.makeIt(ds_h, {
            "name": "Custom_Inheritance_Mode",
            "title": "Custom Inheritance Mode",
            "vgroup": "Inheritance"},
            before = "Proband_Zygosity")

    if ds_h.testRequirements({"ZYG"}):
        CompHetsUnit.makeIt(ds_h, {
            "name":   "Compound_Het",
            "title":  "Calculated Compound",
            "vgroup": "Inheritance"})
        CompoundRequestUnit.makeIt(ds_h, {
            "name":   "Compound_Request",
            "title":  "Calculated Compound Request",
            "vgroup": "Inheritance"})
#===============================================
