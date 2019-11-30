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

from app.config.a_config import AnfisaConfig
#===============================================
class SolutionTypeHandler:
    sStdFMark = AnfisaConfig.configOption("filter.std.mark")

    def __init__(self, ds_h, sol_agent, key, filter_class):
        self.mDS = ds_h
        self.mSolAgent = sol_agent
        self.mKey = key
        self.mFltClass = filter_class
        self.mNames = []
        self.mFltDict = dict()
        for it in self.mDS.iterStdItems(self.mKey):
            std_name = self.sStdFMark + it.getName()
            self.mNames.append(std_name)
            self.mFltDict[std_name] = self.mFltClass(
                self.mDS.getCondEnv(), it.getData(), std_name)
        self.mStdCount = len(self.mNames)
        for info in self.mSolAgent.iterEntries(self.mKey):
            name, value, upd_time, upd_from = info
            self.mNames.append(name)
            self.mFltDict[name] = self.mFltClass(
                self.mDS.getCondEnv(), value, name = name,
                updated_time = upd_time, updated_from = upd_from)
        self.mHashDict = {flt_obj.getHashCode(): flt_obj
            for flt_obj in self.mFltDict.values()}

    def refreshSolEntries(self):
        _names = []
        updated = False
        for info in self.mSolAgent.iterEntries(self.mKey):
            name, value, upd_time, upd_from = info
            _names.append(name)
            flt_obj = self.mFltDict.get(name)
            if (flt_obj is not None
                    and [upd_time, upd_from] != flt_obj.getUpdateInfo()):
                del self.mHashDict[flt_obj.getHashCode()]
                flt_obj = None
            if flt_obj is None:
                flt_obj = self.mFltClass(
                    self.mDS.getCondEnv(), value, name = name,
                    updated_time = upd_time, updated_from = upd_from)
                self.mFltDict[name] = flt_obj
                self.mHashDict[flt_obj.getHashCode()] = flt_obj
                updated = True
        for name in (set(self.mNames[self.mStdCount:]) - set(_names)):
            flt_obj = self.mFltDict[name]
            del self.mHashDict[flt_obj.getHashCode()]
            del self.mFltDict[name]
            updated = True
        if updated:
            self.mNames = self.mNames[:self.mStdCount] + _names
        return updated

    def getList(self):
        ret_handle = []
        for idx, name in enumerate(self.mNames):
            flt_obj = self.mFltDict[name]
            info = [name, idx < self.mStdCount, True]
            info += flt_obj.getUpdateInfo()
            info.append(flt_obj.noErrors())
            ret_handle.append(info)
        return ret_handle

    def modify(self, instr, value):
        option, _, name = instr.partition('/')
        assert (name and not name.startswith(self.sStdFMark)
            and name[0].isalpha() and ' ' not in name)
        return self.mSolAgent.modifyEntry(
            self.mDS, self.mKey, option, name, value)

    def updateFltObj(self, flt_obj):
        upd_flt_obj = self.mHashDict.get(flt_obj.getHashCode())
        if upd_flt_obj is not None:
            return upd_flt_obj
        return flt_obj

    def pickByHash(self, hash_code):
        return self.mHashDict.get(hash_code)

    def pickByName(self, name):
        return self.mFltDict[name]
