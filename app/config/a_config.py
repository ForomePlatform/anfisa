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
from zlib import crc32

from forome_tools.path_works import AttrFuncHelper
#===============================================
class AnfisaConfig:
    sTextMessages = {
        "aspect.tags.title": "Tags&nbsp;&amp;<br/>Filters"}

    sConfigOptions = {
        "aspect.tags.name": "tags_data",

        "zygosity.cases": {
            "homo_recess": "Homozygous Recessive",
            "x_linked": "X-linked",
            "dominant": "Autosomal Dominant",
            "compens": "Compensational"
        },

        "tm.coeff": .2,

        "max.ws.size":  9000,
        "report.lines": 100,
        "max.export.size": 300,

        "xl.view.count.full": 300,
        "xl.view.count.samples": 25,
        "xl.view.min.samples": 50,

        "max.tab.rq.size": 50,

        "filter.std.mark": u"\u23da",
        "code.error.mark": u"\u26a0",

        "rules.setup": {
            "name": "Rules",
            "vgroup": "Decision trees application",
            "title": None,
            "render": None
        },

        "zygosity.path.base": "/__data/zygosity",

        "transcript.path.base": "/_view/transcripts",

        "job.pool.size":    50,
        "job.pool.threads": 10,
        "job.pool.memlen":  100,

        "long.run.passtime": timedelta(minutes = 10),
        "long.run.failures": 5,

        "comp-hets.cache.size": 10,

        "max.gene.comp.count": 10000}

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
            return None
        return time_label

    @classmethod
    def getAnfisaVersion(cls):
        with open(os.path.dirname(os.path.abspath(__file__))
                + "/../VERSION", "r", encoding = "utf-8") as inp:
            return inp.read().strip()

    sVariantSystemFields = {
        "_color": AttrFuncHelper.singleGetter(
            "/__data/color_code"),
        "_label": AttrFuncHelper.singleGetter(
            "/__data/label"),
        "_key":   AttrFuncHelper.multiStrGetter(
            "-", ["/_filters/chromosome",
            "/_filters/start", "/_filters/ref", "/_filters/alt"])}

    @classmethod
    def getVariantSystemFields(cls, rec_data):
        result = dict()
        for name, fld_f in cls.sVariantSystemFields.items():
            result[name] = fld_f(rec_data)
        result["_rand"] = crc32(bytes(result["_key"], 'utf-8'))
        return result

#===============================================
