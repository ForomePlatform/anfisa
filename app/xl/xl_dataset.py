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
import logging
from datetime import datetime

from app.config.a_config import AnfisaConfig
from app.model.dataset import DataSet
from .xl_space import XL_EvalSpace
from .xl_unit import XL_Unit
from .long_runner import XL_LongRunner_DTreeCounts
#===============================================
class XLDataset(DataSet):
    sStdFMark = AnfisaConfig.configOption("filter.std.mark")

    def __init__(self, data_vault, dataset_info, dataset_path):
        DataSet.__init__(self, data_vault, dataset_info, dataset_path)
        self.addModes({"XL"})
        self.mEvalSpace = XL_EvalSpace(self, self.getApp().getDruidAgent())
        self.mLongRunners = dict()

        for zyg_name in self.getZygUnitNames():
            self.mEvalSpace._addZygUnit(zyg_name)

        for unit_data in self.getFltSchema():
            if unit_data["sub-kind"].startswith("transcript-"):
                continue
            u_h = self.mEvalSpace.getUnit(unit_data["name"])
            if u_h is not None:
                logging.warning(
                    "Dataset %s: unit name %s already reserved as %s, skipped"
                    % (self.getName(), u_h.getName(), u_h.getUnitKind()))
                continue
            xl_unit = XL_Unit.create(self.mEvalSpace, unit_data)
            if xl_unit is not None:
                self.mEvalSpace._addUnit(xl_unit)

        if self.getDataSchema() == "FAVOR":
            self.mOrdUnit = XL_Unit.create(self.mEvalSpace, {
                "def": 2592,
                "default": 0,
                "kind": "numeric",
                "max": -1,
                "min": 0,
                "name": "_ord",
                "sub-kind": "int",
                "title": "Order nubler",
                "undef": 0,
                "vgroup": "Debug_Info"})
            self.mEvalSpace._addUnit(self.mOrdUnit, force_it = True)

        self.startService()

    def getEvalSpace(self):
        return self.mEvalSpace

    #===============================================
    def fiterRecords(self, condition, zone_data = None):
        assert zone_data is None
        rec_count = self.mEvalSpace.evalTotalCounts(condition)[0]
        assert rec_count <= AnfisaConfig.configOption("max.export.size")
        return self.mEvalSpace.evalRecSeq(condition, rec_count)

    #===============================================
    def prepareDTreePointCounts(self, dtree_h, rq_id,
            point_idxs = None, time_end = None):
        if self.mLongRunners is None:
            return DataSet.prepareDTreePointCounts(self, dtree_h, rq_id,
                point_idxs, time_end)
        with self:
            needs_start = False
            runner = self.mLongRunners.get(rq_id)
            if runner is None:
                runner = XL_LongRunner_DTreeCounts(
                    self, rq_id, dtree_h, point_idxs)
                needs_start =  True
                self.mLongRunners[rq_id] = runner
        if needs_start:
            self.getApp().runTask(runner, 2)
            point_idxs = None
        timeout = None
        if time_end is not None:
            time_now = datetime.now()
            if time_now < time_end:
                timeout = (time_end - time_now).total_seconds()
        return runner.getEvaluatedCounts(point_idxs, timeout)

    #===============================================
    def _cleanUpLongRunners(self):
        assert self.mLongRunners is not None
        cur_datetime = datetime.now()
        to_remove = []
        with self:
            for rq_id, runner in self.mLongRunners.items():
                if runner.outOfDate(cur_datetime):
                    to_remove.append(rq_id)
            for rq_id in to_remove:
                del self.mLongRunners[rq_id]
