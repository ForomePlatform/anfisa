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

from app.view.asp_set import AspectSetH
from app.view.aspect import AspectH
from app.view.attr import AttrH
from app.view.colgrp import ColGroupsH


# ===============================================
def defFavorView(metadata_record):
    assert metadata_record.get("data_schema") == "FAVOR", (
        "FAVOR data schema expected: "
        + metadata_record.get("data_schema"))

    aspect_list = [
        AspectH("view_bas", "Basic", "_view", field = "general"),
        AspectH("view_variant_category", "Variant Category", "_view",
            field = "variant_category"),
        AspectH("view_allele_frequencies", "Frequencies", "_view",
            field = "allele_frequencies"),
        AspectH("view_integrative_score", "Score", "_view",
            field = "integrative_score"),
        AspectH("view_protein_function", "Protein Function", "_view",
            field = "protein_function"),
        AspectH("view_conservation", "Conservation", "_view",
            field = "conservation"),
        AspectH("view_epigenetics", "Epigenetics", "_view",
            col_groups = ColGroupsH([["epigenetics", None]])),
        AspectH("view_transcription_factors", "Transcription Factors", "_view",
            field = "transcription_factors"),
        AspectH("view_chromatin_states", "Chromatin States", "_view",
            field = "chromatin_states"),
        AspectH("view_local_nucleotide_diversity",
            "Nucleotide Diversity", "_view",
            field = "local_nucleotide_diversity"),
        AspectH("view_mutation_rate", "Mutation Rate", "_view",
            field = "mutation_rate"),
        AspectH("view_mappability", "Mappability", "_view",
            field = "mappability"),
        AspectH("_main", "VEP Data", "__data")
    ]

    aspects = AspectSetH(aspect_list)

    aspects["view_bas"].setAttributes([
        AttrH("type", title = "Variant Type",
            kind = "string", tooltip = "Type of variant"),
        AttrH("gene_panels", title = "Gene panels", is_seq = True),
        AttrH("rsID", kind = "string"),
        AttrH("TOPMed_Depth", kind = "string"),
        AttrH("TOPMed_QC_Status", kind = "string"),
        AttrH("TOPMed_Bravo_AF", kind = "string"),
        AttrH("GNOMAD_Total_AF", kind = "string"),
        AttrH("ALL_1000G_AF", kind = "string")
    ])

    aspects["view_variant_category"].setAttributes([
        AttrH("GENCODE_Category", title = "GENCODE Category", kind = "string"),
        AttrH("GENCODE_Exonic_Category", kind = "string"),
        AttrH("GENCODE_Exonic_Info", kind = "string"),
        AttrH("GENCODE_Info", kind = "string"),
        AttrH("CAGE_Enhancer", kind = "string"),
        AttrH("CAGE_Promoter", kind = "string"),
        AttrH("ClinVar", kind = "string"),
        AttrH("Disruptive_Missense", kind = "string"),
        AttrH("GeneHancer", kind = "string"),
        AttrH("SuperEnhancer", kind = "string")
    ])

    aspects["view_allele_frequencies"].setAttributes([
        AttrH("AFR_1000G_AF", kind = "string"),
        AttrH("ALL_1000G_AF", kind = "string"),
        AttrH("AMR_1000G_AF", kind = "string"),
        AttrH("EAS_1000G_AF", kind = "string"),
        AttrH("ESP_AA", kind = "string"),
        AttrH("ESP_ALL", kind = "string"),
        AttrH("ESP_EA", kind = "string"),
        AttrH("EUR_1000G_AF", kind = "string"),
        AttrH("ExAC03", kind = "string"),
        AttrH("ExAC03_nontcga", kind = "string"),
        AttrH("GNOMAD_Total_AF", kind = "string"),
        AttrH("SAS_1000G_AF", kind = "string"),
        AttrH("TOPMed_Bravo_AF", kind = "string")
    ])

    aspects["view_integrative_score"].setAttributes([
        AttrH("LINSIGHT", title = "LINSIGHT", kind = "string"),
        AttrH("gc", title = "GC", kind = "string"),
        AttrH("cpg", title = "CpG", kind = "string"),
        AttrH("APC_Conservation", kind = "string"),
        AttrH("APC_Epigenetics", kind = "string"),
        AttrH("APC_Local_Nucleotide_Diversity", kind = "string"),
        AttrH("APC_MapAbility", kind = "string"),
        AttrH("APC_MutationDensity", kind = "string"),
        AttrH("APC_ProteinFunction", kind = "string"),
        AttrH("APC_Proximity_To_TSSTES", kind = "string"),
        AttrH("APC_TranscriptionFactor", kind = "string"),
        AttrH("CADD_PHRED", kind = "string"),
        AttrH("CADD_RawScore", kind = "string"),
        AttrH("FATHMM_XF_coding", kind = "string"),
        AttrH("FATHMM_XF_noncoding", kind = "string")
    ])

    aspects["view_protein_function"].setAttributes([
        AttrH("APC_ProteinFunction",
            title = "APC ProteinFunction", kind = "string"),
        AttrH("Grantham", kind = "string"),
        AttrH("MutationAssessor", kind = "string"),
        AttrH("MutationTaster", kind = "string"),
        AttrH("PolyPhenCat", kind = "string"),
        AttrH("PolyPhenVal", kind = "string"),
        AttrH("SIFTcat", kind = "string"),
        AttrH("SIFTval", kind = "string"),
        AttrH("polyphen2_hdiv", kind = "string"),
        AttrH("polyphen2_hdiv_score", kind = "string"),
        AttrH("polyphen2_hvar", kind = "string"),
        AttrH("polyphen2_hvar_score", kind = "string")
    ])

    aspects["view_conservation"].setAttributes([
        AttrH("APC_Conservation", title = "APC Conservation", kind = "string"),
        AttrH("GerpN", kind = "string"),
        AttrH("GerpS", kind = "string"),
        AttrH("mamPhCons", kind = "string"),
        AttrH("mamPhyloP", kind = "string"),
        AttrH("priPhCons", kind = "string"),
        AttrH("priPhyloP", kind = "string"),
        AttrH("verPhCons", kind = "string"),
        AttrH("verPhyloP", kind = "string"),
    ])

    aspects["view_epigenetics"].setAttributes([
        AttrH("APC_Epigenetics",
            kind = "string", title = "APC Epigenetics"),
        AttrH("DNase", kind = "string"),
        AttrH("H2AFZ", kind = "string"),
        AttrH("H3K27ac", kind = "string"),
        AttrH("H3K27me3", kind = "string"),
        AttrH("H3K36me3", kind = "string"),
        AttrH("H3K4me1", kind = "string"),
        AttrH("H3K4me2", kind = "string"),
        AttrH("H3K4me3", kind = "string"),
        AttrH("H3K79me2", kind = "string"),
        AttrH("H3K9ac", kind = "string"),
        AttrH("H3K9me3", kind = "string"),
        AttrH("H4K20me1", kind = "string"),
        AttrH("totalRNA", kind = "string")])

    aspects["view_transcription_factors"].setAttributes([
        AttrH("APC_TranscriptionFactor",
            kind = "string", title = "APC TranscriptionFactor"),
        AttrH("OverlapCL", kind = "string"),
        AttrH("OverlapTF", kind = "string")
    ])

    aspects["view_chromatin_states"].setAttributes([
        AttrH("cHmm_E1", title = "cHmm E1", kind = "string"),
        AttrH("cHmm_E2", title = "cHmm E2", kind = "string"),
        AttrH("cHmm_E3", title = "cHmm E3", kind = "string"),
        AttrH("cHmm_E4", title = "cHmm E4", kind = "string"),
        AttrH("cHmm_E5", title = "cHmm E5", kind = "string"),
        AttrH("cHmm_E6", title = "cHmm E6", kind = "string"),
        AttrH("cHmm_E7", title = "cHmm E7", kind = "string"),
        AttrH("cHmm_E8", title = "cHmm E8", kind = "string"),
        AttrH("cHmm_E9", title = "cHmm E9", kind = "string"),
        AttrH("cHmm_E10", title = "cHmm E10", kind = "string"),
        AttrH("cHmm_E11", title = "cHmm E11", kind = "string"),
        AttrH("cHmm_E12", title = "cHmm E12", kind = "string"),
        AttrH("cHmm_E13", title = "cHmm E13", kind = "string"),
        AttrH("cHmm_E14", title = "cHmm E14", kind = "string"),
        AttrH("cHmm_E15", title = "cHmm E15", kind = "string"),
        AttrH("cHmm_E16", title = "cHmm E16", kind = "string"),
        AttrH("cHmm_E17", title = "cHmm E17", kind = "string"),
        AttrH("cHmm_E18", title = "cHmm E18", kind = "string"),
        AttrH("cHmm_E19", title = "cHmm E19", kind = "string"),
        AttrH("cHmm_E20", title = "cHmm E20", kind = "string"),
        AttrH("cHmm_E21", title = "cHmm E21", kind = "string"),
        AttrH("cHmm_E22", title = "cHmm E22", kind = "string"),
        AttrH("cHmm_E23", title = "cHmm E23", kind = "string"),
        AttrH("cHmm_E24", title = "cHmm E24", kind = "string"),
        AttrH("cHmm_E25", title = "cHmm E25", kind = "string")
    ])

    aspects["view_local_nucleotide_diversity"].setAttributes([
        AttrH("APC_Local_Nucleotide_Diversity", kind = "string",
            title = "APC Local Nucleotide Diversity"),
        AttrH("NucDiv", kind = "string"),
        AttrH("RecRate", kind = "string"),
        AttrH("bStatistics", kind = "string"),
    ])

    aspects["view_mutation_rate"].setAttributes([
        AttrH("APC_MutationDensity", kind = "string",
            title = "APC MutationDensity"),
        AttrH("Freq1000bp", kind = "string"),
        AttrH("Rare1000bp", kind = "string"),
        AttrH("Sngl1000bp", kind = "string")
    ])

    aspects["view_mappability"].setAttributes([
        AttrH("APC_MapAbility", kind = "string", title = "APC MapAbility"),
        AttrH("Bismap_k100", kind = "string"),
        AttrH("Bismap_k24", kind = "string"),
        AttrH("Bismap_k50", kind = "string"),
        AttrH("Umap_k100", kind = "string"),
        AttrH("Umap_k24", kind = "string"),
        AttrH("Umap_k50", kind = "string")
    ])

    aspects["_main"].setAttributes([
        AttrH("label"),
        AttrH("color_code")
    ])

    return aspects
