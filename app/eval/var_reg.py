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
import re


from forome_tools.ident import checkIdentifier
from forome_tools.yaml_supp import YProperty, YClass

#===============================================
class FacetClassifier:
    sVariantClass = YClass([
        YProperty("id", required=True),
        YProperty("name", required=True)
        ])

    sClass = YClass([
        YProperty("facet", required=True),
        YProperty("title", required=True),
        YProperty("variants", sVariantClass,
            is_seq=True, required=True)
        ])

    def __init__(self, facet_descr_seq):
        self.mDescr = []
        self.mFacetMaps = []
        self.mFacetAllNamesMap = []
        for facet_descr in facet_descr_seq:
            self._loadFacet(facet_descr)

    def _loadFacet(self, facet_info):
        val_names = []
        val_titles = []
        facet_map = dict()
        facet_all_map = dict()
        for variant_info in facet_info["variants"]:
            name = variant_info["id"]
            assert checkIdentifier(name, ext_mode=True), (
                "Facet variant id is not an identifier: " + name)
            title = variant_info["name"]
            assert name not in facet_map, (
                "Facet variant id duplication: " + name)
            assert title not in facet_all_map, (
                "Facet variant name duplication: " + title)
            facet_map[name] = len(val_titles)
            facet_all_map[name] = len(val_titles)
            facet_all_map[title] = len(val_titles)
            val_names.append(name)
            val_titles.append(title)

        self.mDescr.append({
            "name": facet_info["facet"],
            "title": facet_info["title"],
            "names": val_names,
            "values": val_titles})
        self.mFacetMaps.append(facet_map)
        self.mFacetAllNamesMap.append(facet_all_map)

    def getSize(self):
        return len(self.mFacetMaps)

    def getYProperties(self):
        return [YProperty(facet_info["name"])
            for facet_info in self.mDescr]

    def mapFacetClassName(self, facet_idx, facet_name):
        assert facet_name in self.mFacetMaps[facet_idx], (
            f"Improper facet class name {facet_name}"
            f" for facet no {facet_idx + 1}")
        return self.mFacetMaps[facet_idx][facet_name]

    def getDescr(self):
        return self.mDescr

    def prepareFacetIdxSet(self, descr):
        ret = []
        for idx, facet_info in enumerate(self.mDescr):
            val = descr.get(facet_info["name"])
            if val is not None:
                facet_idx = self.mapFacetClassName(idx, val)
            else:
                facet_idx = len(facet_info["names"]) - 1
            ret.append(facet_idx)
        return ret

    def checkMetaAnnotation(self, facet, fvalue):
        for idx, descr in enumerate(self.mDescr):
            if descr["name"] == facet:
                return (idx, self.mFacetAllNamesMap[idx].get(fvalue)), None
        return None, f"Wrong meta annotation group: {facet}"

#===============================================
class VarRegistry:
    sListClass = YClass([
        YProperty("list", required=True),
        YProperty("values", is_seq=True, required=True)
        ])

    sMapClass = YClass([
        YProperty("map", required=True),
        YProperty("values", dict, required=True)
        ])

    sConfigClass = YClass([
        YProperty("facets", FacetClassifier.sClass,
            is_seq=True, required=True),
        YProperty("lists", sListClass, is_seq=True),
        YProperty("maps", sMapClass, is_seq=True)
        ])

    def prepareGroupAttrClass(self):
        attr_properties = [
            YProperty("attribute", required=True),
            YProperty("template-base"),
            YProperty("panel"),
            YProperty("title"),
            YProperty("alt-names", is_seq=True),
            YProperty("type", required=True),
            YProperty("transcript-mode"),
            YProperty("transcript-mode-flex", bool),
            YProperty("panel-type")]

        attr_properties += self.mFacetClassifier.getYProperties()

        attr_properties += [
            YProperty("comment"),
            YProperty("description"),
            YProperty("reference"),
            YProperty("requires", is_seq=True),
            YProperty("diap"),
            YProperty("default"),
            YProperty("variants"),
            YProperty("value-map"),
            YProperty("render-mode"),
            ]

        attrClass = YClass(attr_properties)
        groupClass = YClass([
            YProperty("group", required=True),
            YProperty("comment"),
            YProperty("attributes", attrClass, is_seq=True, required=True)
        ])

        return groupClass

    def __init__(self, config_fname, var_fname):
        config_data = self.sConfigClass.loadFile(config_fname)
        self.mFacetClassifier = FacetClassifier(config_data["facets"])
        self.mPresetMaps = {entry["map"]: entry["values"]
            for entry in config_data["maps"]}
        self.mPresetLists = {entry["list"]: entry["values"]
            for entry in config_data["lists"]}

        groupClass = self.prepareGroupAttrClass()
        self.mGroupsData = groupClass.loadFile(var_fname)

        self.mVariables = {}
        self.mTemplates = {}
        for group_info in self.mGroupsData:
            for var_descr in group_info["attributes"]:
                self._regVar(var_descr)
