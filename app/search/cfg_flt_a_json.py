from .flt_legend import FilterLegend
from .chunker import AttrChunker
import flt_unit

#===============================================
LEGEND_AJson = FilterLegend("AJson")

flt_unit.StatusUnit(LEGEND_AJson, "color", "/color_code",
    ["red", "yellow", "green", "undef"],
    default_value = "undef")

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
    "/most_severe_consequence", default_value = "undef")

flt_unit.StatusUnit(LEGEND_AJson, "transcript_id",
    "/transcript_id", default_value = "undef")

flt_unit.MultiStatusUnit(LEGEND_AJson, "genes",
    "/view.general/Gene(s)[]", compact_mode = True)

flt_unit.StatusUnit(LEGEND_AJson, "proband_genotype",
    "/view.general/Proband Genotype", default_value = "undef")

flt_unit.FloatValueUnit(LEGEND_AJson, "gnomAD_AF",
    "/view.gnomAD/AF", diap = (0., 1.), default_value = 0.,
    title = "gnomAD Allele Frequency")

flt_unit.PresenceUnit(LEGEND_AJson, "db", [
    ("ClinVar", "/view.Databases/ClinVar"),
    ("GnomAD", "/view.gnomAD/URL"),
    ("HGMD", "/view.Databases/HGMD"),
    ("OLIM", "/view.Databases/OLIM")],
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
