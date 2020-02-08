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

#===============================================
def defFavorView(metadata_record):
    assert metadata_record.get("data_schema") == "FAVOR"

    aspect_list = [
        AspectH("view_bas", "Basic", "_view", field = "general"),
        AspectH("view_variant_category", "Variant Category", "_view", field = "variant_category"),
        AspectH("view_allele_frequencies", "Frequencies", "_view", field = "allele_frequencies"),
        AspectH("view_integrative_score", "Score", "_view", field = "integrative_score"),
        AspectH("view_protein_function", "Protein Function", "_view", field = "protein_function"),
        AspectH("view_conservation", "Conservation", "_view", field = "conservation"),
        AspectH("view_epigenetics", "Epigenetics", "_view",
                col_groups = ColGroupsH(attr = "epigenetics")),
        AspectH("view_transcription_factors", "Transcription Factors", "_view", field = "transcription_factors"),
        AspectH("view_chromatin_states", "Chromatin States", "_view", field = "chromatin_states"),
        AspectH("view_local_nucleotide_diversity", "Nucleotide Diversity", "_view", field = "local_nucleotide_diversity"),
        AspectH("view_mutation_rate", "Mutation Rate", "_view", field = "mutation_rate"),
        AspectH("view_mappability", "Mappability", "_view", field = "mappability"),
        AspectH("_main", "VEP Data", "__data")
    ]

    aspects = AspectSetH(aspect_list)

    aspects["view_bas"].setAttributes([
        AttrH("type", title = "Variant Type",
            tooltip = "Type of variant"),
        AttrH("gene_panels", title = "Gene panels", is_seq = True)
    ])

    aspects["view_variant_category"].setAttributes([
        AttrH("GENCODE_Category", title = "GENCODE Category")
    ])

    aspects["view_allele_frequencies"].setAttributes([
            AttrH("GENCODE_Category", title = "GENCODE Category")
    ])

    aspects["view_integrative_score"].setAttributes([
        AttrH("LINSIGHT", title = "LINSIGHT")
    ])

    aspects["view_protein_function"].setAttributes([
        AttrH("APC_ProteinFunction", title = "APC ProteinFunction")
    ])

    aspects["view_conservation"].setAttributes([
        AttrH("APC_Conservation", title = "APC Conservation")
    ])

    aspects["view_epigenetics"].setAttributes([
        AttrH("APC_Epigenetics", title = "APC Epigenetics"),
        AttrH("DNase"),
        AttrH("H3K27ac"),
        AttrH("H3K4me1"),
        AttrH("H3K4me2"),
        AttrH("H3K4me3"),
        AttrH("H3K9ac"),
        AttrH("H4K20me1"),
        AttrH("H2AFZ"),
        AttrH("H3K9me3"),
        AttrH("H3K27me3"),
        AttrH("H3K36me3"),
        AttrH("H3K79me2"),
        AttrH("totalRNA")
    ])

    aspects["view_transcription_factors"].setAttributes([
        AttrH("APC_TranscriptionFactor", title = "APC TranscriptionFactor")
    ])

    aspects["view_chromatin_states"].setAttributes([
        AttrH("cHmm_E1", title = "cHmm E1")
    ])

    aspects["view_local_nucleotide_diversity"].setAttributes([
        AttrH("APC_Local_Nucleotide_Diversity", title = "APC Local Nucleotide Diversity")
    ])

    aspects["view_mutation_rate"].setAttributes([
        AttrH("APC_MutationDensity", title = "APC MutationDensity")
    ])

    aspects["view_mappability"].setAttributes([
        AttrH("APC_MapAbility", title = "APC MapAbility")
    ])

    aspects["_main"].setAttributes([
        AttrH("label"),
        AttrH("color_code")
    ])

    return aspects
