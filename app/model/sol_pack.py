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

#===============================================
def codeHash(tree_code):
    return md5(bytes(tree_code.strip(), 'utf-8')).hexdigest()

#===============================================
class SolutionItem:
    def __init__(self, kind, name, data, requires,
            used_names, ext_name = None):
        self.mKind = kind
        self.mName = name
        self.mRequires = requires
        self.mData = data
        use_name = ext_name if ext_name else self.mName
        assert use_name not in used_names
        used_names.add(use_name)

    def testIt(self, kind, test_f):
        if kind is not None and self.mKind != kind:
            return False
        return test_f(self.mRequires)

    def getName(self):
        return self.mName

    def getData(self):
        return self.mData

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
        assert solution_pack.getName() not in cls.sPacks
        cls.sPacks[solution_pack.getName()] = solution_pack

    @classmethod
    def regDefaultPack(cls, solution_pack):
        assert None not in cls.sPacks
        cls.sPacks[None] = solution_pack

    @classmethod
    def select(cls, pack_name = None):
        if pack_name not in cls.sPacks:
            logging.warning("Unregistered pack name: " + pack_name)
            pack_name = None
        return cls.sPacks[pack_name]

    #===============================================
    def __init__(self, name):
        self.mName = name
        self.mItems = []
        self.mUsedNames = set()

    def getName(self):
        return self.mName

    def regFilter(self, flt_name, cond_seq, requires = None):
        self.mItems.append(SolutionItem("filter", flt_name,
            cond_seq, requires, self.mUsedNames))

    def regDTree(self, tree_name, fname_seq, requires = None):
        tree_code = self.readFileSeq(fname_seq)
        it = SolutionItem("dtree", tree_name,
            tree_code, requires, self.mUsedNames)
        self.mItems.append(it)

    def regPanel(self, unit_name, panel_name, fname, requires = None):
        self.mItems.append(SolutionItem("panel", unit_name,
            (panel_name, self.readListFile(fname)), requires,
            self.mUsedNames, unit_name + "/" + panel_name))

    def regZone(self, zone_title, unit_name, requires = None):
        self.mItems.append(SolutionItem("zone",
            zone_title,  unit_name, requires, self.mUsedNames))

    def regTabSchema(self, tab_schema, requires = None):
        self.mItems.append(SolutionItem("tab-schema",
            tab_schema.getName(), tab_schema, requires, self.mUsedNames))

    #===============================================
    def iterItems(self, kind, test_f):
        for it in self.mItems:
            if it.testIt(kind, test_f):
                yield it

    def getTreeByHashCode(self, hash_code):
        return self.mTreeCodes.get(hash_code)
