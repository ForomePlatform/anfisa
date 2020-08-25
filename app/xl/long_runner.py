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
from threading import Condition
from datetime import datetime

from forome_tools.job_pool import ExecutionTask
from forome_tools.log_err import logException
from app.config.a_config import AnfisaConfig
#===============================================
class XL_LongRunner_DTreeCounts(ExecutionTask):
    def __init__(self, ds_h, rq_id, dtree_h, point_idxs = None):
        ExecutionTask.__init__(self, "dtree-counts")
        self.mDS = ds_h
        self.mRqID = rq_id
        self.mDTreeH = dtree_h
        self.mCondition = Condition()
        self.mCounts = [None] * len(dtree_h)
        self.mFailureCount = 0
        self.mNextPointIdxs = []
        self.mTimeAccess = datetime.now()
        for idx in (range(len(dtree_h))
                if point_idxs is None else point_idxs):
            if dtree_h.pointNotActive(idx):
                self.mCounts[idx] = self.mDS.getEvalSpace().makeEmptyCounts()
            else:
                self.mNextPointIdxs.append(idx)

    def getTaskType(self):
        return "dtree-counts"

    def outOfDate(self, cur_datetime):
        with self.mDS:
            return (self.mCondition is None
                and cur_datetime - self.mTimeAccess
                    > AnfisaConfig.cconfigOption("long.run.passtime"))

    def execIt(self):
        while True:
            with self.mDS:
                if len(self.mNextPointIdxs) == 0:
                    break
                idx = self.mNextPointIdxs[0]
            try:
                with self.mCondition:
                    self.mCondition.notify_all()
                counts = self.mDS.getEvalSpace().evalTotalCounts(
                    self.mDTreeH.getActualCondition(idx))
            except Exception as err:
                logException("Long run exception in DS=%s"
                    % self.mDS.getName())
                self.mFailureCount += 1
                if self.mFailureCount > AnfisaConfig.configOption(
                        "long.run.failures"):
                    raise err
                else:
                    continue
            with self.mDS:
                self.mTimeAccess = datetime.now()
                self.mCounts[idx] = counts
                if counts[0] == 0 and self.mDTreeH.checkZeroAfter(idx):
                    for idx1 in range(idx, len(self.mCounts)):
                        self.mCounts[idx1] = counts[:]
                for j, pcounts in enumerate(self.mCounts):
                    if pcounts is not None and j in self.mNextPointIdxs:
                        self.mNextPointIdxs.remove(j)

        with self.mDS:
            with self.mCondition:
                self.mCondition.notify_all()
            self.mCondition = None
        return False

    def getEvaluatedCounts(self, next_points = None, time_end = None):
        condition = None
        with self.mDS:
            if next_points is not None:
                next_points_idxs = []
                for idx in next_points:
                    if (0 <= idx < len(self.mCounts)
                            and self.mCounts[idx] is None):
                        next_points_idxs.append(idx)
                for idx in self.mNextPointIdxs:
                    if (idx not in next_points_idxs
                            and self.mCounts[idx] is None):
                        next_points_idxs.append(idx)
                self.mNextPointIdxs = next_points_idxs
        while time_end is not None:
            time_now = datetime.now()
            if time_now >= time_end:
                break
            with self.mDS:
                condition = self.mCondition
            if condition is None:
                break
            timeout = (time_end - time_now).total_seconds()
            with condition:
                condition.wait(timeout)
        with self.mDS:
            self.mTimeAccess = datetime.now()
            return self.mCounts[:]

    #===============================================
