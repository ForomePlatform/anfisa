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
from datetime import timedelta

#===============================================
class AnfisaConfig:
    sTextMessages = {
        "aspect.tags.title": "Tags"}

    sConfigOptions = {
        "aspect.tags.name": "tags_data",

        "zygosity.cases": {
            "homo_recess": "Homozygous Recessive",
            "x_linked": "X-linked",
            "dominant": "Autosomal Dominant",
            "compens": "Compensational"
        },

        "tm.coeff": .2,
        "report.lines": 100,

        "ws.max.count":  9000,
        "export.max.count": 300,
        "tab.max.count": 9000,  # 50,

        "ds.name.max.length": 255,
        "tag.name.max.length": 255,
        "sol.name.max.length": 255,

        "xl.view.count.full": 300,
        "xl.view.count.samples.default": 25,
        "xl.view.count.samples.min": 10,
        "xl.view.count.samples.max": 150,

        "solution.std.mark": '@',
        "code.error.mark": u"\u26a0",

        "rules.setup": {
            "name": "Rules",
            "vgroup": "Decision trees application",
            "title": None,
            "render": None
        },

        "panels.setup": {
            "Symbol": {"unit": "Symbol", "special": "__Symbol__"}
        },

        "ws.transcript.id": "Transcript_id",

        "job.pool.size":    50,
        "job.pool.threads": 10,
        "job.pool.memlen":  100,

        "long.run.passtime": timedelta(minutes = 10),
        "long.run.failures": 5,

        "variety.max.rest.size": 300,
        "comp-hets.cache.size": 10,

        "max.gene.comp.count": 10000}

    sDefaultPathBase = {
        "chromosome":       "/_filters/chromosome",
        "start":            "/_filters/start",
        "ref":              "/_filters/ref",
        "alt":              "/_filters/alt",
        "color":            "/__data/color_code",
        "label":            "/__data/label",
        "zygosity":         "/__data/zygosity",
        "transcripts":      "/_view/transcripts",
    }

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
    def getAnfisaVersion(cls):
        fname = os.path.dirname(os.path.abspath(__file__)) + "/../VERSION"
        with open(fname, "r", encoding = "utf-8") as inp:
            return inp.read().strip()

    @classmethod
    def getAnfisaBuildHash(cls):
        fname = os.path.dirname(os.path.abspath(__file__)) + "/../BUILD-HASH"
        if not os.path.exists(fname):
            return None
        with open(fname, "r", encoding = "utf-8") as inp:
            return inp.read().strip()

    sDatasetPreffixMap = {
        "xl": "xl",
        "wgs": "xl",
        "wes": "xl"
    }

    @classmethod
    def checkDatasetName(cls, name, ds_kind, force_preffix = False):
        if len(name) < 1:
            return "Empty dataset name"
        if ' ' in name:
            return "Improper name for dataset: " + name
        max_ds_name_length = cls.sConfigOptions["ds.name.max.length"]
        if len(name) >= max_ds_name_length:
            return f"Too long dataset name ({max_ds_name_length}+): {name}"
        if force_preffix and ds_kind not in cls.sDatasetPreffixMap.values():
            force_preffix = False
        prefix, sep, name = name.partition('_')
        if sep is None:
            if force_preffix:
                return "No prefix in dataset name: " + name
            return None
        if force_preffix:
            if cls.sDatasetPreffixMap.get(prefix) != ds_kind:
                return f"Improper prefix for dataset kind {ds_kind}: {name}"
        else:
            if cls.sDatasetPreffixMap.get(prefix) not in (ds_kind, None):
                return f"Improper prefix for dataset kind {ds_kind}: {name}"
        if prefix in cls.sDatasetPreffixMap:
            if name is None or len(name) == 0:
                return ("Dataset name needs to be longer than just prefix: "
                    + name)
        return None

    @classmethod
    def assertGoodTagName(cls, name):
        max_tag_name_length = cls.sConfigOptions["tag.name.max.length"]
        assert len(name) <= max_tag_name_length, (
            f"Too long tag name ({max_tag_name_length}+): {name}")

    @classmethod
    def assertGoodSolutionName(cls, name):
        assert name[0].isalpha() and ' ' not in name, (
            "Improper name for solution entry: " + name)
        max_sol_name_length = cls.sConfigOptions["sol.name.max.length"]
        assert len(name) < max_sol_name_length, (
            f"Too long solution name ({max_sol_name_length}+): {name}")

#===============================================
