import sys
from itertools import product

from app.prepare.prep_filters import FilterPrepareSetH
from app.filter.condition import ConditionMaker

#===============================================
def _conv_len(arr):
    if arr:
        return len(arr)
    return 0

def _conv_bool(v, s1, s2):
    if v in [True, "True"]:
        return s1
    elif v in [False, "False"]:
        return s2
    return v

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
def defineFilterSchema():
    filters = FilterPrepareSetH()

    with filters.viewGroup("Inheritance"):
        filters.statusUnit("Proband_Zygosity", "/view/bioinformatics/zygosity",
                           title="Proband Zygosity")
        filters.zygositySpecialUnit("Inheritance_Mode",
            "/data/zygosity", config = {"x_cond":
            ConditionMaker.condEnum("Chromosome", ["chrX"])},
            title = "Inheritance Mode")
        filters.multiStatusUnit("Callers", "/view/bioinformatics/called_by[]",
            title = "Called by")
        filters.intValueUnit("Num_Samples", "/_filters/has_variant",
                            title="Number of Samples", conversion=_conv_len,
                            default_value = 0,
            tooltip="Number of samples for which this variant has been called")
        filters.multiStatusUnit("Has_Variant", "/_filters/has_variant[]")

    with filters.viewGroup("Cohorts"):
        for f in product(["ALL", "bgm", "srr", "m"], ["AF", "AF2"]):
            key = "cohort/{}/{}".format(f[0], f[1])
            filters.floatValueUnit(key.replace('/','_'), "/_filters/{}".format(key), default_value=0)

    with filters.viewGroup("Variant"):
        filters.statusUnit("Variant_Class", "/data/variant_class",
            tooltip = ("Variant class as returned by VEP. "
                "The class of a variant is based on Sequence "
                "Ontology and is called according to its component "
                "alleles and its mapping to the reference genome. "
                "https://useast.ensembl.org/info/genome/variation/"
                "prediction/classification.html#classes"))
        filters.statusUnit("Most_Severe_Consequence",
               "/data/most_severe_consequence",
               variants = sConsequenceVariants,
               default_value = "undefined")
        filters.statusUnit("Canonical_Annotation",
            "/view/general/canonical_annotation",
            default_value = "undefined")
        filters.intValueUnit("Number_ALTs",
            "/_filters/alts",
            title = "Number of Alternative alleles",
            conversion = _conv_len, default_value = 0)

        #filters.intValueUnit("zyg_len", "/data/zygosity",
        #   conversion = _conv_len, default_value = 0)

    with filters.viewGroup("Genes"):
        genes_unit = filters.multiStatusUnit("Symbol",
            "/view/general/genes[]",
            compact_mode = True)
        filters.panelStatusUnit("Panels", genes_unit,
            view_path = "/view/general/gene_panels")
        #filters.multiStatusUnit("Transcripts",
        #    "/data/transcript_consequences[]", compact_mode = True,
        #    conversion = lambda arr:
        #        [el["transcript_id"] for el in arr] if arr else [])
        filters.intValueUnit("Num_Genes", "/view/general/genes",
            title = "Number of overlapping genes",
            conversion = _conv_len, default_value = 0)
        filters.intValueUnit("Num_Transcripts",
            "/data/transcript_consequences",
            title = "Number of transcripts at the position",
            conversion = _conv_len, default_value = 0)

    with filters.viewGroup("Transcripts"):
        filters.transctiptMultisetUnit("Transctipt_consequence",
            "consequence_terms", variants = sConsequenceVariants)
        filters.transctiptStatusUnit("Transcript_canonical", "canonical",
            bool_check_value = "1", default_value = "False")
        filters.transctiptStatusUnit("Transcript_biotype", "biotype",
            default_value = "undefined")
        filters.transctiptStatusUnit("Transcript_worst", "consequence_terms",
            bool_check_value = "${Most_Severe_Consequence}",
            default_value = "False")
        filters.transctiptStatusUnit("Transcript_id", "transcript_id",
            default_value = "undefined")
        filters.transctiptStatusUnit("Transctript_gene_id", "gene_id",
            default_value = "undefined")
        filters.transctiptStatusUnit("Transcript_source", "source",
            default_value = "undefined")
        filters.transctiptStatusUnit("Transcript_strand", "strand",
            default_value = "undefined")

    with filters.viewGroup("Coordinates"):
        filters.statusUnit("Chromosome", "/_filters/chromosome",
            variants = ["chr1", "chr2", "chr3", "chr4", "chr5",
            "chr6", "chr7", "chr8", "chr9", "chr10",
            "chr11", "chr12", "chr13", "chr14", "chr15",
            "chr16", "chr17", "chr18", "chr19", "chr20",
            "chr21", "chr22", "chr23", "chrX", "chrY", "undefined"],
            default_value = "undefined")

        filters.intValueUnit("Start_Pos", "/data/start",
            title = "Start Position",
            render_mode = "neighborhood", default_value=sys.maxsize)
        filters.intValueUnit("End_Pos", "/data/end",
            title = "End Position", default_value = 0,
            render_mode = "neighborhood")
        filters.intValueUnit("Dist_from_Exon", "/_filters/dist_from_exon",
            title = "Distance From Intron/Exon Boundary (Canonical)",
            default_value = 0, render_mode = "log,<")
        filters.statusUnit("Region", "/data/region_canonical",
            title = "Region (Canonical)", default_value = "Other")

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
            tooltip = "Maximum allele frequency across all populations",
            diap = (0., 1.), default_value = 0.,
            title = "gnomAD PopMax Allele Frequency",
            render_mode = "log,<")
        filters.statusUnit("gnomAD_PopMax",
            "/_filters/gnomad_popmax", default_value = "None",
            title = "gnomAD PopMax Ancestry",
            tooltip = "Population that has the maximum allele frequency")
        filters.intValueUnit("gnomAD_PopMax_AN",
            "/_filters/gnomad_popmax_an",
            default_value = 0,
            title = "gnomAD: Number of alleles in PopMax Ancestry",
            render_mode = "log,>")
        filters.intValueUnit("gnomAD_Hom",
            "/_filters/gnomad_hom",
            default_value = 0,
            title = "gnomAD: Number of homozygous",
            render_mode = "log,>")
        filters.intValueUnit("gnomAD_Hem",
            "/_filters/gnomad_hem",
            default_value = 0,
            title = "gnomAD: Number of hemizygous",
            render_mode = "log,>")

    with filters.viewGroup("Databases"):
        filters.presenceUnit("Presence_in_Databases", [
            ("ClinVar", "/view/databases/clinVar"),
            ("LMM", "/view/databases/lmm_significance"),
            ("GeneDx", "/view/databases/gene_dx_significance"),
            ("GnomAD", "/_filters/gnomad_af_fam"),
            ("HGMD", "/view/databases/hgmd_pmids[]"),
            ("OMIM", "/view/databases/omim")],
            title = "Presence in Databases")

        filters.multiStatusUnit("ClinVar_Submitters",
            "/view/databases/clinVar_submitters[]",
            title = "ClinVar Submitters", compact_mode = True)
        filters.intValueUnit("Number_submitters",
            "/view/databases/clinVar_submitters",
            title = "Number of ClinVar Submitters",
            conversion = _conv_len, default_value = 0)
        filters.intValueUnit("Number_pmid",
            "/view/databases/hgmd_pmids",
            title = "Number of PMIDs in HGMD",
            conversion = _conv_len, default_value = 0)

        # filters.multiStatusUnit("beacons",
        #     "/data/beacon_names",
        #     title = "Observed at")

    with filters.viewGroup("Call_Quality"):
        filters.floatValueUnit("Proband_GQ", "/_filters/proband_gq",
            title = "Genotype Quality (GQ) for Proband",
            render_mode = "linear,>", default_value = 1000,
            tooltip = "GQ tells you how confident we are that "
            "the genotype we assigned to a particular sample is correct. "
            "It is simply the second lowest PL, because it is the "
            "difference between the second lowest PL and the lowest PL "
            "(always 0).")
        filters.floatValueUnit("Min_GQ", "/_filters/min_gq",
            title = "Minimum GQ for the family)", render_mode = "linear,>",
            default_value = 1000,
            tooltip = "GQ tells you how confident we are that "
            "the genotype we assigned to a particular sample is correct. "
            "It is simply the second lowest PL, because it is the "
            "difference between the second lowest PL and the lowest PL "
            "(always 0).")
        filters.floatValueUnit("QD", "/_filters/qd",
            title = "Quality by Depth", render_mode = "linear,>",
            default_value=100000.,
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
            "Fisher Strand Bias",
            render_mode = "linear,<", default_value = 0.,
              tooltip = "Phred-scaled probability that there is strand bias at "
                    "the site. Strand Bias tells us whether the alternate "
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
        filters.statusUnit("HGMD_Benign", "/_filters/hgmd_benign",
            title = "Categorized Benign in HGMD",
            default_value = "Not in HGMD", research_only=True, render_mode="replace(True/Benign, False/Not Benign)")
        filters.multiStatusUnit("HGMD_Tags", "/view/databases/hgmd_tags[]",
            default_value = "None")

        filters.statusUnit("Clinvar_Benign", "/_filters/clinvar_benign",
            default_value = "Not in ClinVar",
            title = "Categorized Benign in ClinVar by all submitters",
                           research_only=True)
        filters.multiStatusUnit("ClinVar_Significance",
            "/data/clinvar_significance[]",
            title = "Clinical Significance in ClinVar")
        filters.statusUnit("Clinvar_stars",
            "/_filters/clinvar_stars",
            default_value = "No data",
            title = "ClinVar Stars")
        filters.intValueUnit("Number_of_clinvar_submitters",
            "/_filters/num_clinvar_submitters", render_mode = "log,>",
            default_value = 0, title = "ClinVar: Number of Submitters")
        filters.statusUnit("Clinvar_review_status",
            "/_filters/clinvar_review_status",
            default_value = "No data",
            title = "ClinVar Review Status")
        filters.statusUnit("Clinvar_criteria_provided",
            "/_filters/clinvar_criteria_provided",
            default_value = "Not Provided",
            title = "ClinVar Criteria")
        filters.statusUnit("Clinvar_conflicts",
            "/_filters/clinvar_conflicts",
            default_value = "Criteria not Provided",
            title = "ClinVar Conflicts")
        filters.multiStatusUnit("Clinvar_acmg_guidelines",
            "/_filters/clinvar_acmg_guidelines[]",
            default_value = "None")

        filters.statusUnit("Clinvar_Trusted_Benign",
            "/_filters/clinvar_trusted_benign",
            default_value = "No data",
            title = "Categorized Benign by Clinvar Trusted Submitters")
        filters.multiStatusUnit("LMM_Significance",
            "/data/lmm", title = "Clinical Significance by LMM")
        filters.multiStatusUnit("GeneDx_Significance",
            "/data/gene_dx", title = "Clinical Significance by GeneDx")

        filters.statusUnit("splice_altering", "/_filters/splice_altering",
            default_value = "No altering",
            title = "Splice AI splice altering")
        filters.floatValueUnit("splice_ai_dsmax", "/_filters/splice_ai_dsmax",
            render_mode = "linear,>", default_value = 0,
            title = "Splice AI splice altering score")

        # filters.multiStatusUnit("Polyphen", "/view/predictions/polyphen[]",
        # default_value="N/A")
        # This is an obsolete filter replaced by Polyphen 2
        filters.multiStatusUnit("Polyphen_2_HVAR",
            "/view/predictions/polyphen2_hvar[]",
            separators = "[\s\,]", default_value = "N/A",
            title="Polyphen",
            tooltip="HumVar (HVAR) is PolyPhen-2 classifier "
                "trained on known human variation (disease mutations vs."
                " common neutral variants)")
        filters.multiStatusUnit("Polyphen_2_HDIV",
            "/view/predictions/polyphen2_hdiv[]",
            separators = "[\s\,]", default_value = "N/A",
            title="Polyphen HDIV (High sensitivity)",
            tooltip="HumDiv (HDIV) classifier is trained on a smaller number "
                "of select extreme effect disease mutations vs. divergence "
                "with close homologs (e.g. primates), which is supposed to "
                "consist of mostly neutral mutations.")

        filters.multiStatusUnit("SIFT", "/view/predictions/sift[]",
                                default_value="N/A",
            tooltip="Sort intolerated from tolerated (An amino acid at a "
                    "position is tolerated | The most frequentest amino acid "
                    "being tolerated). D: Deleterious T: tolerated")
        filters.multiStatusUnit("FATHMM", "/view/predictions/fathmm[]",
                                default_value="N/A",
                tooltip="Functional analysis through hidden markov model HMM."
                      "D: Deleterious; T: Tolerated"),
        filters.floatValueUnit("GERP_score",
            "/view/bioinformatics/gerp_rs", render_mode = "linear,>",
            default_value = 0, title = "GERP Score")

    with filters.viewGroup("Debug_Info"):
        filters.intValueUnit("Severity", "/_filters/severity",
            research_only = True, default_value = -1)

    return filters
