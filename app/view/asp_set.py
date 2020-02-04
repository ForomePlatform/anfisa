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

from .aspect import AspectH

#===============================================
class AspectSetH:
    def __init__(self, aspects):
        self.mAspects = aspects

    def __getitem__(self, name):
        for asp in self.mAspects:
            if asp.getName() == name:
                return asp
        return None

    def __iter__(self):
        return iter(self.mAspects)

    #===============================================
    def dump(self):
        return [asp.dump() for asp in self.mAspects]

    @classmethod
    def load(cls, data):
        return cls([AspectH.load(it) for it in data])

    #===============================================
    def getViewRepr(self, rec_data, view_context):
        ret = []
        for aspect in self.mAspects:
            if aspect.isIgnored():
                continue
            ret.append(aspect.getViewRepr(rec_data, view_context))
        return ret

    def getFirstAspectID(self):
        return self.mAspects[0].getName()

    def setAspectHitGroup(self, aspect_name, group_attr):
        for aspect in self.mAspects:
            if aspect.getName() == aspect_name:
                aspect.getColGroups().setHitGroup(group_attr)
                return
        assert False, "Failed to find aspect for hit group"
