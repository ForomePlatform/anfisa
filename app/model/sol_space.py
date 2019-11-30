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
from threading import Lock

from utils.lock_obj import ObjWithLock
from .sol_pack import SolutionPack
#===============================================
class SolutionSpace(ObjWithLock):
    def __init__(self, modes = None, pack_name = None):
        ObjWithLock.__init__(self)
        self.mSolPack = SolutionPack.select(pack_name)
        self.mLock  = Lock()
        self.mModes = set()
        self.addModes(modes)
        self.mStdFilterDict = None
        self.mStdFilterList = None
        self.mFilterCache = None

    #===============================================
    def addModes(self, modes):
        if modes:
            self.mModes |= set(modes)

    def testRequirements(self, modes):
        if not modes:
            return True
        return len(modes & self.mModes) == len(modes)

    def iterStdItems(self, item_kind):
        return self.mSolPack.iterItems(item_kind, self.testRequirements)

    #===============================================
    def getUnitPanelNames(self, unit_name):
        ret = []
        for it in self.iterStdItems("panel"):
            if it.getName() == unit_name:
                ret.append(it.getData()[0])
        return ret

    def getUnitPanel(self, unit_name, panel_name, assert_mode = True):
        for it in self.iterStdItems("panel"):
            if it.getName() == unit_name:
                if it.getData()[0] == panel_name:
                    return it.getData()[1]
        if assert_mode:
            assert False, "%s: Panel %s not found" % (unit_name, panel_name)
        else:
            logging.warning("%s: Panel %s not found" % (unit_name, panel_name))

    #===============================================
    def getFilters(self):
        return [(it.getName(), it.getData())
            for it in self.iterStdItems("filter")]

    #===============================================
    def getStdTreeCodeNames(self):
        return [it.getName() for it in self.iterStdItems("tree_code")]

    def getStdTreeCode(self, code_name):
        for it in self.iterStdItems("dtree"):
            if it.getName() == code_name or code_name is None:
                return it.getData()
        logging.error("Request for bad std tree: " + code_name)
        assert False

    #===============================================
    def reportSolutions(self):
        panel_info = dict()
        for it in self.iterStdItems("panel"):
            unit_name = it.getName()
            if unit_name in panel_info:
                panel_info[unit_name].append(it.getData()[0])
            else:
                panel_info[unit_name] = [it.getData()[0]]
        return {
            "codes": [it.getName()
                for it in self.iterStdItems("tree_code")],
            "panels": panel_info}
