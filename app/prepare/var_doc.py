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

import os, shutil
from app.config import getDS_Schema

#===============================================
class VariablesDocHandler:
    def __init__(self, doc_set_handler):
        assert doc_set_handler["id"] == "variables"
        assert doc_set_handler.get("mode") == "pre-build"
        self.mTitle = doc_set_handler["title"]
        self.mFarUrl = doc_set_handler.get("url")
        self.mWorkDir = doc_set_handler["source"]
        self.mDocPath = doc_set_handler["path"]
        self.mUsedFNames = set()
        self.mVarRefs = {}

        if os.path.exists(self.mWorkDir):
            shutil.rmtree(self.mWorkDir)
        #os.mkdir(self.mWorkDir)
        shutil.copytree(
            os.path.dirname(__file__) + "/../../doc/variables",
            self.mWorkDir)

        var_registry =  getDS_Schema(None).defineVariables()
        self.mFacetNames = var_registry.getFacetNames()

        index_doc = _IndexDocOutput(self)

        for idx, group_info in enumerate(var_registry.iterGroups()):
            group_doc = _GroupDocOutput(index_doc, idx+1, group_info)
            var_docs = []
            for attr_info in group_info["attributes"]:
                var_doc = _VariableDocOutput(group_doc, attr_info)
                assert var_doc.getFName() not in self.mVarRefs
                self.mVarRefs[var_doc.getName()] = var_doc.getFName()
                var_docs.append(var_doc)
            for var_doc in var_docs:
                var_doc.close()
            group_doc.close()
        index_doc.close()

    def formWorkFName(self, fname):
        assert fname not in self.mUsedFNames, "FName duplication: " + fname
        return self.mWorkDir + "/" + fname

    def getTitle(self):
        return self.mTitle

    def getFacetNames(self):
        return self.mFacetNames

    def getDocRef(self, var_name):
        ret = self.mVarRefs.get(var_name)
        if ret is not None:
            # TRF: form url!!!
            return ret
        return None


#===============================================
class _DocOutput:
    def __init__(self, master, fname):
        self.mMaster = master
        self.mFName = fname
        self.mOut = open(master.formWorkFName(fname) + ".rst",
            "w", encoding="utf-8")
        self.mTopics = []

    def getOut(self):
        return self.mOut

    def close(self):
        self.mOut.close()
        self.mOut = None

    def getFName(self):
        return self.mFName

    def getMaster(self):
        return self.mMaster

    def getTopics(self):
        return self.mTopics

    def relax(self):
        print(file=self.mOut)

    def printHeader(self, header, header_kind = "="):
        print(header, file=self.mOut)
        print(header_kind * len(header), file=self.mOut)
        self.relax()

    def startTocTree(self, max_depth=1):
        print(".. toctree::", file=self.mOut)
        print(f"    :maxdepth: {max_depth}", file=self.mOut)
        self.relax()

    def printTopic(self, topic):
        print(f"    {topic}", file=self.mOut)
        self.mTopics.append(topic)
        self.relax()

    def printRef(self, topic):
        print(f"* :ref:`{topic}`", file=self.mOut)

    def printRefDoc(self, topic):
        print(f"* :doc:`{topic}`", file=self.mOut)

    def _printLine_2(self, names):
        prefix = "   *"
        for nm in names:
            print(prefix + " - " +  nm, file=self.mOut)
            prefix = "    "

    def printTable_2(self, title, records, title_rec = None, width="30"):
        ncols = len(records[0])
        assert all(len(rec) == ncols for rec in records)
        ntitle = 0
        if title_rec is not None:
            assert len(title_rec) == ncols
            ntitle = 1

        print(f".. list-table:: {title}", file=self.mOut)
        print("   :widths: ", " ".join([width] * ncols),
            file=self.getOut())
        print(f"   :header-rows: {ntitle}", file=self.mOut)
        self.relax()
        if title_rec is not None:
            self._printLine_2(title_rec)
        for rec in records:
            self._printLine_2(rec)
        self.relax()

    def printTable(self, records, title_rec, title="", width="30"):
        ncols = len(records[0])
        assert all(len(rec) == ncols for rec in records)
        assert len(title_rec) == ncols
        print(f".. csv-table:: {title}", file=self.mOut)
        print("   :header: ", ", ".join(f'"{nm}"' for nm in title_rec),
            file=self.mOut)
        print("   :widths: ", ", ".join([width] * ncols),
            file=self.getOut())
        self.relax()

        for rec in records:
            print("   " + ", ".join(f'"{nm}"' for nm in rec),
            file=self.getOut())
        self.relax()
        self.relax()

    def printList(self, title, seq):
        if seq is None:
            return
        print(f"    **{title}**:", file=self.mOut)
        self.relax()
        for line in seq:
            print("        *", line, file=self.mOut)
            self.relax()

    def printDict(self, title, obj):
        if obj is None:
            return
        lst = []
        for key in sorted(obj.keys()):
            val = obj[key]
            lst.append(f"{key}: {val}")
        self.printList(title, lst)

    def printVal(self, title, value):
        if value is None:
            return
        print(f"    **{title}**: {value}", file=self.mOut)
        self.relax()

    def printText(self, title, value):
        if value is None:
            return
        print(f"    **{title}**:", file=self.mOut)
        self.relax()
        for line in value.split("\n"):
            print("    |", line, file=self.mOut)
        self.relax()

    def printIndex(self, topic):
        print(".. index:", file=self.mOut)
        print(f"    {topic}", file=self.mOut)
        self.relax()

