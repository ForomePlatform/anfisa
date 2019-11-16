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

#===============================================
class VariantSet:
    @classmethod
    def create(cls, variants):
        if variants is None:
            return None
        return cls(variants)

    def __init__(self, variants):
        self.mVariants = variants
        self.mVarDict = {variant: idx
            for idx, variant in enumerate(self.mVariants)}

    def __iter__(self):
        return iter(self.mVariants)

    def __len__(self):
        return len(self.mVariants)

    def makeIdxSet(self, variants):
        idx_set = set()
        for var in variants:
            pos = self.mVarDict.get(var)
            if pos is not None:
                idx_set.add(pos)
        return idx_set

    def makeValueSet(self, idx_set):
        return {self.mVariants[pos] for pos in idx_set}

    def indexOf(self, variant):
        return self.mVarDict.get(variant)

    def getValue(self, idx_no):
        return self.mVariants[idx_no]
