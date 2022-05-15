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
from .variables import anfisaVariables
from .favor import FavorSchema
#===============================================
#===============================================
sAdvanceMode = False

sConsequenceVariants = [
    "transcript_ablation",
    "splice_acceptor_variant",
    "splice_donor_variant",
    "stop_gained",
    "frameshift_variant",
    "stop_lost",
    "start_lost",
    "transcript_amplification",
    "inframe_insertion",
    "inframe_deletion",
    "missense_variant",
    "protein_altering_variant",
    "incomplete_terminal_codon_variant",
    "stop_retained_variant",
    "synonymous_variant",
    "splice_region_variant",
    "coding_sequence_variant",
    "mature_miRNA_variant",
    "5_prime_UTR_variant",
    "3_prime_UTR_variant",
    "non_coding_transcript_exon_variant",
    "intron_variant",
    "NMD_transcript_variant",
    "non_coding_transcript_variant",
    "upstream_gene_variant",
    "downstream_gene_variant",
    "TFBS_ablation",
    "TFBS_amplification",
    "TF_binding_site_variant",
    "regulatory_region_ablation",
    "regulatory_region_amplification",
    "feature_elongation",
    "regulatory_region_variant",
    "feature_truncation",
    "intergenic_variant",
    "undefined"]

#===============================================
def clinvarPreTransform(rec_data, trusted_map):
    clinvar_submit_data = rec_data["_view"][
        "databases"].get("clinVar_submitters")
    if not clinvar_submit_data:
        return
    clinvar_trusted = dict()
    clinvar_trusted_simplified = dict()
    for descr in clinvar_submit_data:
        submitter, _, status = descr.partition(':')
        submitter = submitter.strip()
        if submitter in trusted_map:
            value = status.strip().lower()
            if value.startswith('{') and value.endswith('}'):
                value = value[1:-1]
            clinvar_trusted[trusted_map[submitter]] = value
            if "uncertain" in value:
                s_value = "uncertain"
            elif "pathogen" in value:
                s_value = "pathogenic"
            elif "benign" in value:
                s_value = "benign"
            else:
                s_value = "other"
            clinvar_trusted_simplified[trusted_map[submitter]] = s_value
    rec_data["_view"]["databases"]["clinvar_trusted"] = clinvar_trusted
    rec_data["_view"]["databases"]["clinvar_trusted_simplified"] = (
        clinvar_trusted_simplified)

#===============================================
def sample_has_variant(sample):
    genotype = sample.get("genotype")
    return genotype and not ("HOM_REF" in genotype or "NO_CALL" in genotype)

def is_none(value):
    return value == "None"


