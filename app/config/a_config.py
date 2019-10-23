import os

#===============================================
class AnfisaConfig:
    sTextMessages = {
        "aspect.tags.title": "Tags&nbsp;&amp;<br/>Filters"}

    sConfigOptions = {
        "aspect.tags.name": "tags_data",
        "zones" : [
            ("Gene",       "Symbol"),
            ("Sample",       "Has_Variant"),
            ("Tag", "_tags")
        ],
        "check.tags":       [
            "Previously categorized",
            "Previously Triaged",
            "Not categorized",
            "Benign/Likely benign",
            "False positives"
        ],
        "zygosity.cases": {
            "homo_recess": "Homozygous Recessive",
            "x_linked": "X-linked",
            "dominant": "Autosomal Dominant",
            "compens": "Compensational"
        },
        "rand.min.size":    100,
        "rand.sample.size": 100,

        "tm.coeff": .2,

        "max.ws.size":  5000,
        "report.lines": 100,
        "max.export.size": 300,

        "xl.view.count.full": 300,
        "xl.view.count.samples": 25,
        "xl.view.min.samples": 50,

        "max.tree.versions": 30,

        "filter.std.mark": u"\u23da",

        "comp-hets.setup": {
            "zygosity.unit": "Inheritance_Mode",
            "vgroup": "Inheritance",
            "Genes": "Symbol",
            "op-variables.xl": [
                ["Compound_Het", "Symbol",
                    "Calculated Compound Hetreozygous"],
                ["Compound_Het2", "Symbol",
                    "Calculated Compound Hetreozygous"]],
            "op-variables.ws": [
                ["Compound_Het_transcript", "Transcript_id",
                    "Calculated Compound Hetreozygous, transcript approx"],
                ["Compound_Het_gene", "Transctript_gene_id",
                    "Calculated Compound Hetreozygous, gene approx"],
                ["Compound_Het_rough", "Symbol",
                    "Calculated Compound Hetreozygous, rough approx"]],
        },

        "transcript.path.base": "/data/transcript_consequences",
        "transcript.view.setup": ("transcripts", "transcript_consequences"),

        "job.pool.size":    3,
        "job.pool.threads": 1}

    sTextDecor = {
        "VEP Data": "VEP<br/>Data",
        "VEP Transcripts": "VEP<br/>Transcripts",
        "Colocated Variants": "Colocated<br/>Variants"}

    @classmethod
    def textMessage(cls, key):
        return cls.sTextMessages[key]

    @classmethod
    def configOption(cls, key):
        return cls.sConfigOptions[key]

    @classmethod
    def decorText(cls, text):
        return cls.sTextDecor.get(text, text)

    @classmethod
    def normalizeColorCode(cls, color_code):
        if color_code in {"red", "red-cross",
                "yellow", "yellow-cross", "green"}:
            return color_code
        return "grey"

    @classmethod
    def normalizeTime(cls, time_label):
        if time_label is None:
            return '2019-03-01T00:00:00'
        return time_label

    @classmethod
    def getAnfisaVersion(cls):
        with open(os.path.dirname(os.path.abspath(__file__))
                + "/../VERSION", "r", encoding = "utf-8") as inp:
            return inp.read().strip()


#===============================================
