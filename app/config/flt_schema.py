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
from .favor import FavorSchema
#===============================================
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
def defineFilterSchema(metadata_record):
    data_schema = metadata_record.get("data_schema")
    if data_schema == "FAVOR":
        return FavorSchema.defineFilterSchema(metadata_record)
    assert data_schema is None or data_schema == "CASE", (
        "Bad data schema: " + data_schema)

    filters = FilterPrepareSetH(metadata_record)

    cohorts = metadata_record.get("cohorts")
    with filters.viewGroup("Inheritance"):
        if cohorts:
            filters.multiStatusUnit("Variant_in",
                "/_filters/cohort_has_variant[]")
        filters.multiStatusUnit("Callers", "/_view/bioinformatics/called_by[]",
            title = "Called by")
        filters.statusUnit("Proband_Zygosity",
            "/_view/bioinformatics/zygosity",
            title = "Proband Zygosity")
        filters.intValueUnit("Num_Samples", "/_filters/has_variant",
            title = "Number of Samples",
            conversion = ["len"], default_value = 0,
            tooltip =
            "Number of samples for which this variant has been called")
        filters.multiStatusUnit("Has_Variant", "/_filters/has_variant[]")

    if cohorts:
        all_cohorts = ["ALL"] + [ch["name"] for ch in cohorts]
        with filters.viewGroup("Cohorts"):
            for ch_name in all_cohorts:
                filters.floatValueUnit(ch_name + "_AF",
                    "/_view/cohorts/" + ch_name + "/AF",
                    default_value = 0)
                filters.floatValueUnit(ch_name + "_AF2",
                    "/_view/cohorts/" + ch_name + "/AF2",
                    default_value = 0, title = "AF_Hom")

    with filters.viewGroup("Variant"):
        filters.statusUnit("Variant_Class", "/__data/variant_class",
            tooltip = ("Variant class as returned by VEP. "
                "The class of a variant is based on Sequence "
                "Ontology and is called according to its component "
                "alleles and its mapping to the reference genome. "
                "https://useast.ensembl.org/info/genome/variation/"
                "prediction/classification.html#classes"))
        filters.statusUnit("Most_Severe_Consequence",
               "/__data/most_severe_consequence",
               variants = sConsequenceVariants,
               default_value = "undefined")
        filters.multiStatusUnit("Canonical_Annotation",
            "/_view/general/canonical_annotation[]",
            default_value = "undefined")
        filters.statusUnit("Multiallelic", "/_filters/multiallelic",
            title = "Multi-allelic?")
        filters.statusUnit("Altered_VCF", "/_filters/altered_vcf",
            title = "Has VCF been normalized?")
        # filters.intValueUnit("Number_ALTs",
        #     "/_filters/alts",
        #     title = "Number of Alternative alleles",
        #     conversion = ["len"], default_value = 0)

        #filters.intValueUnit("zyg_len", "/__data/zygosity",
        #   conversion = ["len"], default_value = 0)

    with filters.viewGroup("Genes"):
        genes_unit = filters.multiStatusUnit("Symbol",
            "/_view/general/genes[]",
            compact_mode = True)
        filters.panelsUnit("Panels", genes_unit, "Symbol",
            view_path = "/_view/general/gene_panels")
        filters.multiStatusUnit("EQTL_Gene", "/_filters/eqtl_gene[]",
            title = "EQTL Gene", default_value = "None")
        #filters.multiStatusUnit("Transcripts",
        #    "/__data/transcript_consequences[]", compact_mode = True,
        #    conversion = [["property", transcript_id"]])
        filters.intValueUnit("Num_Genes", "/_view/general/genes",
            title = "Number of overlapping genes",
            conversion = ["len"], default_value = 0)
        filters.intValueUnit("Num_Transcripts",
            "/__data/transcript_consequences",
            title = "Number of transcripts at the position",
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
            default_value = "undefined")
        tr_genes_unit = filters.transcriptStatusUnit("Transctript_Gene",
            "gene", default_value = "undefined")
        filters.transcriptPanelsUnit("Transcript_Gene_Panels",
            tr_genes_unit, "Symbol", view_name = "tr_gene_panels")
        filters.transcriptStatusUnit("Transcript_source", "transcript_source",
            default_value = "undefined")
        filters.transcriptStatusUnit("Transcript_codon_pos", "codonpos",
            default_value = "undefined")
        filters.transcriptStatusUnit("Transcript_region", "region",
            title= "Gene Region", default_value = "undefined")
        filters.transcriptStatusUnit("Transcript_CDS", "cds",
            title= "CDS?", default_value = "-")
        filters.transcriptStatusUnit("Transcript_masked", "masked_region",
            title= "Masked", default_value = "No")
        filters.transcriptIntValueUnit("Transcript_dist_from_exon",
            "dist_from_exon",
            title = "Distance from Exon Boundary", default_value = -1)
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

    # with filters.viewGroup("Transcripts"):
    #     filters.transcriptMultisetUnit("Transcript_consequence",
    #         "consequence_terms", variants = sConsequenceVariants,
    #         default_value = "undefined")
    #     filters.transcriptStatusUnit("Transcript_canonical", "canonical",
    #         bool_check_value = "1", default_value = "False")
    #     filters.transcriptStatusUnit("Transcript_biotype", "biotype",
    #         default_value = "undefined")
    #     filters.transcriptStatusUnit("Transcript_worst", "consequence_terms",
    #         bool_check_value = "${Most_Severe_Consequence}",
    #         default_value = "False")
    #     filters.transcriptStatusUnit("Transcript_id", "transcript_id",
    #         default_value = "undefined")
    #     filters.transcriptStatusUnit("Transctript_gene_id", "gene_id",
    #         default_value = "undefined")
    #     filters.transcriptStatusUnit("Transcript_source", "source",
    #         default_value = "undefined")
    #     filters.transcriptStatusUnit("Transcript_strand", "strand",
    #         default_value = "undefined")

    with filters.viewGroup("Coordinates"):
        filters.statusUnit("Chromosome", "/_filters/chromosome",
            variants = ["chr1", "chr2", "chr3", "chr4", "chr5",
            "chr6", "chr7", "chr8", "chr9", "chr10",
            "chr11", "chr12", "chr13", "chr14", "chr15",
            "chr16", "chr17", "chr18", "chr19", "chr20",
            "chr21", "chr22", "chr23", "chrX", "chrY", "undefined"],
            default_value = "undefined")

        filters.intValueUnit("Start_Pos", "/__data/start",
            title = "Start Position",
            render_mode = "neighborhood", default_value = sys.maxsize)
        filters.intValueUnit("End_Pos", "/__data/end",
            title = "End Position", default_value = 0,
            render_mode = "neighborhood")
        filters.intValueUnit("Dist_from_Exon", "/_filters/dist_from_exon",
            title = "Distance From Intron/Exon Boundary (Canonical)",
            default_value = 0, render_mode = "log,<")
        filters.intValueUnit("Dist_from_Exon_Canonical",
            "/_filters/dist_from_exon_canonical",
            title = "Distance From Intron/Exon Boundary (Canonical)",
            default_value = 0, render_mode = "log,<", conversion = ["min"])
        filters.intValueUnit("Dist_from_Exon_Worst",
            "/_filters/dist_from_exon_worst",
            title = "Distance From Intron/Exon Boundary (Canonical)",
            default_value = 0, render_mode = "log,<", conversion = ["min"])
        filters.multiStatusUnit("Region_Canonical",
            "/__data/region_canonical[]",
            title = "Region (Canonical)", default_value = "Other")
        filters.multiStatusUnit("Region_Worst", "/__data/region_worst[]",
            title = "Region (Canonical)", default_value = "Other")
        filters.statusUnit("Region", "/__data/region_canonical",
            title = "Region (Legacy)", default_value = "Other", )
        filters.statusUnit("hg19", "/_view/general/hg19", title = "HG19",
            conversion = [["filter", "is_none"]],
            value_map= {"None": "Unmapped"}, default_value = "Mapped")

    with filters.viewGroup("gnomAD"):
        filters.floatValueUnit("gnomAD_AF",
            "/_filters/gnomad_af_fam",
            diap = (0., 1.), default_value = 0.,
            title = "gnomAD Allele Frequency (family)",
            tooltip = "gnomAD Overall Allele Frequency",
            render_mode = "log,<")
        filters.floatValueUnit("gnomAD_AF_Exomes",
            "/_filters/gnomad_db_exomes_af",
            diap = (0., 1.), default_value = 0.,
            title = "gnomAD Exome Allele Frequency (family)",
            render_mode = "log,<")
        filters.floatValueUnit("gnomAD_AF_Genomes",
            "/_filters/gnomad_db_genomes_af",
            diap = (0., 1.), default_value = 0.,
            title = "gnomAD Genome Allele Frequency (family)",
            render_mode = "log,<")
        filters.floatValueUnit("gnomAD_AF_Proband",
            "/_filters/gnomad_af_pb",
            diap = (0., 1.), default_value = 0.,
            title = "gnomAD Allele Frequency (proband)",
            tooltip = "gnomAD Overall Allele Frequency "
            "for the allele present in proband",
            render_mode = "log,<")
        filters.floatValueUnit("gnomAD_PopMax_AF",
            "/_filters/gnomad_popmax_af",
            tooltip = "Maximum allele frequency across outbred populations",
            diap = (0., 1.), default_value = 0.,
            title = "PopMax Allele Frequency",
            render_mode = "log,<")
        filters.statusUnit("gnomAD_PopMax",
            "/_filters/gnomad_popmax", default_value = "None",
            title = "PopMax Ancestry",
            tooltip =
                "Outbred population that has the maximum allele frequency")
        filters.intValueUnit("gnomAD_PopMax_AN",
            "/_filters/gnomad_popmax_an",
            default_value = 0,
            title = "Number of alleles in outbred PopMax Ancestry",
            render_mode = "log,>")
        filters.floatValueUnit("gnomAD_PopMax_AF_Inbred",
            "/_filters/gnomad_raw_popmax_af",
            tooltip = "Maximum allele frequency across all populations "
                      + "(including inbred)",
            diap = (0., 1.), default_value = 0.,
            title = "PopMax Allele Frequency (including inbred)",
            render_mode = "log,<")
        filters.statusUnit("gnomAD_PopMax_Inbred",
            "/_filters/gnomad_raw_popmax", default_value = "None",
            title = "PopMax Ancestry (including inbred)",
            tooltip = "Population, including inbred, that has the maximum "
                      + "allele frequency")
        filters.intValueUnit("gnomAD_PopMax_AN_Inbred",
            "/_filters/gnomad_raw_popmax_an",
            default_value = 0, render_mode = "log,>",
            title = "Number of alleles in (inbred) PopMax Ancestry")
        filters.intValueUnit("gnomAD_Hom",
            "/_filters/gnomad_hom",
            default_value = 0, render_mode = "log,>",
            title = "gnomAD: Number of homozygous")
        filters.intValueUnit("gnomAD_Hem",
            "/_filters/gnomad_hem",
            default_value = 0, render_mode = "log,>",
            title = "gnomAD: Number of hemizygous")

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
        filters.presenceUnit("Presence_in_Databases", presence_in_db,
            title = "Presence in Databases")

        filters.multiStatusUnit("ClinVar_Submitters",
            "/_view/databases/clinVar_submitters[]",
            title = "ClinVar Submitters", compact_mode = True)
        filters.intValueUnit("Number_submitters",
            "/_view/databases/clinVar_submitters",
            title = "Number of ClinVar Submitters",
            conversion = ["len"], default_value = 0)

        filters.multiStatusUnit("PMIDs",
            "/_view/databases/references[]",
            title = "PMIDs", compact_mode = True)
        filters.intValueUnit("Number_pmid",
            "/_view/databases/references",
            title = "Number of PMIDs",
            conversion = ["len"], default_value = 0)

        # filters.multiStatusUnit("beacons",
        #     "/__data/beacon_names",
        #     title = "Observed at")

    with filters.viewGroup("Call_Quality"):
        filters.floatValueUnit("Proband_GQ", "/_filters/proband_gq",
            title = "Genotype Quality (GQ) for Proband",
            render_mode = "linear,>", default_value = -1,
            tooltip = "GQ tells you how confident we are that "
            "the genotype we assigned to a particular sample is correct. "
            "It is simply the second lowest PL, because it is the "
            "difference between the second lowest PL and the lowest PL "
            "(always 0).")
        filters.floatValueUnit("Min_GQ", "/_filters/min_gq",
            title = "Minimum GQ for the family", render_mode = "linear,>",
            default_value = -1,
            tooltip = "GQ tells you how confident we are that "
            "the genotype we assigned to a particular sample is correct. "
            "It is simply the second lowest PL, because it is the "
            "difference between the second lowest PL and the lowest PL "
            "(always 0).")
        filters.intValueUnit("Max_GQ", "/_view/quality_samples",
            title = "The highest GQ",
            tooltip= "Max(GQ) for those samples that have the variant",
            render_mode = "linear,=", default_value = 0,
            conversion = [
                ["filter", "has_variant"],
                ["property", "genotype_quality"],
                "max"])

        filters.intValueUnit("Num_NO_CALL", "/_view/quality_samples",
            title = "Number of NO_CALL samples",
            tooltip= "Number of samples with NO_CALL in the current site",
            render_mode = "linear,=", default_value = 0,
            conversion = [
                ["skip", 1],
                ["property", "genotype_quality"],
                "negative", "len"])
        filters.intValueUnit("QUAL", "/_filters/qual",
            title = "Variant Call Quality",
            default_value = -1)
        filters.floatValueUnit("QD", "/_filters/qd",
            title = "Quality by Depth",
            render_mode = "linear,>", default_value = -1.,
            tooltip = "The QUAL score normalized by allele depth (AD) "
            "for a variant. This annotation puts the variant confidence "
            "QUAL score into perspective by normalizing for the amount "
            "of coverage available. Because each read contributes a little "
            "to the QUAL score, variants in regions with deep coverage "
            "can have artificially inflated QUAL scores, giving the "
            "impression that the call is supported by more evidence "
            "than it really is. To compensate for this, we normalize "
            "the variant confidence by depth, which gives us a more "
            "objective picture of how well supported the call is.")
        filters.floatValueUnit("FS", "/_filters/fs",
            title = "Fisher Strand Bias",
            render_mode = "linear,<", default_value = 0.,
            tooltip = "Phred-scaled probability that there is strand bias "
            "at the site. Strand Bias tells us whether the alternate "
            "allele was seen more or less often on the forward or "
            "reverse strand than the reference allele. When there "
            "little to no strand bias at the site, the FS value "
            "will be close to 0.")
        filters.multiStatusUnit("FT", "/_filters/filters[]", title = "FILTER",
            tooltip = "This field contains the name(s) of any filter(s) "
            "that the variant fails to pass, or the value PASS if the "
            "variant passed all filters. If the FILTER value is ., "
            "then no filtering has been applied to the records.")

    with filters.viewGroup("Predictions"):
        # research_only = True
        filters.statusUnit("HGMD_Benign", "/_filters/hgmd_benign",
            title = "Categorized Benign in HGMD",
            default_value = "Not in HGMD",
            value_map = {"True": "Benign", "False": "VUS or Pathogenic"})
        filters.multiStatusUnit("HGMD_Tags", "/_view/databases/hgmd_tags[]",
            default_value = "None")

        # research_only = True
        filters.statusUnit("Clinvar_Benign", "/_filters/clinvar_benign",
            default_value = "Not in ClinVar",
            title = "Categorized Benign in ClinVar by all submitters",
            value_map = {"True": "Benign", "False": "VUS or Pathogenic"})
        filters.multiStatusUnit("ClinVar_Significance",
            "/__data/clinvar_significance[]",
            title = "Clinical Significance in ClinVar")
        filters.regPreTransform(lambda rec_no, rec_data:
            clinvarPreTransform(rec_data, filters.getStdItem(
                "item-dict", "Clinvar_Trusted_Submitters").getData()))

        filters.multiStatusUnit("Clinvar_Trusted_Significance",
            "/_view/databases/clinvar_trusted",
            title = "ClinVar significance by trusted submitters only",
            tooltip =
                "Clinical Significance by ClinVar trusted submitters only",
            conversion = ["values", ["split", ','], "clear", "uniq"])
        filters.multiStatusUnit("Clinvar_Trusted_Simplified",
            "/_view/databases/clinvar_trusted_simplified",
            tooltip =
                "Simplified Clinical Significance by trusted submitters only",
            conversion = ["values", ["split", ','], "clear", "uniq"])

        filters.statusUnit("Clinvar_stars", "/_filters/clinvar_stars",
            default_value = "No data", title = "ClinVar Stars")
        filters.intValueUnit("Number_of_clinvar_submitters",
            "/_filters/num_clinvar_submitters", render_mode = "log,>",
            default_value = 0, title = "ClinVar: Number of Submitters")
        filters.statusUnit("Clinvar_review_status",
            "/_filters/clinvar_review_status",
            default_value = "No data", title = "ClinVar Review Status")
        filters.statusUnit("Clinvar_criteria_provided",
            "/_filters/clinvar_criteria_provided",
            default_value = "Not Provided", title = "ClinVar Criteria")
        filters.statusUnit("Clinvar_conflicts",
            "/_filters/clinvar_conflicts",
            default_value = "Criteria not Provided",
            title = "ClinVar Conflicts")
        filters.multiStatusUnit("Clinvar_acmg_guidelines",
            "/_filters/clinvar_acmg_guidelines[]",
            default_value = "None")

        for submitter in sorted(filters.getStdItem(
                "item-dict", "Clinvar_Trusted_Submitters").getData().values()):
            filters.statusUnit("%s_Significance" % submitter,
                "/_view/databases/clinvar_trusted",
                title = "Clinical Significance by %s" % submitter,
                conversion = [["property", submitter]],
                default_value = "None")

        #filters.statusUnit("Clinvar_Trusted_Benign",
        #    "/_filters/clinvar_trusted_benign",
        #    default_value = "No data",
        #    title = "Categorized Benign by Clinvar Trusted Submitters",
        #    value_map = {"True": "Benign by Trusted submitters",
        #        "False": "Unknown"})

        filters.statusUnit("splice_altering", "/_filters/splice_altering",
            title = "Splice AI splice altering",
            default_value = "No altering")
        filters.floatValueUnit("splice_ai_dsmax", "/_filters/splice_ai_dsmax",
            title = "Splice AI splice altering score",
            render_mode = "linear,>", default_value = 0)

        # filters.multiStatusUnit("Polyphen", "/_view/predictions/polyphen[]",
        # default_value = "N/A")
        # This is an obsolete filter replaced by Polyphen 2
        filters.multiStatusUnit("Polyphen_2_HVAR",
            "/_view/predictions/polyphen2_hvar[]",
            title = "Polyphen",
            conversion = [["split_re", r"[\s\,]"], "clear", "uniq"],
            default_value = "N/A",
            tooltip = "HumVar (HVAR) is PolyPhen-2 classifier "
            "trained on known human variation (disease mutations vs."
            " common neutral variants)")
        filters.multiStatusUnit("Polyphen_2_HDIV",
            "/_view/predictions/polyphen2_hdiv[]",
            title = "Polyphen HDIV (High sensitivity)",
            conversion = [["split_re", r"[\s\,]"], "clear", "uniq"],
            default_value = "N/A",
            tooltip = "HumDiv (HDIV) classifier is trained on a smaller "
            "number of select extreme effect disease mutations vs. "
            "divergence with close homologs (e.g. primates), which is "
            "supposed to consist of mostly neutral mutations.")

        filters.multiStatusUnit("SIFT", "/_view/predictions/sift[]",
            default_value = "N/A",
            tooltip = "Sort intolerated from tolerated (An amino acid at a "
            "position is tolerated | The most frequentest amino acid "
            "being tolerated). D: Deleterious T: tolerated")
        filters.multiStatusUnit("FATHMM", "/_view/predictions/fathmm[]",
            default_value = "N/A",
            tooltip = "Functional analysis through hidden markov model HMM."
            "D: Deleterious; T: Tolerated")
        filters.multiStatusUnit("PrimateAI",
            "/_view/predictions/primate_ai_pred[]",
            default_value = "N/A",
            tooltip = "Prediction of PrimateAI score based on the authors "
            "recommendation, “T(olerated)” or “D(amaging)”. "
            "The score cutoff between “D” and “T” is 0.803.")
        filters.floatValueUnit("GERP_score", "/_view/bioinformatics/gerp_rs",
            render_mode = "linear,>", default_value = 0, title = "GERP Score")

    with filters.viewGroup("Pharmacogenomics"):
        filters.multiStatusUnit("Diseases",
            "/_filters/pharmacogenomics_diseases[]", default_value = "N/A")
        filters.multiStatusUnit("Chemicals",
            "/_filters/pharmacogenomics_chemicals[]", default_value = "N/A")

    with filters.viewGroup("Expression"):
        filters.multiStatusUnit("Mostly_Expressed_in",
            "/_filters/top_tissues[]", default_value = "N/A")

    # required = {"debug"}
    with filters.viewGroup("Debug_Info"):
        filters.intValueUnit("Severity", "/_filters/severity",
            default_value = -1)

    return filters
