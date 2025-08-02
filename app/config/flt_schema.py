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

from app.prepare.prep_filters import FiltersMaster
#===============================================
sAdvanceMode = False

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

FiltersMaster.regNamedFunction("has_variant", sample_has_variant)
FiltersMaster.regNamedFunction("is_none", is_none)

#===============================================
#===============================================
def defineFilterMaster_Case(metadata_record, ds_kind, druid_adm = None):
    assert ds_kind in ("ws", "xl")
    assert (druid_adm is None) == (ds_kind == "ws")
    filters = FiltersMaster(metadata_record, ds_kind, druid_adm = druid_adm)

    cohorts = metadata_record.get("cohorts")
    assert (not cohorts) == (not filters.testRequirements({"COHORTS"}))

    #===============================================
    filters.startViewGroup("Inheritance")
    #===============================================
    filters.multiStatusUnit("Variant_in", "/_filters/cohort_has_variant[]")
    filters.multiStatusUnit("Callers", "/_view/bioinformatics/called_by[]")
    filters.statusUnit("Proband_Zygosity", "/_view/bioinformatics/zygosity")
    filters.intValueUnit("Num_Samples", "/_filters/has_variant",
            conversion = ["len"])
    filters.multiStatusUnit("Has_Variant", "/_filters/has_variant[]")

    if cohorts:
        #===============================================
        filters.startViewGroup("Cohorts")
        #===============================================
        filters.floatValueUnit("ALL_AF", "/_view/cohorts/ALL")
        filters.floatValueUnit("ALL_AF2", "/_view/cohorts/ALL2")
        for ch_info in cohorts:
            cohort = ch_info["name"]
            filters.floatValueUnit(
                f"Cohort_{cohort}_AF", f"/_view/cohorts/{cohort}/AF")
            filters.floatValueUnit(
                f"Cohort_{cohort}_AF2", f"/_view/cohorts/{cohort}/AF2")

    #===============================================
    filters.startViewGroup("Variant")
    #===============================================
    filters.statusUnit(
        "Variant_Class", "/__data/variant_class")
    filters.statusUnit(
        "Most_Severe_Consequence", "/__data/most_severe_consequence")
    filters.multiStatusUnit(
        "Canonical_Annotation", "/_view/general/canonical_annotation[]")
    filters.statusUnit("Multiallelic", "/_filters/multiallelic")
    filters.statusUnit("Altered_VCF", "/_filters/altered_vcf")
    # filters.intValueUnit("Number_ALTs", "/_filters/alts",
    #       conversion = ["len"])
    # filters.intValueUnit("zyg_len", "/__data/zygosity",
    #   conversion = ["len"])

    #===============================================
    filters.startViewGroup("Genes")
    #===============================================
    if sAdvanceMode:
        filters.varietyUnit("_Symbol", "Symbol", "/_view/general/genes[]")
    else:
        genes_unit = filters.multiStatusUnit("Symbol",
            "/_view/general/genes[]", compact_mode = True)
        filters.panelsUnit(genes_unit, "/_view/general/gene_panels")

    filters.multiStatusUnit("EQTL_Gene", "/_filters/eqtl_gene[]")
    filters.intValueUnit("Num_Genes", "/_view/general/genes",
        conversion = ["len"])
    filters.intValueUnit("Num_Transcripts", "/__data/transcript_consequences",
        conversion = ["len"])

    #===============================================
    filters.startViewGroup("Transcripts")
    #===============================================
    filters.transcriptMultisetUnit(
        "Transcript_consequence", "transcript_annotations")
    filters.transcriptStatusUnit("Transcript_canonical", "is_canonical",
        bool_check_value = "True")
    filters.transcriptStatusUnit("Transcript_GENCODE_Basic",
        "gencode_basic", bool_check_value = "True")
    filters.transcriptStatusUnit("Transcript_biotype", "biotype")
    filters.transcriptStatusUnit("Transcript_worst", "is_worst",
        bool_check_value = "True")
    filters.transcriptStatusUnit("Transcript_id", "id")

    if sAdvanceMode:
        filters.transcriptVarietyUnit("Transcript_Gene", "gene")
    else:
        tr_genes_unit = filters.transcriptStatusUnit(
            "Transcript_Gene", "gene")
        filters.transcriptPanelsUnit(tr_genes_unit, "tr_gene_panels")

    filters.transcriptStatusUnit("Transcript_source", "transcript_source")
    filters.transcriptStatusUnit("Transcript_codon_pos", "codonpos")
    filters.transcriptStatusUnit("Transcript_region", "region")
    filters.transcriptStatusUnit("Transcript_CDS", "cds")
    filters.transcriptStatusUnit("Transcript_masked", "masked_region",)
    filters.transcriptIntValueUnit(
        "Transcript_dist_from_exon", "dist_from_exon")
    # filters.transcriptStatusUnit("Transcript_strand", "strand")

    #===============================================
    filters.startViewGroup("Transcript_Predictions")
    #===============================================
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

    filters.startViewGroup("Coordinates")
    filters.statusUnit("Chromosome", "/_filters/chromosome")
    filters.intValueUnit("Start_Pos", "/__data/start")
    filters.intValueUnit("End_Pos", "/__data/end")
    filters.intValueUnit("Dist_from_Exon", "/_filters/dist_from_exon")
    filters.intValueUnit("Dist_from_Exon_Canonical",
        "/_filters/dist_from_exon_canonical", conversion = ["min"])
    filters.intValueUnit("Dist_from_Exon_Worst",
        "/_filters/dist_from_exon_worst", conversion = ["min"])
    filters.multiStatusUnit("Region_Canonical", "/__data/region_canonical[]")
    filters.multiStatusUnit("Region_Worst", "/__data/region_worst[]")
    filters.transcriptStatusUnit("Region", "region")
    filters.statusUnit("In_hg19", "/_view/general/hg19",
        conversion = [["filter", "is_none"]])

    #===============================================
    filters.startViewGroup("gnomAD")
    #===============================================
    filters.floatValueUnit(
        "gnomAD_AF", "/_filters/gnomad_af_fam")
    filters.floatValueUnit(
        "gnomAD_AF_Exomes", "/_filters/gnomad_db_exomes_af")
    filters.floatValueUnit(
        "gnomAD_AF_Genomes", "/_filters/gnomad_db_genomes_af")
    filters.floatValueUnit(
        "gnomAD_AF_Proband", "/_filters/gnomad_af_pb")
    filters.floatValueUnit(
        "gnomAD_PopMax_AF", "/_filters/gnomad_popmax_af")
    filters.statusUnit(
        "gnomAD_PopMax", "/_filters/gnomad_popmax")
    filters.intValueUnit(
        "gnomAD_PopMax_AN", "/_filters/gnomad_popmax_an")
    filters.floatValueUnit(
        "gnomAD_PopMax_AF_Inbred", "/_filters/gnomad_raw_popmax_af")
    filters.statusUnit(
        "gnomAD_PopMax_Inbred", "/_filters/gnomad_raw_popmax")
    filters.intValueUnit(
        "gnomAD_PopMax_AN_Inbred", "/_filters/gnomad_raw_popmax_an")
    filters.intValueUnit("gnomAD_Hom", "/_filters/gnomad_hom")
    filters.intValueUnit("gnomAD_Hem", "/_filters/gnomad_hem")


    #===============================================
    filters.startViewGroup("Databases")
    #===============================================
    clinvarTrusted = filters.getStdItemData(
        "item-dict", "Clinvar_Trusted_Submitters")
    presence_in_db = [
        ("ClinVar", "/_view/databases/clinVar"),
        ("GnomAD", "/_filters/gnomad_af_fam"),
        ("HGMD", "/__data/hgmd_pmids[]"),
        ("OMIM", "/_view/databases/omim")]
    for submitter in sorted(clinvarTrusted.values()):
        presence_in_db.append((submitter,
            f"/_view/databases/clinvar_trusted/{submitter}"))
    filters.presenceUnit("Presence_in_Databases", presence_in_db)
    #===============================================
    filters.multiStatusUnit("ClinVar_Submitters",
        "/_view/databases/clinVar_submitters[]", compact_mode = True)
    filters.intValueUnit("Number_submitters",
        "/_view/databases/clinVar_submitters", conversion = ["len"])

    filters.multiStatusUnit("PMIDs",
        "/_view/databases/references[]", compact_mode = True)
    filters.intValueUnit("Number_pmid",
        "/_view/databases/references", conversion = ["len"])

    # filters.multiStatusUnit("beacons", "/__data/beacon_names")

    #===============================================
    filters.startViewGroup("Call_Quality")
    #===============================================
    filters.floatValueUnit("Proband_GQ", "/_filters/proband_gq")
    filters.floatValueUnit("Min_GQ", "/_filters/min_gq")
    filters.intValueUnit("Max_GQ", "/_view/quality_samples",
        conversion = [
            ["filter", "has_variant"],
            ["property", "genotype_quality"],
            "max"])
    filters.intValueUnit("Num_NO_CALL", "/_view/quality_samples",
        conversion = [
            ["skip", 1],
            ["property", "genotype_quality"],
            "negative", "len"])
    filters.intValueUnit("QUAL", "/_filters/qual")
    filters.floatValueUnit("QD", "/_filters/qd")
    filters.floatValueUnit("FS", "/_filters/fs")
    filters.multiStatusUnit("FT", "/_filters/filters[]")

    #===============================================
    filters.startViewGroup("Predictions")
    #===============================================
    # research_only = True
    filters.statusUnit("HGMD_Benign", "/_filters/hgmd_benign")
    filters.multiStatusUnit("HGMD_Tags", "/_view/databases/hgmd_tags[]")
    # research_only = True
    filters.statusUnit("Clinvar_Benign", "/_filters/clinvar_benign")
    filters.multiStatusUnit(
        "ClinVar_Significance", "/__data/clinvar_significance[]")

    filters.regPreTransform(lambda rec_no, rec_data:
        clinvarPreTransform(rec_data, clinvarTrusted))

    filters.multiStatusUnit("Clinvar_Trusted_Significance",
        "/_view/databases/clinvar_trusted",
        conversion = ["values", ["split", ','], "clear", "uniq"])
    filters.multiStatusUnit("Clinvar_Trusted_Simplified",
        "/_view/databases/clinvar_trusted_simplified",
        conversion = ["values", ["split", ','], "clear", "uniq"])

    filters.statusUnit(
        "Clinvar_stars", "/_filters/clinvar_stars")
    filters.intValueUnit(
        "Number_of_clinvar_submitters", "/_filters/num_clinvar_submitters")
    filters.statusUnit(
        "Clinvar_review_status", "/_filters/clinvar_review_status")
    filters.statusUnit(
        "Clinvar_criteria_provided", "/_filters/clinvar_criteria_provided")
    filters.statusUnit(
        "Clinvar_conflicts", "/_filters/clinvar_conflicts")
    filters.multiStatusUnit(
        "Clinvar_acmg_guidelines", "/_filters/clinvar_acmg_guidelines[]")

    for submitter in sorted(clinvarTrusted.values()):
        filters.statusUnit(f"ClinVar_Significance_{submitter}",
            "/_view/databases/clinvar_trusted",
            conversion = [["property", submitter]])

    #filters.statusUnit(
    #   "Clinvar_Trusted_Benign", "/_filters/clinvar_trusted_benign")

    filters.statusUnit("splice_altering", "/_filters/splice_altering")
    filters.floatValueUnit("splice_ai_dsmax", "/_filters/splice_ai_dsmax")

    filters.multiStatusUnit(
        "Polyphen_2_HVAR", "/_view/predictions/polyphen2_hvar[]",
        conversion = [["split_re", r"[\s\,]"], "clear", "uniq"])
    filters.multiStatusUnit(
        "Polyphen_2_HDIV", "/_view/predictions/polyphen2_hdiv[]",
        conversion = [["split_re", r"[\s\,]"], "clear", "uniq"])

    filters.multiStatusUnit("SIFT", "/_view/predictions/sift[]")
    filters.multiStatusUnit("FATHMM", "/_view/predictions/fathmm[]")
    filters.multiStatusUnit(
        "PrimateAI", "/_view/predictions/primate_ai_pred[]")
    filters.floatValueUnit(
        "GERP_score", "/_view/bioinformatics/gerp_rs")

    #===============================================
    filters.startViewGroup("Pharmacogenomics")
    #===============================================
    filters.multiStatusUnit(
        "Diseases", "/_filters/pharmacogenomics_diseases[]")
    filters.multiStatusUnit(
        "Chemicals", "/_filters/pharmacogenomics_chemicals[]")

    #===============================================
    filters.startViewGroup("Expression")
    #===============================================
    filters.multiStatusUnit(
        "Mostly_Expressed_in", "/_filters/top_tissues[]")

    # requires = {"debug"}
    #===============================================
    filters.startViewGroup("Debug_Info")
    #===============================================
    filters.intValueUnit("Severity", "/_filters/severity")

    filters.standUp()

    return filters
