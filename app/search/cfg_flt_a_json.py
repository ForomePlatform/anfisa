from .flt_legend import FilterLegend
from .chunker import AttrChunker
from .hot_eval import HOT_LIST
import flt_unit

#===============================================
LEGEND_AJson = FilterLegend("AJson", HOT_LIST)

flt_unit.StatusUnit(LEGEND_AJson, "chr", "/seq_region_name",
    ["chr1", "chr2", "chr3", "chr4", "chr5",
    "chr6", "chr7", "chr8", "chr9", "chr10",
    "chr11", "chr12", "chr13", "chr14", "chr15",
    "chr16", "chr17", "chr18", "chr19", "chr20",
    "chr21", "chr22", "chr23", "chrX", "chrY"])
flt_unit.IntValueUnit(LEGEND_AJson, "chr_start", "/start")
flt_unit.IntValueUnit(LEGEND_AJson, "chr_end", "/end")

flt_unit.MultiStatusUnit(LEGEND_AJson, "caller",
    "/view.general/Called by[]")

flt_unit.StatusUnit(LEGEND_AJson, "most_severe_consequence",
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

flt_unit.MultiStatusUnit(LEGEND_AJson, "genes",
    "/view.general/Gene(s)[]", compact_mode = True)

flt_unit.StatusUnit(LEGEND_AJson, "Proband_has_Variant",
    "/_filters.Proband_has_Variant")

flt_unit.IntValueUnit(LEGEND_AJson, "Proband GQ",
    "/_filters.Proband_GQ", default_value = "undefined")

flt_unit.IntValueUnit(LEGEND_AJson, "Min GQ",
    "/_filters.Min_GQ", default_value = "undefined")

flt_unit.IntValueUnit(LEGEND_AJson, "QD",
    "/_filters.QD", default_value = "undefined")

flt_unit.IntValueUnit(LEGEND_AJson, "FS",
    "/_filters.FS", default_value = "undefined")

flt_unit.StatusUnit(LEGEND_AJson, "Rare Variant",
    "/_filters.RareVariantFilter")

flt_unit.FloatValueUnit(LEGEND_AJson, "gnomAD_AF",
    "/view.gnomAD/AF", diap = (0., 1.), default_value = 0.,
    title = "gnomAD Allele Frequency")

flt_unit.PresenceUnit(LEGEND_AJson, "db", [
    ("ClinVar", "/view.Databases/ClinVar"),
    ("GnomAD", "/view.gnomAD/URL"),
    ("HGMD", "/view.Databases/HGMD PMIDs[]"),
    ("OMIM", "/view.Databases/OMIM")],
    title ="Presence in databases")

flt_unit.MultiStatusUnit(LEGEND_AJson, "Polyphen",
    "/view.Predictions/Polyphen[]")

flt_unit.MultiStatusUnit(LEGEND_AJson, "SIFT",
    "/view.Predictions/SIFT[]")

flt_unit.MultiStatusUnit(LEGEND_AJson, "Polyphen_2_HVAR",
    "/view.Predictions/Polyphen 2 HVAR[]",
    chunker = AttrChunker("[\s\,]"), default_value = "undef")
flt_unit.MultiStatusUnit(LEGEND_AJson, "Polyphen_2_HDIV",
    "/view.Predictions/Polyphen 2 HDIV[]",
    chunker = AttrChunker("[\s\,]"), default_value = "undef")

#===============================================