#===============================================
class _IndexDocOutput(_DocOutput):
    def __init__(self, master):
        _DocOutput.__init__(self, master, "index")
        self.printHeader(self.getMaster().getTitle(), "-")
        self.printIndex("index")
        self.startTocTree()

#===============================================
class _GroupDocOutput(_DocOutput):
    def __init__(self, index_doc, no, group_info):
        _DocOutput.__init__(self, index_doc.getMaster(), f"group_{no}")
        index_doc.printTopic(self.getFName())
        self.mName = group_info["group"]

        self.printHeader("Group: " + self.mName)
        self.printIndex(self.getFName() + "; group")

        self.printText("Comment", group_info.get("comment"))
        self.startTocTree()

    def getName(self):
        return self.mName

    def close(self):
        self.printHeader("Index", "-")
        self.printRefDoc("index")
        self.relax()
        self.printRef("genindex")
        self.printRef("search")
        self.relax()
        _DocOutput.close(self)

#===============================================
class _VariableDocOutput(_DocOutput):
    @staticmethod
    def makeFName(name):
        return name.lower().replace("-", "_").replace("{}", "x")

    def __init__(self, group_doc, attr_info):
        _DocOutput.__init__(self, group_doc.getMaster(),
            self.makeFName(attr_info["attribute"]))
        self.mGroupFName = group_doc.getFName()
        self.mGroupDoc = group_doc
        self.mName = attr_info["attribute"]
        group_doc.printTopic(self.getFName())

        self.printHeader(self.mName)

        self.printIndex(self.getFName() + "; variable")

        self.printHeader("Classifiers", "-")
        facet_names = self.getMaster().getFacetNames()
        facet_values = [attr_info.get(key, "N/A")
            for key in facet_names]
        self.printTable([facet_values], facet_names)

        self.printHeader("Synopsis", "-")

        template_base = attr_info.get("template-base")
        if template_base is not None:
            print(f"    **Template Base**: {template_base}",
                file=self.getOut())
            self.relax()

        title = attr_info.get("title")
        if title and title != self.mName:
            print(f"    **Title**: {title}", file=self.getOut())
            self.relax()

        type_diag = attr_info["type"]
        transcript_mode = attr_info.get("transcript-mode")
        tr_mode_flex = attr_info.get("transcript-mode-flex")
        if transcript_mode == "master":
            type_diag += ", Transctipt master field"
        elif transcript_mode:
            type_diag += ", Transctipt based"
            if tr_mode_flex:
                type_diag += " (flexible)"
        elif tr_mode_flex:
           type_diag += "(transcript mode is flexible)"
        self.printVal("Type", type_diag)

        self.printVal("Panel", attr_info.get("panel"))
        self.printVal("Panel Type", attr_info.get("panel-type"))
        self.printVal("Reference", attr_info.get("reference"))

        self.printList("Alternative names", attr_info.get("alt-names"))

        self.printText("Comment", attr_info.get("comment"))
        self.printText("Desription (tooltip)", attr_info.get("description"))

        self.printList("Required modes", attr_info.get("requires"))

        self.printVal("Values bounds", attr_info.get("diap"))
        self.printVal("Default value", attr_info.get("default"))
        self.printList("Value variants", attr_info.get("variants"))
        self.printDict("Value map", attr_info.get("value-map"))
        self.printVal("Render mode", attr_info.get("render-mode"))

    def getName(self):
        return self.mName

    def close(self):
        self.printHeader("Variables in group " +
            self.mGroupDoc.getName(), "-")
        for nm in self.mGroupDoc.getTopics():
            if nm != self.getFName():
                self.printRefDoc(nm)
        self.relax()

        self.relax()
        self.printHeader("Indices", "-")
        self.printRefDoc("index")
        self.printRefDoc(self.mGroupFName)
        self.relax()
        _DocOutput.close(self)
