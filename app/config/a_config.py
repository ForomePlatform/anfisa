#  Copyright (c) 2019. Partners HealthCare and other members of
#  Forome Association
#
#  Developed by Sergey Trifonov based on contributions by Joel Krier,
#  Michael Bouzinier, Shamil Sunyaev and other members of Division of
#  Genetics, Brigham and Women's Hospital
#
#  Licensed under the Apache License, Version 2.0 (the "License");
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
#
#        http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.
#

import os

#===============================================
class AnfisaConfig:
    sTextMessages = {
        "aspect.tags.title": "Tags&nbsp;&amp;<br/>Filters"}

    sConfigOptions = {
        "aspect.tags.name": "tags_data",
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

        "tm.coeff": .2,

        "max.ws.size":  5000,
        "report.lines": 100,
        "max.export.size": 300,

        "xl.view.count.full": 300,
        "xl.view.count.samples": 25,
        "xl.view.min.samples": 50,

        "max.tree.versions": 30,

        "filter.std.mark": u"\u23da",
        "code.error.mark": u"\u26a0",

        "rules.setup": {
            "name": "Rules",
            "title": None,
            "vgroup": "Decision trees application",
            "render": None
        },

        "transcript.path.base": "/__data/transcript_consequences",
        "transcript.view.setup": ("transcripts", "transcript_consequences"),

        "view.cohorts.aspect": "view_qsamples",

        "job.pool.size":    3,
        "job.pool.threads": 1,
        "op.cache.size":   50,

        "sol-log.size": 30}

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
