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

from .f_solutions import solutionsFavor
from .f_view import defFavorView
from .f_flt import defFavorFlt
from .f_tune import tuneFavorAspects, tuneFavorUnits, completeFavorDS
#===============================================
class FavorSchema:

    @classmethod
    def readySolutions(cls, sol_pack):
        solutionsFavor(sol_pack)

    @classmethod
    def defineViewSchema(cls, metadata_record):
        return defFavorView(metadata_record)

    @classmethod
    def defineFilterSchema(cls, metadata_record):
        return defFavorFlt(metadata_record)

    @classmethod
    def tuneAspects(cls, ds_h, aspects):
        tuneFavorAspects(ds_h, aspects)

    @classmethod
    def tuneUnits(cls, ds_h):
        tuneFavorUnits(ds_h)

    @classmethod
    def completeDsModes(cls, ds_h):
        completeFavorDS(ds_h)
