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
import abc
from cachetools import LRUCache

from app.config.a_config import AnfisaConfig
#===============================================
class EvalSpace:
    def __init__(self, ds_h):
        self.mDS = ds_h
        self.mUnits = []
        self.mUnitDict = dict()
        self.mOpCache = LRUCache(
            AnfisaConfig.configOption("op.cache.size"))

    def getDS(self):
        return self.mDS

    def getName(self):
        return self.mDS.getName()

    def heavyMode(self):
        return False

    @abc.abstractmethod
    def getZygUnit(self, idx):
        assert False

    @abc.abstractmethod
    def iterZygUnits(self):
        assert False

    def _addUnit(self, unit_h):
        self.mUnits.append(unit_h)
        assert unit_h.getName() not in self.mUnitDict, (
            "Duplicate unit name: " + unit_h.getName())
        self.mUnitDict[unit_h.getName()] = unit_h

    def _insertUnit(self, unit_h,
            before = None, after = None, insert_idx = None):
        assert unit_h.getName() not in self.mUnitDict, (
            "Duplicate unit name: " + unit_h.getName())
        if insert_idx is None:
            last_vgroup_idx = None, None
            for idx, u_h in enumerate(self.mUnits):
                if before is not None and u_h.getName() == before:
                    insert_idx = idx
                    break
                if after is not None and u_h.getName() == after:
                    insert_idx = idx + 1
                    break
                if u_h.getVGroup() == unit_h.getVGroup():
                    last_vgroup_idx = idx
        if insert_idx is None:
            if last_vgroup_idx is not None:
                insert_idx = last_vgroup_idx + 1
            else:
                insert_idx = len(self.mUnits)
        self.mUnits.insert(insert_idx, unit_h)
        self.mUnitDict[unit_h.getName()] = unit_h

    def _addReservedUnit(self, meta_unit_h):
        assert meta_unit_h.getName() not in self.mUnitDict, (
            "Duplicate meta unit name: " + meta_unit_h.getName())
        self.mUnitDict[meta_unit_h.getName()] = meta_unit_h

    def getUnit(self, unit_name):
        return self.mUnitDict.get(unit_name)

    def iterUnits(self):
        return iter(self.mUnits)

    def joinAnd(self, seq):
        ret = self.getCondAll()
        for cond in seq:
            ret = ret.addAnd(cond)
        return ret

    def joinOr(self, seq):
        ret = self.getCondNone()
        for cond in seq:
            ret = ret.addOr(cond)
        return ret

    def getOpCacheValue(self, unit_name, hash_code):
        return self.mOpCache.get(unit_name + '|' + hash_code)

    def setOpCacheValue(self, unit_name, hash_code, data):
        with self.mDS:
            self.mOpCache[unit_name + '|' + hash_code] = data
