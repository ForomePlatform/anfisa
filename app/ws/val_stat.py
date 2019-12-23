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

from collections import Counter

#===============================================
class NumDiapStat:
    def __init__(self):
        self.mMin, self.mMax = None, None
        self.mCntDef = 0

    def regValue(self, val):
        self.mCntDef += 1
        if self.mCntDef == 1:
            self.mMin = self.mMax = val
        else:
            if val < self.mMin:
                self.mMin = val
            elif val > self.mMax:
                self.mMax = val

    def reportResult(self, ret_handle):
        ret_handle["min"] = self.mMin
        ret_handle["max"] = self.mMax
        ret_handle["count"] = self.mCntDef

#===============================================
class EnumStat:
    def __init__(self, variant_set, detailed = False):
        self.mVariantSet = variant_set
        self.mStat = Counter()
        self.mGroupStat = None
        if detailed:
            self.mGroupStat = Counter()
            self.mCurGroupNo = None
            self.mGroupSet = set()

    def isDefined(self):
        for cnt in self.mStat.values():
            if cnt > 0:
                return True
        return False

    def flushGroup(self):
        for val in self.mGroupSet:
            self.mGroupStat[val] += 1
        self.mGroupSet = set()

    def regValues(self, values, count = 1, group_no = None):
        if not values:
            return
        if group_no is not None and group_no != self.mCurGroupNo:
            self.mCurGroupNo = group_no
            self.flushGroup()

        for val in values:
            if not(0 <= val < len(self.mVariantSet)):
                continue
            assert 0 <= val < len(self.mVariantSet)
            self.mStat[val] += count
            if self.mGroupStat is not None:
                self.mGroupSet.add(val)

    def reportResult(self, ret_handle):
        if self.mGroupStat is not None:
            self.flushGroup()
        rep_list = []
        for idx, variant in enumerate(iter(self.mVariantSet)):
            info = [variant, self.mStat.get(idx, 0)]
            if self.mGroupStat is not None:
                info.append(self.mGroupStat.get(idx, 0))
            rep_list.append(info)
        ret_handle["variants"] = rep_list
