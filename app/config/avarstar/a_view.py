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

from app.view.asp_set import AspectSetH
from app.view.aspect import AspectH
from app.view.attr import AttrH
from app.view.colgrp import ColGroupsH

# ===============================================
def defAvarstarView(metadata_record, schema_modes):
    assert metadata_record.get("data_schema") == "AVARSTAR", (
        "AVARSTAR data schema expected: "
        + metadata_record.get("data_schema"))

    aspect_list = [
        AspectH("view_gen", "General", "_view", field = "general"),
        AspectH("view_transcripts", "Transcripts", "_view",
            col_groups = ColGroupsH([("transcripts", "Transcripts")])),
        #AspectH("view_gnomAD", "gnomAD", "_view", field = "gnomAD"),
        #AspectH("view_pred", "Predictions", "_view", field = "predictions"),
    ]

    aspects = AspectSetH(aspect_list, schema_modes)

    aspects["view_gen"].setAttributes([
        AttrH("label"),
    ])

    aspects["view_transcripts"].setAttributes([])


    return aspects
