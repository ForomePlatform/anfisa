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
def defAvarstarFlt(metadata_record, ds_kind, druid_adm):
    assert metadata_record.get("data_schema") == "AVARSTAR", (
        "AVARSTAR data schema expected: "
        + metadata_record.get("data_schema"))

    filters = FilterPrepareSetH(metadata_record, anfisaVariables, ds_kind,
        druid_adm = druid_adm if ds_kind != "ws" else None,
        path_base = {
            "chromosome":       "/_filters/chromosome",
            "start":            "/_filters/start",
            "ref":              "/_data/ref",
            "alt":              "/_data/alt",
            "color":            "/_data/color_code",
            "label":            "/_data/label",
            "zygosity":         "/_data/zygosity",
            "transcripts":      "/_view/transcripts"})

    with filters.viewGroup("Coordinates"):
        filters.statusUnit("Chromosome", "/_filters/chromosome",
            variants = ["chr1", "chr2", "chr3", "chr4", "chr5",
                "chr6", "chr7", "chr8", "chr9", "chr10",
                "chr11", "chr12", "chr13", "chr14", "chr15",
                "chr16", "chr17", "chr18", "chr19", "chr20",
                "chr21", "chr22", "chr23", "chrX", "chrY", "undefined"],
            default_value = "undefined")

        filters.intValueUnit("Start_Pos", "/_filters/start",
            default_value = sys.maxsize)
        filters.intValueUnit("End_Pos", "/_filters/end",
            default_value = 0)

    with filters.viewGroup("Genes"):
        filters.varietyUnit("_Symbol", "Symbol", "Gene_Lists",
            "/_view/general/genes[]", "Symbol")

    with filters.viewGroup("gnomAD"):
        filters.floatValueUnit("gnomAD_AF",
            "/_filters/gnomad_af",
            diap = (0., 1.), default_value = 0.)

        filters.floatValueUnit("gnomAD_AF_Genomes",
            "/_filters/gnomad_af_genomes",
            diap = (0., 1.), default_value = 0.)

        filters.floatValueUnit("gnomAD_AF_Exomes",
            "/_filters/gnomad_af_exomes",
            diap = (0., 1.), default_value = 0.)

        filters.intValueUnit("gnomAD_Hom",
            "/_filters/gnomad_hom", default_value = 0)

        filters.intValueUnit("gnomAD_Hem",
            "/_filters/gnomad_hom", default_value = 0)

        filters.statusUnit("gnomAD_PopMax",
            "/_filters/gnomad_popmax", default_value = "None")

        filters.floatValueUnit("gnomAD_PopMax_AF",
            "/_filters/gnomad_popmax_af",
            diap = (0., 1.), default_value = 0.)

        filters.statusUnit("gnomAD_PopMax_Outbred",
            "/_filters/gnomad_popmax_outbred", default_value = "None")

        filters.floatValueUnit("gnomAD_PopMax_AF_Outbred",
            "/_filters/gnomad_popmax_af_outbred",
            diap = (0., 1.), default_value = 0.)

        filters.intValueUnit("gnomAD_PopMax_AN",
            "/_filters/gnomad_popmax_an", default_value = 0)

        filters.intValueUnit("gnomAD_PopMax_AN_Outbred",
            "/_filters/gnomad_popmax_an_outbred", default_value = 0)

    with filters.viewGroup("Transcripts"):
        filters.transcriptStatusUnit("Transcript_id", "Ensembl_transcriptid",
            default_value = "undefined", transcript_id_mode = True)
        filters.transcriptVarietyUnit("Transcript_Gene",
            "Transcript_Gene_Lists", "Ensembl_geneid", "Symbol",
            default_value = "undefined")

    return filters
