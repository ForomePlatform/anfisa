from app.search.flt_legend import FilterLegend
from app.search.chunker import AttrChunker
from app.search.hot_eval import HOT_SETUP
from app.search.condition import ConditionMaker
import app.search.flt_unit as flt_unit

#===============================================
def prepareLegend(ws_name):
    legend = FilterLegend(ws_name, HOT_SETUP)

    legend._startViewGroup("Coordinates")
    # flt_unit.StatusUnit(legend, "Chromosome", "/seq_region_name",
    #     ["chr1", "chr2", "chr3", "chr4", "chr5",
    #     "chr6", "chr7", "chr8", "chr9", "chr10",
    #     "chr11", "chr12", "chr13", "chr14", "chr15",
    #     "chr16", "chr17", "chr18", "chr19", "chr20",
    #     "chr21", "chr22", "chr23", "chrX", "chrY", "?"], research_only=True, accept_wrong_values=True)

    flt_unit.StatusUnit(legend, "Chromosome", "/data/seq_region_name",
        research_only = True, accept_wrong_values = True)

    flt_unit.IntValueUnit(legend, "Start_Pos", "/data/start",
        title = "Start Position", research_only = True)
    flt_unit.IntValueUnit(legend, "End_Pos", "/data/end",
        title = "End Position", research_only = True)
    flt_unit.IntValueUnit(legend, "Dist_from_Exon",
        "/_filters/dist_from_exon",
        title="Distance From Intron/Exon Boundary (Canonical)",
        research_only = False, default_value = 0)
    flt_unit.StatusUnit(legend, "Region",
        "/data/region_canonical",
        title="Region (Canonical)",
        research_only = False, default_value = "Other")
    legend._endViewGroup()

    flt_unit.MultiStatusUnit(legend, "Genes",
        "/view/general/genes[]", compact_mode = True)

    flt_unit.StatusUnit(legend, "Most_Severe_Consequence",
        "/data/most_severe_consequence",
        ["transcript_ablation",
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
        "undefined"], default_value = "undefined")

    legend._startViewGroup("gnomAD")
    flt_unit.FloatValueUnit(legend, "gnomAD_AF",
        "/_filters/gnomad_af_fam",
        diap = (0., 1.), default_value = 0.,
        title = "gnomAD Allele Frequency (family)")
    flt_unit.FloatValueUnit(legend, "gnomAD_AF_Exomes",
        "/_filters/gnomad_db_exomes_af",
        diap = (0., 1.), default_value = 0.,
        title = "gnomAD Exome Allele Frequency (family)")
    flt_unit.FloatValueUnit(legend, "gnomAD_AF_Genomes",
        "/_filters/gnomad_db_genomes_af",
        diap = (0., 1.), default_value = 0.,
        title = "gnomAD Genome Allele Frequency (family)")
    flt_unit.FloatValueUnit(legend, "gnomAD_AF_Proband",
        "/_filters/gnomad_af_pb",
        diap = (0., 1.), default_value = 0.,
        title = "gnomAD Allele Frequency (proband)")
    flt_unit.FloatValueUnit(legend, "gnomAD_PopMax_AF",
        "/_filters/gnomad_popmax_af",
        diap = (0., 1.), default_value = 0.,
        title = "gnomAD PopMax Allele Frequency")
    flt_unit.StatusUnit(legend, "gnomAD_PopMax",
        "/_filters/gnomad_popmax", default_value= None,
        title = "gnomAD PopMax Ancestry")
    flt_unit.IntValueUnit(legend, "gnomAD_PopMax_AN",
        "/_filters/gnomad_popmax_an",
        default_value = 0,
        title = "gnomAD: Number of alleles in PopMax Ancestry")
    flt_unit.IntValueUnit(legend, "gnomAD_Hom",
        "/_filters/gnomad_hom",
        default_value = 0,
        title = "gnomAD: Number of homozygous")
    flt_unit.IntValueUnit(legend, "gnomAD_Hem",
        "/_filters/gnomad_hem",
        default_value = 0,
        title = "gnomAD: Number of hemizygous")

    legend._endViewGroup()
    legend._startViewGroup("Databases")
    flt_unit.PresenceUnit(legend, "Presence_in_Databases", [
        ("ClinVar", "/view/databases/clinVar"),
        ("LMM", "/view/databases/lmm_significance"),
        ("GeneDx", "/view/databases/gene_dx_significance"),
        ("GnomAD", "/_filters/gnomad_af_fam"),
        ("HGMD", "/view/databases/hgmd_pmids[]"),
        ("OMIM", "/view/databases/omim")])

    flt_unit.MultiStatusUnit(legend, "ClinVar_Submitters",
        "/view/databases/clinVar_submitters[]",
        title="ClinVar Submitters")

    # flt_unit.MultiStatusUnit(legend, "beacons",
    #     "/data/beacon_names",
    #     title="Observed at")

    legend._endViewGroup()

    legend._startViewGroup("Call")
    flt_unit.StatusUnit(legend, "Variant_Class",
        "/data/variant_class")

    flt_unit.MultiStatusUnit(legend, "Callers",
        "/view/bioinformatics/called_by[]",
        title="Called by", research_only = False)

    flt_unit.MultiStatusUnit(legend, "Has_Variant",
        "/_filters/has_variant[]")

    legend._endViewGroup()

    legend._startViewGroup("Call_Quality")
    flt_unit.IntValueUnit(legend, "Proband_GQ",
        "/_filters/proband_gq")

    flt_unit.IntValueUnit(legend, "Min_GQ",
        "/_filters/min_gq")

    flt_unit.IntValueUnit(legend, "QD",
        "/_filters/qd")

    flt_unit.IntValueUnit(legend, "MQ",
        "/_filters/mq")

    flt_unit.IntValueUnit(legend, "FS",
        "/_filters/fs")
    legend._endViewGroup()

    legend._startViewGroup("Predictions")

    flt_unit.StatusUnit(legend, "Clinvar_Benign",
        "/_filters/clinvar_benign", default_value="Not in ClinVar")
    flt_unit.StatusUnit(legend, "Clinvar_Trusted_Benign",
        "/_filters/clinvar_trusted_benign", default_value="No data", title="Benign by Clinvar Trusted Submitters")
    flt_unit.StatusUnit(legend, "HGMD_Benign",
        "/_filters/hgmd_benign", default_value="Not in HGMD")

    flt_unit.MultiStatusUnit(legend, "HGMD_Tags",
        "/view/databases/hgmd_tags[]", default_value = "None")

    flt_unit.MultiStatusUnit(legend, "ClinVar_Significance",
        "/data/clinvar_significance[]")

    flt_unit.MultiStatusUnit(legend, "LMM_Significance",
        "/data/lmm", title="Clinical Significance by LMM")

    flt_unit.MultiStatusUnit(legend, "GeneDx_Significance",
        "/data/gene_dx", title="Clinical Significance by GeneDx")

    flt_unit.MultiStatusUnit(legend, "Polyphen",
        "/view/predictions/polyphen[]")

    flt_unit.MultiStatusUnit(legend, "SIFT",
        "/view/predictions/sift[]")

    flt_unit.MultiStatusUnit(legend, "Polyphen_2_HVAR",
        "/view/predictions/polyphen2_hvar[]",
        chunker = AttrChunker("[\s\,]"), default_value = "undef")
    flt_unit.MultiStatusUnit(legend, "Polyphen_2_HDIV",
        "/view/predictions/polyphen2_hdiv[]",
        chunker = AttrChunker("[\s\,]"), default_value = "undef")
    legend._endViewGroup()

    legend._startViewGroup("Debug_Info")
    flt_unit.IntValueUnit(legend, "Severity",
        "/_filters/severity", research_only = True, default_value = -1)
    legend._endViewGroup()

    #===============================================
    legend.regFilter("Candidates_BGM",
        [ConditionMaker.condEnum("Rules", ["Candidates_BGM"])])
    legend.regFilter("SEQaBOO_Hearing_Loss_v_01",
        [
            ConditionMaker.condEnum("Rules", ["SEQaBOO_Hearing_Loss_v_01"]),
            ConditionMaker.condEnum("Rules", ["ACMG59"], "NOT")
        ])
    legend.regFilter("SEQaBOO_Hearing_Loss_v_02",
        [
            ConditionMaker.condEnum("Rules", ["SEQaBOO_Hearing_Loss_v_02"]),
            ConditionMaker.condEnum("Rules", ["ACMG59"], "NOT")
        ])
    legend.regFilter("SEQaBOO_Hearing_Loss_v_03",
        [
            ConditionMaker.condEnum("Rules", ["SEQaBOO_Hearing_Loss_v_03"]),
            ConditionMaker.condEnum("Rules", ["ACMG59"], "NOT")
        ])
    legend.regFilter("SEQaBOO_ACMG59",
        [
            ConditionMaker.condEnum("Rules", ["SEQaBOO_ACMG59"]),
            ConditionMaker.condEnum("Rules", ["ACMG59"], "AND")
        ])

    return legend
