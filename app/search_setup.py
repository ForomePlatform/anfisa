from   app.search.flt_legend import FilterLegend
from   app.search.chunker import AttrChunker
from   app.search.hot_eval import HOT_SETUP
from   app.search.condition import ConditionMaker
import app.search.flt_unit as flt_unit

#===============================================
MainLegend = FilterLegend("AJson", HOT_SETUP)

flt_unit.StatusUnit(MainLegend, "Chromosome", "/seq_region_name",
    ["chr1", "chr2", "chr3", "chr4", "chr5",
    "chr6", "chr7", "chr8", "chr9", "chr10",
    "chr11", "chr12", "chr13", "chr14", "chr15",
    "chr16", "chr17", "chr18", "chr19", "chr20",
    "chr21", "chr22", "chr23", "chrX", "chrY"])
flt_unit.IntValueUnit(MainLegend, "Start Position", "/start")
flt_unit.IntValueUnit(MainLegend, "End Position", "/end")

flt_unit.MultiStatusUnit(MainLegend, "caller",
    "/view.general/Called by[]", expert_only = False)

flt_unit.StatusUnit(MainLegend, "most_severe_consequence",
    "/most_severe_consequence", [
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
    "undefined"], default_value = "undefined")

flt_unit.MultiStatusUnit(MainLegend, "genes",
    "/view.general/Gene(s)[]", compact_mode = True)

flt_unit.StatusUnit(MainLegend, "Proband_has_Variant",
    "/_filters.Proband_has_Variant")

flt_unit.StatusUnit(MainLegend, "Variant_Class",
    "/variant_class")

flt_unit.IntValueUnit(MainLegend, "Proband_GQ",
    "/_filters.Proband_GQ")

flt_unit.IntValueUnit(MainLegend, "Severity",
    "/_filters.Severity", expert_only=True, default_value=5)

flt_unit.IntValueUnit(MainLegend, "Min_GQ",
    "/_filters.Min_GQ")

flt_unit.IntValueUnit(MainLegend, "QD",
    "/_filters.QD")

flt_unit.IntValueUnit(MainLegend, "FS",
    "/_filters.FS")

flt_unit.StatusUnit(MainLegend, "Rare_Variant",
    "/_filters.RareVariantFilter")

flt_unit.FloatValueUnit(MainLegend, "gnomAD_AF",
    "/_filters.gnomaAD_AF", diap = (0., 1.), default_value = 0.,
    title = "gnomAD Allele Frequency")

flt_unit.PresenceUnit(MainLegend, "Presence_in_Databases", [
    ("ClinVar", "/view.Databases/ClinVar"),
    ("GnomAD", "/_filters.gnomaAD_AF"),
    ("HGMD", "/view.Databases/HGMD PMIDs[]"),
    ("OMIM", "/view.Databases/OMIM")],
    title ="Presence in databases")

flt_unit.MultiStatusUnit(MainLegend, "Polyphen",
    "/view.Predictions/Polyphen[]")

flt_unit.MultiStatusUnit(MainLegend, "SIFT",
    "/view.Predictions/SIFT[]")

flt_unit.MultiStatusUnit(MainLegend, "Polyphen_2_HVAR",
    "/view.Predictions/Polyphen 2 HVAR[]",
    chunker = AttrChunker("[\s\,]"), default_value = "undef")
flt_unit.MultiStatusUnit(MainLegend, "Polyphen_2_HDIV",
    "/view.Predictions/Polyphen 2 HDIV[]",
    chunker = AttrChunker("[\s\,]"), default_value = "undef")

#===============================================
MainLegend.regFilter("Candidates",
    [ConditionMaker.condEnum("Rules", ["Candidates"])])
MainLegend.regFilter("Candidates-Rare",
    [ConditionMaker.condEnum("Rules", ["Candidates-Rare"])])

