from view.aspect import AspectH
from view.attr   import AttrH
from view.colgrp import ColGroupsH

#===============================================
class ViewSetup:
    sTextMessages = {
        "aspect.hot.title": "Tags&nbsp;&amp;<br/>Filters" }

    sConfigOptions = {
        "label.key":        "label",
        "color.code":       "color_code",
        "aspect.hot.name":  "hot_data",
        "uniq.keys":        ("seq_region_name", "start", "end"),
        "zones":            [
            ("Chromosome", "Chromosome"),
            ("Gene",       "genes"),
            ("Tag",        "_tags")],
        "attrs.to.ignore":  ["/view"],
        "rand.seed":        179,
        "rand.min.size":    100,
        "rand.sample.size": 100}

    @classmethod
    def textMessage(cls, key):
        return cls.sTextMessages[key]

    @classmethod
    def configOption(cls, key):
        return cls.sConfigOptions[key]

    @classmethod
    def normalizeColorCode(cls, color_code):
        if color_code in {"red", "red-cross",
                "yellow", "yellow-cross", "green"}:
            return color_code
        return "grey"

    sAspects = [
        AspectH("view_gen", "General", "/view.general"),
        AspectH("view_qsamples", "Quality", "",
            col_groups = ColGroupsH(attr = "quality.samples")),
        AspectH("view_gnomAD", "gnomAD",
                "", col_groups = ColGroupsH(attr = "view.gnomAD")),
        AspectH("view_db", "Databases", "/view.Databases"),
        AspectH("view_pred", "Predictions", "/view.Predictions"),
        AspectH("view_genetics", "Genetics", "/view.Genetics"),
        AspectH("view_inheritance", "Inheritance", "/view.Inheritance",
            ignored = True),
        AspectH("_main", "VEP<br/>Data", "", kind = "tech"),
        AspectH("transcripts", "VEP<br/>Transcripts", "", kind = "tech",
            col_groups = ColGroupsH([
                ("intergenic_consequences", "Intergenic"),
                ("motif_feature_consequences", "Motif"),
                ("regulatory_feature_consequences", "Regulatory"),
                ("transcript_consequences", "Transcript")])),
        AspectH("colocated_v", "Colocated<br/>Variants", "", kind = "tech",
            col_groups = ColGroupsH(attr = "colocated_variants")),
        AspectH("input", "VCF", "", kind = "tech",
            attrs = [AttrH("input")])]

    @classmethod
    def setRecomendedAttributes(cls, aspect_name, attrs):
        for aspect in cls.sAspects:
            if aspect.getName() == aspect_name:
                aspect.setRecommendedAttrs(attrs)
                return
        assert False

    @classmethod
    def getAspects(cls):
        return cls.sAspects

#===============================================
