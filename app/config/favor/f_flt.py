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

#===============================================
def _conv_len(arr):
    if arr:
        return len(arr)
    return 0

# ===============================================
def defFavorFlt(metadata_record):
    assert metadata_record.get("data_schema") == "FAVOR"

    filters = FilterPrepareSetH(metadata_record)

    with filters.viewGroup("Variant"):
        filters.statusUnit("Variant_Type", "/_filters/type",
                           default_value="Complex",
                           tooltip="Type of variant")

    with filters.viewGroup("Coordinates"):
        filters.statusUnit("Chromosome", "/_filters/chromosome",
            variants=["chr1", "chr2", "chr3", "chr4", "chr5",
                "chr6", "chr7", "chr8", "chr9", "chr10",
                "chr11", "chr12", "chr13", "chr14", "chr15",
                "chr16", "chr17", "chr18", "chr19", "chr20",
                "chr21", "chr22", "chr23", "chrX", "chrY", "undefined"],
            default_value="undefined")

        filters.intValueUnit("Start_Pos", "/_filters/start",
            title="Start Position",
            render_mode="neighborhood", default_value=sys.maxsize)
        filters.intValueUnit("End_Pos", "/_filters/end",
            title="End Position", default_value=0,
            render_mode="neighborhood")

    with filters.viewGroup("Genes"):
        genes_unit = filters.multiStatusUnit("Symbol", "/_filters/genes[]",
            compact_mode = True)
        filters.panelsUnit("Panels", genes_unit[0],
            view_path="/_view/general/gene_panels")
        filters.intValueUnit("Num_Genes", "/_view/general/genes",
            title = "Number of overlapping genes",
            conversion = _conv_len, default_value = 0)

    with filters.viewGroup("gnomAD"):
        filters.floatValueUnit("gnomAD_Total_AF",
            "/_filters/gnomad_total_af",
            diap = (0., 1.), default_value = 0.,
            title = "gnomAD Allele Frequency",
            render_mode = "log,<")

    with filters.viewGroup("GENCODE"):
        filters.multiStatusUnit("GENCODE Category",
            "/_filters/gencode_category",
            compact_mode=True)
        filters.multiStatusUnit("GENCODE Exonic Category",
            "/_filters/gencode_exonic_category",
            compact_mode=True)

    with filters.viewGroup("Predictions"):
        filters.multiStatusUnit("Clinvar",
            "/_filters/clinvar[]",
            default_value = "N/A",
            title = "Clinvar")

    with filters.viewGroup("Protein Function"):
        filters.multiStatusUnit("Polyphen_2_HVAR",
            "/_filters/polyphen2_hvar",
            default_value = "N/A",
            title = "Polyphen",
            tooltip = "HumVar (HVAR) is PolyPhen-2 classifier "
                "trained on known human variation (disease mutations vs."
                " common neutral variants)")
        filters.multiStatusUnit("Polyphen_2_HDIV",
            "/_filters/polyphen2_hdiv",
            default_value = "N/A",
            title = "Polyphen HDIV (High sensitivity)",
            tooltip = "HumDiv (HDIV) classifier is trained on a smaller "
                "number of select extreme effect disease mutations vs. "
                "divergence with close homologs (e.g. primates), which is "
                "supposed to consist of mostly neutral mutations.")

        filters.multiStatusUnit("PolyPhenCat",
            "/_filters/polyphen_cat",
            default_value = "N/A",
            title = "PolyPhenCat")

        filters.multiStatusUnit("SIFTcat", "/_filters/sift_cat",
            default_value = "N/A",
            tooltip = "Sort intolerated from tolerated (An amino acid at a "
                "position is tolerated | The most frequentest amino acid "
                "being tolerated).")

    return filters
