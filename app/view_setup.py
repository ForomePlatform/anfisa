from app.view.aspect import AspectH
from app.view.colgrp import ColGroupsH

#===============================================
class ViewSetup:
    sTextMessages = {
        "aspect.tags.title": "Tags&nbsp;&amp;<br/>Filters"}

    sConfigOptions = {
        "label.key":        "/data/label",
        "color.code":       "/data/color_code",
        "aspect.tags.name": "tags_data",
        "uniq.keys":
            ["/data/seq_region_name", "/data/start", "/data/end"],
        # "zones":            [
        #     ("Chromosome", "Chromosome"),
        #     ("Gene",       "Genes"),
        #     ("Tag",        "_tags")],
        "zones":[
            ("Gene",       "Genes"),
            ("Tag", "_tags")
        ],
        "check.tags":       [
            "Previously categorized",
            "Previously Triaged",
            "Not categorized",
            "Benign/Likely benign",
            "False positives"
        ],
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
    def normalizeColorCode(cls, color_codes):
        if color_codes:
            for code in color_codes:
                if code in {"red", "red-cross",
                        "yellow", "yellow-cross", "green"}:
                    return code
        return "grey"

    sAspects = [
        AspectH("view_gen", "General", "view", field = "general"),
        AspectH("view_qsamples", "Quality", "view",
            col_groups = ColGroupsH(attr = "quality_samples")),
        AspectH("view_gnomAD", "gnomAD", "view",
                col_groups = ColGroupsH(attr = "gnomAD")),
        AspectH("view_db", "Databases", "view", field = "databases"),
        AspectH("view_pred", "Predictions", "view", field = "predictions"),
        AspectH("view_genetics", "Bioinformatics", "view",
            field = "bioinformatics"),
        AspectH("view_inheritance", "Inheritance", "view",
            field = "inheritance", ignored = True),
        AspectH("_main", "VEP<br/>Data", "data"),
        AspectH("transcripts", "VEP<br/>Transcripts", "data",
            col_groups = ColGroupsH([
                ("intergenic_consequences", "Intergenic"),
                ("motif_feature_consequences", "Motif"),
                ("regulatory_feature_consequences", "Regulatory"),
                ("transcript_consequences", "Transcript")])),
        AspectH("colocated_v", "Colocated<br/>Variants", "data",
            col_groups = ColGroupsH(attr = "colocated_variants")),
        AspectH("input", "VCF", "data")]

    @classmethod
    def setRecomendedAttributes(cls, aspect_name, attrs):
        for aspect in cls.sAspects:
            if aspect.getName() == aspect_name:
                aspect.setRecommendedAttrs(attrs)
                return
        assert False

    def __init__(self):
        self.mAspects = [asp_h.copy() for asp_h in self.sAspects]

    def iterAspects(self):
        return iter(self.mAspects)

    def getFirstAspectID(self):
        return self.mAspects[0].getName()

#===============================================
