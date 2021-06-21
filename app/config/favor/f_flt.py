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
import sys

from app.prepare.prep_filters import FilterPrepareSetH
from app.config.variables import anfisaVariables

# ===============================================
def defFavorFlt(metadata_record):
    assert metadata_record.get("data_schema") == "FAVOR", (
        "FAVOR data schema expected: "
        + metadata_record.get("data_schema"))

    filters = FilterPrepareSetH(metadata_record, anfisaVariables,
        check_identifiers = False)

    with filters.viewGroup("Coordinates"):
        filters.statusUnit("Chromosome", "/_filters/chromosome",
            variants = ["chr1", "chr2", "chr3", "chr4", "chr5",
                "chr6", "chr7", "chr8", "chr9", "chr10",
                "chr11", "chr12", "chr13", "chr14", "chr15",
                "chr16", "chr17", "chr18", "chr19", "chr20",
                "chr21", "chr22", "chr23", "chrX", "chrY", "undefined"],
            default_value = "undefined")

        filters.intValueUnit("Position", "/_filters/position",
            default_value = sys.maxsize)

    with filters.viewGroup("Genes"):
        genes_unit = filters.multiStatusUnit("Symbol",
            #  "/_filters/genes[]",
            "/_view/general/genes[]",
            compact_mode = True)
        filters.panelsUnit("Panels", genes_unit, "Symbol",
            view_path = "/_view/general/gene_panels")
        filters.intValueUnit("Num_Genes", "/_view/general/genes",
            conversion = "len", default_value = 0)

    with filters.viewGroup("gnomAD"):
        filters.floatValueUnit("gnomAD_Total_AF",
            "/_filters/gnomad_total_af",
            diap = (0., 1.), default_value = 0.)

    with filters.viewGroup("GENCODE"):
        filters.multiStatusUnit("GENCODE_Category",
            "/_filters/gencode_category[]",
            default_value = "None")
        filters.multiStatusUnit("GENCODE_Exonic_Category",
            "/_filters/gencode_exonic_category",
            compact_mode = True)

    with filters.viewGroup("TOPMed"):
        filters.multiStatusUnit("TOPMed_QC_Status",
            "/_filters/top_med_qc_status[]", default_value = "None")
        filters.floatValueUnit("TOPMed_Bravo_AF",
            "/_filters/top_med_bravo_af", default_value = 0.)

    with filters.viewGroup("Allele Frequencies"):
        filters.floatValueUnit("ExAC03", "/_filters/exac03",
            render_mode = "linear,<", default_value = 0.)

    with filters.viewGroup("Variant Category"):
        filters.multiStatusUnit("Disruptive_Missense",
            "/_filters/disruptive_missense", default_value = "N/A")
        filters.multiStatusUnit("CAGE_Promoter", "/_filters/cage_promoter",
            default_value = "N/A")
        filters.multiStatusUnit("CAGE_Enhancer", "/_filters/cage_enhancer",
            default_value = "N/A")
        filters.multiStatusUnit("Gene_Hancer", "/_filters/gene_hancer",
            default_value = "N/A")
        filters.multiStatusUnit("Super_Enhancer", "/_filters/super_enhancer",
            default_value = "N/A")

    with filters.viewGroup("Nucleotide Diversity"):
        filters.floatValueUnit("bStatistics", "/_filters/bstatistics",
            default_value = 0.)

    with filters.viewGroup("Mutation Rate"):
        filters.floatValueUnit("Freq1000bp", "/_filters/freq1000bp",
            default_value = 0.)
        filters.floatValueUnit("Rare1000bp", "/_filters/rare1000bp",
            default_value = 0.)

    with filters.viewGroup("Predictions"):
        filters.multiStatusUnit("Clinvar", "/_filters/clinvar[]",
            default_value = "N/A")

    with filters.viewGroup("Protein Function"):
        filters.multiStatusUnit("Polyphen_2_HVAR", "/_filters/polyphen2_hvar",
            default_value = "N/A")
        filters.multiStatusUnit("Polyphen_2_HDIV", "/_filters/polyphen2_hdiv",
            default_value = "N/A")

        filters.multiStatusUnit("PolyPhenCat", "/_filters/polyphen_cat",
            default_value = "N/A")

        filters.multiStatusUnit("SIFTcat", "/_filters/sift_cat",
            default_value = "N/A")

    with filters.viewGroup("Integrative Score"):
        filters.floatValueUnit("GC", "/_filters/gc", default_value = 0.)
        filters.floatValueUnit("CpG", "/_filters/cpg", default_value = 0.)

    return filters
