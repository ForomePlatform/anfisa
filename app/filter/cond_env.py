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
from cachetools import LRUCache

#===============================================
class CondEnv:
    def __init__(self, ds_name, locker_obj):
        self.mDSName = ds_name
        self.mLockerObj = locker_obj
        self.mSpecialUnits = dict()
        self.mNumUnits = dict()
        self.mEnumUnits = dict()
        self.mOperativeUnits = dict()
        self.mReservedNames = dict()
        self.mOpUnitSeq = []
        self.mCompCache = dict()

    def addNumUnit(self, unit_h):
        assert unit_h.getName() not in self.mNumUnits
        self.mNumUnits[unit_h.getName()] = unit_h

    def addEnumUnit(self, unit_h):
        assert unit_h.getName() not in self.mEnumUnits
        self.mEnumUnits[unit_h.getName()] = unit_h

    def addSpecialUnit(self, unit_h):
        assert unit_h.getName() not in self.mSpecialUnits
        self.mSpecialUnits[unit_h.getName()] = unit_h

    def addOperativeUnit(self, unit_h):
        assert unit_h.getName() not in self.mOperativeUnits
        self.mOperativeUnits[unit_h.getName()] = unit_h
        self.mOpUnitSeq.append(unit_h)

    def addReservedUnit(self, unit_h):
        assert unit_h.getName() not in self.mReservedNames
        self.mReservedNames[unit_h.getName()] = unit_h

    def iterOpUnits(self):
        return iter(self.mOpUnitSeq)

    def nameIsReserved(self, name):
        return name in self.mReservedNames

    def getDSName(self):
        return self.mDSName

    def getLocker(self):
        return self.mLockerObj

    def detectUnit(self, unit_name,
            expect_kind = None, use_logging = True):
        unit_kind, unit_h = self._detectUnit(unit_name)
        if (use_logging and expect_kind is not None
                and expect_kind != unit_kind
                and unit_kind not in {"special", "reserved", "operational"}):
            logging.warning("Mix-up in unit kinds for name=%s/%s asked %s" %
                (unit_name, unit_kind, str(expect_kind)))
            return None, None
        return unit_kind, unit_h

    def _detectUnit(self, unit_name):
        if unit_name in self.mOperativeUnits:
            return ("operational", self.mOperativeUnits[unit_name])
        if unit_name in self.mNumUnits:
            return ("numeric", self.mNumUnits[unit_name])
        if unit_name in self.mEnumUnits:
            return ("enum", self.mEnumUnits[unit_name])
        if unit_name in self.mSpecialUnits:
            return ("special", self.mSpecialUnits[unit_name])
        if unit_name in self.mReservedNames:
            return ("reserved", self.mReservedNames[unit_name])
        return None, None

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

    def getCompCache(self, unit_name, hash_code):
        if unit_name in self.mCompCache:
            return self.mCompCache[unit_name].get(hash_code)
        return None

    sCacheSize = 3

    def setCompCache(self, unit_name, hash_code, comp_data):
        with self.mLockerObj:
            if unit_name not in self.mCompCache:
                self.mCompCache[unit_name] = LRUCache(self.sCacheSize)
            self.mCompCache[unit_name][hash_code] = comp_data
