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
    def __init__(self, detailed = False):
        self.mMin, self.mMax = None, None
        self.mCntDef = 0
        self.mGroupCount = None
        if detailed:
            self.mGroupCount = 0
            self.mCurGroupNo = None

    def regValue(self, val, group_no = None):
        self.mCntDef += 1
        if isinstance(val, list):
            val = val[0]
        if self.mCntDef == 1:
            self.mMin = self.mMax = val
        else:
            if val < self.mMin:
                self.mMin = val
            elif val > self.mMax:
                self.mMax = val
        if self.mGroupCount is not None:
            if group_no != self.mCurGroupNo:
                self.mCurGroupNo = group_no
                self.mGroupCount += 1

    def prepareHistogram(self, unit_h):
        return NumHistogramBuilder(self.mMin, self.mMax,
            self.mCntDef, unit_h)

    def reportResult(self, ret_handle, h_builder):
        ret_handle["min"] = self.mMin
        ret_handle["max"] = self.mMax
        ret_handle["counts"] = [self.mCntDef]
        if self.mGroupCount is not None:
            ret_handle["counts"].insert(0, self.mGroupCount)
        if h_builder is not None and h_builder.isOK():
            ret_handle["histogram"] = h_builder.getInfo()

#===============================================
class NumHistogramBuilder:
    def __init__(self, v_min, v_max, count, unit_h,
            too_low_power = -15, num_bins = 10):
        self.mIntMode = (unit_h.getSubKind() == "int")
        self.mLogMode = "log" in unit_h.getInfo().get("render-mode", "")

        self.mInfo = None
        self.mIntervals = None
        if count < 2 or v_min >= v_max - 1E-15:
            return

        if self.mIntMode:
            v_min, v_max = int(v_min), int(v_max)
        if self.mLogMode:
            self.mInfo = ["LOG"]
            pp = 0 if self.mIntMode else too_low_power
            while (pow(1E1, pp) < v_min):
                pp += 1
            self.mInfo.append(pp - 1)
            self.mIntervals = [pow(1E1, pp - 1)]
            while (v_max > self.mIntervals[-1]):
                self.mIntervals.append(pow(1E1, pp))
                pp += 1
            if len(self.mIntervals) == 1:
                self.mInfo = None
                self.mIntervals = None
                return
            self.mInfo.append(pp)
        else:
            self.mInfo = ["LIN", v_min, v_max]
            if self.mIntMode and v_max - v_min <= num_bins:
                step = 1.
            else:
                step = float(v_max - v_min) / num_bins
            vv = v_min + (step * .5)
            self.mIntervals = []
            while vv < v_max:
                self.mIntervals.append(vv)
                vv += step
        self.mInfo.append([0] * (len(self.mIntervals) + 1))

    def isOK(self):
        return self.mInfo is not None

    def getInfo(self):
        return self.mInfo

    def getIntervals(self):
        return self.mIntervals

    def getIntMode(self):
        return self.mIntMode

    def regValue(self, val):
        if isinstance(val, list):
            val = val[0]
        for idx, cell_value in enumerate(self.mIntervals):
            if val <= cell_value:
                self.mInfo[-1][idx] += 1
                return
        self.mInfo[-1][-1] += 1

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
            self.mVarTrSet = [set() for _ in self.mVariantSet]

    def isDefined(self):
        for cnt in self.mStat.values():
            if cnt > 0:
                return True
        return False

    def flushGroup(self):
        for val in self.mGroupSet:
            self.mGroupStat[val] += 1
        self.mGroupSet = set()

    def regValues(self, values, count = 1,
            group_no = None, transcript_id = None):
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
            if transcript_id is not None:
                self.mVarTrSet[val].add(transcript_id)

    def reportResult(self, ret_handle):
        if self.mGroupStat is not None:
            self.flushGroup()
        rep_list = []
        for idx, variant in enumerate(iter(self.mVariantSet)):
            info = [variant, self.mStat.get(idx, 0)]
            if self.mGroupStat is not None:
                info.insert(1, self.mGroupStat.get(idx, 0))
                info.append(len(self.mVarTrSet[idx]))
            rep_list.append(info)
        ret_handle["variants"] = rep_list