#        for group_info in self.mGroupsData:
#            for var_descr in group_info["attributes"]:
#                if var_descr["type"] == "variety":
#                    assert var_descr["panel"] in self.mVariables, (
#                        "Variable " + var_descr["attribute"] + " panel " +
#                        var_descr["panel"] + " is not found")
#                    panel_descr = self.mVariables[var_descr["panel"]]
#                    assert (panel_descr["type"] == "panel" and
#                        (not var_descr.get("transcript-mode")) ==
#                        (not panel_descr.get("transcript-mode"))), (
#                        "Variable " + var_descr["attribute"] + "panel " +
#                        var_descr["panel"] + " is inconsistent")

    #===============================================
    def getClassificationDescr(self):
        return self.mFacetClassifier.getDescr()

    def checkMetaAnnotation(self, facet, fvalue):
        return self.mFacetClassifier.checkMetaAnnotation(facet, fvalue)

    def getFacetNames(self):
        return [prop.getName()
            for prop in self.mFacetClassifier.getYProperties()]

    #===============================================
    sRegExLetters = re.compile(r'[\W_]+')

    @classmethod
    def normName(cls, name):
        return re.sub(cls.sRegExLetters, '', name.lower())

    #===============================================
    def _regName(self, name, descr, kind="attribute", ):
        assert checkIdentifier(name), f"Not an identifier as {kind}: {name}"
        norm_name = self.normName(name)
        if norm_name in self.mVariables:
            ref_name = self.mVariables[norm_name]["attribute"]
            assert False, (
                f"Name collision: {kind} {name} vs definition of {ref_name}")
        self.mVariables[norm_name] = descr

    #===============================================
    sSupportedTypes = {
        "func", "int", "float", "status", "multiset",
        "panel", "presence", "variety"
    }

    sNumericRenderModes = {"neighborhood"} | {f"{mode},{ord}"
        for mode in ("linear", "log") for ord in ("<", ">", "=")}

    #===============================================
    def _regVar(self, var_descr):
        var_name = var_descr["attribute"]
        if var_descr.get("template-base"):
            assert var_name not in self.mTemplates, (
                "Name duplication in templates: " + var_descr["attribute"])
            self.mTemplates[var_name] = var_descr
        else:
            self._regName(var_name, var_descr)
            alt_names = var_descr.get("alt-names")
            if alt_names:
                for nm in alt_names:
                    self._regName(nm, var_descr, "alt-attr-name")

        if var_descr.get("transcript-mode"):
            assert var_descr["transcript-mode"] in (
                "True", "true", "master"), (
                f"Attribute {var_name}: option transcript-mode should be " +
                "'true' or absent (or once 'master')")

        if var_descr.get("transcript-mode-flex"):
            assert var_descr["transcript-mode-flex"] == True, (
                f"Attribute {var_name}: option transcript-mode-flex should be " +
                "true or absent")

        var_type = var_descr.get("type")
        assert var_type, f"Attribute {var_name} should be set"
        var_descr["var-type"] = var_type
        assert var_type in self.sSupportedTypes, (
            f"Attribute {var_name}: unsupported type {var_type}")

        if var_type == "variety":
            assert var_descr.get("panel"), (
                f"Attribute {var_name} of type variety:" +
                " panel option should be set")
            panel_name = var_descr["panel"]
            assert checkIdentifier(panel_name), (
                f"Attribute {var_name}: panel name " +
                f"is not an identifier: {panel_name} ")
            assert var_descr.get("panel-type") == "Symbol", (
                f"Attribute {var_name} of type variety:" +
                " panel-type option shoul be set to Symbol " +
                "(only Symbol is supported now)")
            # self._regName(var_descr["panel"], var_descr, "panel-name")
        else:
            assert var_descr.get("panel") is None, (
                f"Attribute {var_name} of type {var_type}:" +
                " panel option is out of sense")
            assert var_descr.get("panel-type") is None, (
                f"Attribute {var_name} of type {var_type}:" +
                " panel-type option is out of sense")

        if "title" not in var_descr:
            var_descr["title"] = var_name

        var_descr["facets"] = (
            self.mFacetClassifier.prepareFacetIdxSet(var_descr))

        if var_descr.get("requires"):
            var_descr["requires"] = set(var_descr["requires"])

        if var_descr.get("diap"):
            assert var_type in ("int", "float"), (
                f"Attribute {var_name} of type {var_type}:" +
                " diap option is out of sense")
            diap = var_descr["diap"].strip()
            assert diap[0] == '[' and diap[-1] == ']', (
                f"Attribute {var_name}: bad diap option")
            values = diap[1:-1].split(',')
            assert len(values) == 2, (
                f"Attribute {var_name}: bad diap option")
            res = []
            for val in values:
                try:
                    if var_type == "int":
                        res.append(int(val))
                    else:
                        res.append(float(val))
                except Exception:
                    assert False, "Attribute {var_name}: bad diap option {diap}"
            var_descr["diap"] = res

        if var_type in ("int", "float") and var_descr.get("transcript-mode"):
            assert var_descr.get("default") is not None, (
                f"Attribute {var_name}: transcript numeric fields " +
                "requires default")

        if var_descr.get("variants") is not None:
            assert var_type in ("status", "multiset"), (
                f"Attribute {var_name} of type {var_type}:" +
                " variants option is out of sense")
            variants_name = var_descr["variants"]
            assert variants_name in self.mPresetLists, (
                f"Attribute {var_name}: undefined variant list: " +
                variants_name)
            var_descr["variants"] = self.mPresetLists[variants_name]

        if var_descr.get("value-map") is not None:
            assert var_type in ("status", "multiset"), (
                f"Attribute {var_name} of type {var_type}:" +
                " value-map option is out of sense")
            map_name = var_descr["value-map"]
            assert map_name in self.mPresetMaps, (
                f"Attribute {var_name}: undefined value map: " +
                map_name)
            var_descr["value-map"] = self.mPresetMaps[map_name]

        if var_descr.get("render-mode") is not None:
            render_mode = var_descr["render-mode"]
            if var_type in ("int", "float"):
                assert render_mode in self.sNumericRenderModes, (
                    f"Attribute {var_name}: improper numeric render mode: " +
                    render_mode)
            elif render_mode != "tree-map":
                assert (var_type, render_mode) == ("status", "pie") or (
                    var_type, render_mode) == ("multiset", "bar"), (
                    f"Attribute {var_name}: " +
                    f"improper {var_type} render mode: {render_mode}")

    def __getitem__(self, var_name):
        nm = self.normName(var_name)
        assert nm in self.mVariables, "Attribute not found: " + var_name
        return self.mVariables[nm]

    def __contains__(self, var_name):
        nm = self.normName(var_name)
        return nm in self.mVariables

    def iterGroups(self):
        return iter(self.mGroupsData)

    def makeTemplatedVarSeq(self, template_name, names):
        template_descr = self.mTemplates[template_name]
        for name in names:
            var_descr = {key: val for key, val in template_descr.items()}
            del var_descr["template-base"]
            var_descr["attribute"] = var_descr["attribute"].replace('{}', name)
            var_descr["title"] = var_descr["title"].replace('{}', name)
            if var_descr.get("alt-names"):
                var_descr["alt-names"] = [nm.replace('{}', name)
                    for nm in var_descr["alt-names"]]
            self._regVar(var_descr)

#===============================================
