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
from hashlib import md5
from app.eval.dtree import DTreeEval
from app.eval.condition import condDataUnits
from .sol_support import makeSolItemInfo

#===============================================
def codeHash(tree_code):
    return md5(bytes(tree_code.strip(), 'utf-8')).hexdigest()

#===============================================
class SolutionPack:
    @classmethod
    def readFile(cls, fname):
        with open(fname, "r", encoding = "utf-8") as inp:
            return inp.read()
        assert False
        return None

    @classmethod
    def readFileSeq(cls, fnames):
        return "\n".join([cls.readFile(fname) for fname in fnames])

    @classmethod
    def readListFile(cls, fname):
        ret = []
        with open(fname, "r", encoding = "utf-8") as inp:
            for line in inp:
                val = line.partition('#')[0].strip()
                if val:
                    ret.append(val)
        return ret

    #===============================================
    sPacks = dict()

    @classmethod
    def regPack(cls, solution_pack):
        assert solution_pack.getName() not in cls.sPacks, (
            "Soluton pack is already registered: " + solution_pack.getName())
        cls.sPacks[solution_pack.getName()] = solution_pack

    @classmethod
    def regDefaultPack(cls, solution_pack):
        assert None not in cls.sPacks, "Default pack is already set"
        cls.sPacks[None] = solution_pack

    @classmethod
    def select(cls, pack_name = None):
        if pack_name not in cls.sPacks:
            logging.warning("Unregistered pack name: " + pack_name)
            pack_name = None
        if pack_name is None:
            return []
        return cls.sPacks[pack_name]

    #===============================================
    def __init__(self, name, check_units_func = None):
        self.mName = name
        self.mItems = []
        self.mCheckUnitsFunc = check_units_func
        self.mUsedNames = set()
        self.regPack(self)

    def getName(self):
        return self.mName

    def __iter__(self):
        return iter(self.mItems)

    def regFilter(self, flt_name, cond_seq,
            requires = None, rubric = None):
        if self.mCheckUnitsFunc is not None:
            unit_names = set()
            for cond_data in cond_seq:
                unit_names |= condDataUnits(cond_data)
            if not self.mCheckUnitsFunc("filter",
                    flt_name, unit_names, requires):
                return
        self.mItems.append(makeSolItemInfo(
            "filter", flt_name, cond_seq, rubric,
            used_names = self.mUsedNames, requires = requires, is_std = True))

    def regDTree(self, tree_name, fname_seq,
            requires = None, rubric= None):
        tree_code = self.readFileSeq(fname_seq)
        if self.mCheckUnitsFunc is not None:
            dtree_h = DTreeEval(None, tree_code)
            if not self.mCheckUnitsFunc("dtree",
                    tree_name, dtree_h.getActiveUnitSet(), requires):
                return
        self.mItems.append(makeSolItemInfo(
            "dtree", tree_name, tree_code, rubric,
            used_names = self.mUsedNames, requires = requires, is_std = True))

    def regPanel(self, panel_name, panel_type,
            fname = None, items = None,
            requires = None, rubric = None):
        assert (fname is not None) ^ (items is not None), (
            f"Collision: fname={fname} / items={items is not None}")
        if fname:
            items = self.readListFile(fname)
        else:
            assert isinstance(items, list)
        self.mItems.append(makeSolItemInfo(
            "panel." + panel_type, panel_name, items, rubric,
            used_names = self.mUsedNames, requires = requires, is_std = True))

    def regItemDict(self, name, the_dict, requires = None):
        self.mItems.append(makeSolItemInfo(
            "item-dict", name, the_dict, None,
            used_names = self.mUsedNames, requires = requires, is_std = True))

    def regZone(self, zone_title, unit_name, requires = None):
        self.mItems.append(makeSolItemInfo(
            "zone", zone_title, unit_name, None,
            used_names = self.mUsedNames, requires = requires, is_std = True))

    def regTabSchema(self, tab_schema, requires = None, rubric = None):
        self.mItems.append(makeSolItemInfo(
            "tab-schema", tab_schema.getName(), tab_schema, rubric,
            used_names = self.mUsedNames, requires = requires, is_std = True))