FilterPrepareSetH.regNamedFunction("has_variant", sample_has_variant)
FilterPrepareSetH.regNamedFunction("is_none", is_none)
#===============================================
def defineFilterSchema(metadata_record, ds_kind, derived_mode = False):
    data_schema = metadata_record.get("data_schema")
    if data_schema == "FAVOR":
        return FavorSchema.defineFilterSchema(metadata_record,
            ds_kind, derived_mode)
    assert data_schema is None or data_schema == "CASE", (
        "Bad data schema: " + data_schema)

    filters = FilterPrepareSetH(metadata_record, anfisaVariables,
        ds_kind, derived_mode = derived_mode)

    cohorts = metadata_record.get("cohorts")
    with filters.viewGroup("Inheritance"):
        if cohorts:
            filters.multiStatusUnit("Variant_in",
                "/_filters/cohort_has_variant[]")
        filters.multiStatusUnit("Callers",
            "/_view/bioinformatics/called_by[]")
        filters.statusUnit("Proband_Zygosity",
            "/_view/bioinformatics/zygosity",
            requires = {"PROBAND"})
        filters.intValueUnit("Num_Samples", "/_filters/has_variant",
            conversion = ["len"], default_value = 0)
        filters.multiStatusUnit("Has_Variant", "/_filters/has_variant[]")

    if cohorts:
        with filters.viewGroup("Cohorts"):
            filters.floatValueUnit("ALL_AF",
                "/_view/cohorts/ALL", default_value = 0)
            filters.floatValueUnit("ALL_AF2",
                "/_view/cohorts/ALL2", default_value = 0)
            for ch_info in cohorts:
                ch_name = ch_info["name"]
                filters.floatValueUnit(f"Cohort_{ch_name}_AF",
                    f"/_view/cohorts/{ch_name}/AF",
                    default_value = 0)
                filters.floatValueUnit(f"Cohort_{ch_name}_AF2",
                    f"/_view/cohorts/{ch_name}/AF2",
                    default_value = 0)

    with filters.viewGroup("Variant"):
        filters.statusUnit("Variant_Class", "/__data/variant_class")
        filters.statusUnit("Most_Severe_Consequence",
               "/__data/most_severe_consequence",
               variants = sConsequenceVariants,
               default_value = "undefined")
        filters.multiStatusUnit("Canonical_Annotation",
            "/_view/general/canonical_annotation[]",
            default_value = "undefined")
        filters.statusUnit("Multiallelic", "/_filters/multiallelic")
        filters.statusUnit("Altered_VCF", "/_filters/altered_vcf")
        # filters.intValueUnit("Number_ALTs",
        #     "/_filters/alts",
        #     conversion = ["len"], default_value = 0)

        #filters.intValueUnit("zyg_len", "/__data/zygosity",
        #   conversion = ["len"], default_value = 0)

    with filters.viewGroup("Genes"):
        if sAdvanceMode:
            filters.varietyUnit("_Symbol", "Symbol", "Panels",
                "/_view/general/genes[]", "Symbol", dim_name = "Symbol")
        else:
            genes_unit = filters.multiStatusUnit("Symbol",
                "/_view/general/genes[]", compact_mode = True)
            filters.panelsUnit("Panels", genes_unit, "Symbol",
                view_path = "/_view/general/gene_panels")

        filters.multiStatusUnit("EQTL_Gene", "/_filters/eqtl_gene[]",
            default_value = "None")
        filters.intValueUnit("Num_Genes", "/_view/general/genes",
            conversion = ["len"], default_value = 0)
        filters.intValueUnit("Num_Transcripts",
            "/__data/transcript_consequences",
            conversion = ["len"], default_value = 0)

    with filters.viewGroup("Transcripts"):
        filters.transcriptMultisetUnit("Transcript_consequence",
            "transcript_annotations", variants = sConsequenceVariants,
            default_value = "undefined")
        filters.transcriptStatusUnit("Transcript_canonical", "is_canonical",
            bool_check_value = "True", default_value = "False")
        filters.transcriptStatusUnit("Transcript_GENCODE_Basic",
            "gencode_basic", bool_check_value = "True",
            default_value = "False")
        filters.transcriptStatusUnit("Transcript_biotype", "biotype",
            default_value = "undefined")
        filters.transcriptStatusUnit("Transcript_worst", "is_worst",
            bool_check_value = "True", default_value = "False")
        filters.transcriptStatusUnit("Transcript_id", "id",
            default_value = "undefined", transcript_id_mode = True)

        if sAdvanceMode:
            filters.transcriptVarietyUnit("Transcript_Gene",
                "Transcript_Gene_Panels", "gene", "Symbol",
                default_value = "undefined", dim_name = "Symbol")
        else:
            tr_genes_unit = filters.transcriptStatusUnit("Transctript_Gene",
                "gene", default_value = "undefined")
            filters.transcriptPanelsUnit("Transcript_Gene_Panels",
                tr_genes_unit, "Symbol", view_name = "tr_gene_panels")

        filters.transcriptStatusUnit("Transcript_source", "transcript_source",
            default_value = "undefined")
        filters.transcriptStatusUnit("Transcript_codon_pos", "codonpos",
            default_value = "undefined")
        filters.transcriptStatusUnit("Transcript_region", "region",
            default_value = "undefined")
        filters.transcriptStatusUnit("Transcript_CDS", "cds",
            default_value = "-")
        filters.transcriptStatusUnit("Transcript_masked", "masked_region",
            default_value = "No")
        filters.transcriptIntValueUnit("Transcript_dist_from_exon",
            "dist_from_exon", default_value = -1)
        # filters.transcriptStatusUnit("Transcript_strand", "strand",
        #     default_value = "undefined")

    with filters.viewGroup("Transcript_Predictions"):
        filters.transcriptStatusUnit(
            "Transcript_PolypPhen_HDIV", "polyphen2_hdiv_prediction")
        filters.transcriptStatusUnit(
            "Transcript_PolyPhen_HVAR", "polyphen2_hvar_prediction")
        filters.transcriptStatusUnit(
            "Transcript_SIFT", "sift_prediction")
        filters.transcriptStatusUnit(
            "Transcript_SIFT_4G", "sift_4g_prediction")
        filters.transcriptStatusUnit(
            "Transcript_FATHMM", "fathmm_prediction")

    with filters.viewGroup("Coordinates"):
        filters.statusUnit("Chromosome", "/_filters/chromosome",
            variants = ["chr1", "chr2", "chr3", "chr4", "chr5",
            "chr6", "chr7", "chr8", "chr9", "chr10",
            "chr11", "chr12", "chr13", "chr14", "chr15",
            "chr16", "chr17", "chr18", "chr19", "chr20",
            "chr21", "chr22", "chr23", "chrX", "chrY", "undefined"],
            default_value = "undefined")

        filters.intValueUnit("Start_Pos", "/__data/start",
            default_value = sys.maxsize)
        filters.intValueUnit("End_Pos", "/__data/end",
            default_value = 0)
        filters.intValueUnit("Dist_from_Exon", "/_filters/dist_from_exon",
            default_value = 0)
        filters.intValueUnit("Dist_from_Exon_Canonical",
            "/_filters/dist_from_exon_canonical",
            default_value = 0, conversion = ["min"])
        filters.intValueUnit("Dist_from_Exon_Worst",
            "/_filters/dist_from_exon_worst",
            default_value = 0, conversion = ["min"])
        filters.multiStatusUnit("Region_Canonical",
            "/__data/region_canonical[]",
            default_value = "Other")
        filters.multiStatusUnit("Region_Worst", "/__data/region_worst[]",
            default_value = "Other")
        filters.transcriptStatusUnit("Region", "region",
                                     default_value = "undefined")
        filters.statusUnit("In_hg19", "/_view/general/hg19",
            conversion = [["filter", "is_none"]],
            value_map= {"None": "Unmapped"}, default_value = "Mapped")

    with filters.viewGroup("gnomAD"):
        filters.floatValueUnit("gnomAD_AF",
            "/_filters/gnomad_af_fam",
            diap = (0., 1.), default_value = 0.)
        filters.floatValueUnit("gnomAD_AF_Exomes",
            "/_filters/gnomad_db_exomes_af",
            diap = (0., 1.), default_value = 0.)
        filters.floatValueUnit("gnomAD_AF_Genomes",
            "/_filters/gnomad_db_genomes_af",
            diap = (0., 1.), default_value = 0.)
        filters.floatValueUnit("gnomAD_AF_Proband",
            "/_filters/gnomad_af_pb",
            diap = (0., 1.), default_value = 0.,
            requires = {"PROBAND"})
        filters.floatValueUnit("gnomAD_PopMax_AF",
            "/_filters/gnomad_popmax_af",
            diap = (0., 1.), default_value = 0.)
        filters.statusUnit("gnomAD_PopMax",
            "/_filters/gnomad_popmax", default_value = "None")
        filters.intValueUnit("gnomAD_PopMax_AN",
            "/_filters/gnomad_popmax_an", default_value = 0)
        filters.floatValueUnit("gnomAD_PopMax_AF_Inbred",
            "/_filters/gnomad_raw_popmax_af",
            diap = (0., 1.), default_value = 0.)
        filters.statusUnit("gnomAD_PopMax_Inbred",
            "/_filters/gnomad_raw_popmax", default_value = "None")
        filters.intValueUnit("gnomAD_PopMax_AN_Inbred",
            "/_filters/gnomad_raw_popmax_an", default_value = 0)
        filters.intValueUnit("gnomAD_Hom",
            "/_filters/gnomad_hom", default_value = 0)
        filters.intValueUnit("gnomAD_Hem",
            "/_filters/gnomad_hem", default_value = 0)

    with filters.viewGroup("Databases"):
        presence_in_db = [
            ("ClinVar", "/_view/databases/clinVar"),
            ("GnomAD", "/_filters/gnomad_af_fam"),
            ("HGMD", "/__data/hgmd_pmids[]"),
            ("OMIM", "/_view/databases/omim")]
        for submitter in sorted(filters.getStdItem(
                "item-dict", "Clinvar_Trusted_Submitters").getData().values()):
            presence_in_db.append((submitter,
                "/_view/databases/clinvar_trusted/%s" % submitter))
        filters.presenceUnit("Presence_in_Databases", presence_in_db)

        filters.multiStatusUnit("ClinVar_Submitters",
            "/_view/databases/clinVar_submitters[]", compact_mode = True)
        filters.intValueUnit("Number_submitters",
            "/_view/databases/clinVar_submitters",
            conversion = ["len"], default_value = 0)

        filters.multiStatusUnit("PMIDs",
            "/_view/databases/references[]", compact_mode = True)
        filters.intValueUnit("Number_pmid",
            "/_view/databases/references",
            conversion = ["len"], default_value = 0)

        # filters.multiStatusUnit("beacons",
        #     "/__data/beacon_names")

    with filters.viewGroup("Call_Quality"):
        filters.floatValueUnit("Proband_GQ", "/_filters/proband_gq",
            default_value = -1, requires = {"PROBAND"})
        filters.floatValueUnit("Min_GQ", "/_filters/min_gq",
            default_value = -1)
        filters.intValueUnit("Max_GQ", "/_view/quality_samples",
            default_value = 0,
            conversion = [
                ["filter", "has_variant"],
                ["property", "genotype_quality"],
                "max"])

        filters.intValueUnit("Num_NO_CALL", "/_view/quality_samples",
            default_value = 0,
            conversion = [
                ["skip", 1],
                ["property", "genotype_quality"],
                "negative", "len"])
        filters.intValueUnit("QUAL", "/_filters/qual",
            default_value = -1)
        filters.floatValueUnit("QD", "/_filters/qd",
            default_value = -1.)
        filters.floatValueUnit("FS", "/_filters/fs",
            default_value = 0.)
        filters.multiStatusUnit("FT", "/_filters/filters[]")

    with filters.viewGroup("Predictions"):
        # research_only = True
        filters.statusUnit("HGMD_Benign", "/_filters/hgmd_benign",
            default_value = "Not in HGMD",
            value_map = {"True": "Benign", "False": "VUS or Pathogenic"})
        filters.multiStatusUnit("HGMD_Tags", "/_view/databases/hgmd_tags[]",
            default_value = "None")

        # research_only = True
        filters.statusUnit("Clinvar_Benign", "/_filters/clinvar_benign",
            default_value = "Not in ClinVar",
            value_map = {"True": "Benign", "False": "VUS or Pathogenic"})
        filters.multiStatusUnit("ClinVar_Significance",
            "/__data/clinvar_significance[]")
        filters.regPreTransform(lambda rec_no, rec_data:
            clinvarPreTransform(rec_data, filters.getStdItem(
                "item-dict", "Clinvar_Trusted_Submitters").getData()))

        filters.multiStatusUnit("Clinvar_Trusted_Significance",
            "/_view/databases/clinvar_trusted",
            conversion = ["values", ["split", ','], "clear", "uniq"])
        filters.multiStatusUnit("Clinvar_Trusted_Simplified",
            "/_view/databases/clinvar_trusted_simplified",
            conversion = ["values", ["split", ','], "clear", "uniq"])

        filters.statusUnit("Clinvar_stars", "/_filters/clinvar_stars",
            default_value = "No data")
        filters.intValueUnit("Number_of_clinvar_submitters",
            "/_filters/num_clinvar_submitters",
            default_value = 0)
        filters.statusUnit("Clinvar_review_status",
            "/_filters/clinvar_review_status",
            default_value = "No data")
        filters.statusUnit("Clinvar_criteria_provided",
            "/_filters/clinvar_criteria_provided",
            default_value = "Not Provided")
        filters.statusUnit("Clinvar_conflicts",
            "/_filters/clinvar_conflicts",
            default_value = "Criteria not Provided")
        filters.multiStatusUnit("Clinvar_acmg_guidelines",
            "/_filters/clinvar_acmg_guidelines[]",
            default_value = "None")

        for submitter in sorted(filters.getStdItem(
                "item-dict", "Clinvar_Trusted_Submitters").getData().values()):
            filters.statusUnit(f"ClinVar_Significance_{submitter}",
                "/_view/databases/clinvar_trusted",
                conversion = [["property", submitter]],
                default_value = "None")

        #filters.statusUnit("Clinvar_Trusted_Benign",
        #    "/_filters/clinvar_trusted_benign",
        #    default_value = "No data",
        #    value_map = {"True": "Benign by Trusted submitters",
        #        "False": "Unknown"})

        filters.statusUnit("splice_altering", "/_filters/splice_altering",
            default_value = "No altering")
        filters.floatValueUnit("splice_ai_dsmax", "/_filters/splice_ai_dsmax",
            default_value = 0)

        filters.multiStatusUnit("Polyphen_2_HVAR",
            "/_view/predictions/polyphen2_hvar[]",
            conversion = [["split_re", r"[\s\,]"], "clear", "uniq"],
            default_value = "N/A")
        filters.multiStatusUnit("Polyphen_2_HDIV",
            "/_view/predictions/polyphen2_hdiv[]",
            conversion = [["split_re", r"[\s\,]"], "clear", "uniq"],
            default_value = "N/A")

        filters.multiStatusUnit("SIFT", "/_view/predictions/sift[]",
            default_value = "N/A")
        filters.multiStatusUnit("FATHMM", "/_view/predictions/fathmm[]",
            default_value = "N/A")
        filters.multiStatusUnit("PrimateAI",
            "/_view/predictions/primate_ai_pred[]",
            default_value = "N/A")
        filters.floatValueUnit("GERP_score", "/_view/bioinformatics/gerp_rs",
            default_value = 0)

    with filters.viewGroup("Pharmacogenomics"):
        filters.multiStatusUnit("Diseases",
            "/_filters/pharmacogenomics_diseases[]", default_value = "N/A")
        filters.multiStatusUnit("Chemicals",
            "/_filters/pharmacogenomics_chemicals[]", default_value = "N/A")

    with filters.viewGroup("Expression"):
        filters.multiStatusUnit("Mostly_Expressed_in",
            "/_filters/top_tissues[]", default_value = "N/A")

    # requires = {"debug"}
    with filters.viewGroup("Debug_Info"):
        filters.intValueUnit("Severity", "/_filters/severity",
            default_value = -1)

    assert filters.getTranscriptIdUnitName() is not None, (
        "Transcript ID unit is not set")

    return filters
