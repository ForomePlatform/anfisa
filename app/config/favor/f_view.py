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

#===============================================
def defFavorView(metadata_record):
    assert metadata_record.get("data_schema") == "FAVOR"

    aspect_list = [
        AspectH("view_gen", "General", "_view", field = "general"),
        AspectH("_main", "VEP Data", "__data")
    ]

    aspects = AspectSetH(aspect_list)

    aspects["view_gen"].setAttributes([
        AttrH("line", tooltip = "Debug record line no"),
        AttrH("type", title = "Variant Type",
            tooltip = "Type of variant")
    ])

    aspects["_main"].setAttributes([
        AttrH("label"),
        AttrH("color_code")
    ])

    return aspects
