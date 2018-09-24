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
    #     "chr21", "chr22", "chr23", "chrX", "chrY", "?"], expert_only=True, accept_wrong_values=True)

    flt_unit.StatusUnit(legend, "Chromosome", "/seq_region_name",
        expert_only=True, accept_wrong_values=True)


    flt_unit.IntValueUnit(legend, "Start Position", "/start", expert_only=True)
    flt_unit.IntValueUnit(legend, "End Position", "/end", expert_only=True)
    legend._endViewGroup()

    flt_unit.MultiStatusUnit(legend, "Genes",
        "/view.general/Gene(s)[]", compact_mode = True)

    flt_unit.StatusUnit(legend, "Most_Severe_Consequence",
        "/most_severe_consequence",
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

    legend._startViewGroup("Databases")
    flt_unit.FloatValueUnit(legend, "gnomAD_AF",
        "/_filters.gnomaAD_AF", diap = (0., 1.), default_value = 0.,
        title = "gnomAD Allele Frequency")

    flt_unit.StatusUnit(legend, "BGM_Rare_Variant",
        "/_filters.RareVariantFilter", expert_only=True)

    flt_unit.PresenceUnit(legend, "Presence_in_Databases", [
        ("ClinVar", "/view.Databases/ClinVar"),
        ("GnomAD", "/_filters.gnomaAD_AF"),
        ("HGMD", "/view.Databases/HGMD PMIDs[]"),
        ("OMIM", "/view.Databases/OMIM")])

    legend._endViewGroup()

    legend._startViewGroup("Call")
    flt_unit.StatusUnit(legend, "Variant_Class",
        "/variant_class")

    flt_unit.MultiStatusUnit(legend, "Called by",
        "/view.Genetics/Called by[]", expert_only = True)

    flt_unit.StatusUnit(legend, "Proband_has_Variant",
        "/_filters.Proband_has_Variant")

    legend._endViewGroup()

    legend._startViewGroup("Call_Quality")
    flt_unit.IntValueUnit(legend, "Proband_GQ",
        "/_filters.Proband_GQ")

    flt_unit.IntValueUnit(legend, "Min_GQ",
        "/_filters.Min_GQ")

    flt_unit.IntValueUnit(legend, "QD",
        "/_filters.QD")

    flt_unit.IntValueUnit(legend, "FS",
        "/_filters.FS")
    legend._endViewGroup()

    legend._startViewGroup("Predictions")
    flt_unit.MultiStatusUnit(legend, "Polyphen",
        "/view.Predictions/Polyphen[]")

    flt_unit.MultiStatusUnit(legend, "SIFT",
        "/view.Predictions/SIFT[]")

    flt_unit.MultiStatusUnit(legend, "Polyphen_2_HVAR",
        "/view.Predictions/Polyphen 2 HVAR[]",
        chunker = AttrChunker("[\s\,]"), default_value = "undef")
    flt_unit.MultiStatusUnit(legend, "Polyphen_2_HDIV",
        "/view.Predictions/Polyphen 2 HDIV[]",
        chunker = AttrChunker("[\s\,]"), default_value = "undef")
    legend._endViewGroup()

    legend._startViewGroup("Debug_Info")
    flt_unit.IntValueUnit(legend, "Severity",
        "/_filters.Severity", expert_only = True, default_value = -1)
    legend._endViewGroup()

    #===============================================
    legend.regFilter("Candidates_BGM",
        [ConditionMaker.condEnum("Rules", ["Candidates_BGM"])])
    legend.regFilter("Candidates_Including_Common",
        [ConditionMaker.condEnum("Rules", ["Candidates_Including_Common"])])
    legend.regFilter("Candidates_Rare_and_Damaging",
        [
            ConditionMaker.condEnum("Rules", ["Candidates_BGM"]),
            ConditionMaker.condNumLE("Severity", 1)
        ])

    return legend
