#===============================================
class AnfisaConfig:
    sTextMessages = {
        "aspect.tags.title": "Tags&nbsp;&amp;<br/>Filters"}

    sConfigOptions = {
        "aspect.tags.name": "tags_data",
        # "zones":            [
        #     ("Chromosome", "Chromosome"),
        #     ("Gene",       "Genes"),
        #     ("Tag",        "_tags")],
        "zones":[
            ("Gene",       "Genes"),
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
        "rand.min.size":    100,
        "rand.sample.size": 100}

    sTextDecor = {
        "VEP Data": "VEP<br/>Data",
        "VEP Transcripts": "VEP<br/>Transcripts",
        "Colocated Variants": "Colocated<br/>Variants"}

    DRUID_GRANULARITY = "all"
    DRUID_INTERVAL = "2015-01-01/2015-12-31"

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
    def normalizeColorCode(cls, color_codes):
        if color_codes:
            for code in color_codes:
                if code in {"red", "red-cross",
                        "yellow", "yellow-cross", "green"}:
                    return code
        return "grey"

#===============================================
