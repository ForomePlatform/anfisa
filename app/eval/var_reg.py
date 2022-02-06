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

#===============================================
class VarFacetClassifier:
    def __init__(self):
        self.mDescr = []
        self.mFacetMaps = []
        self.mNames = set()

    def getSize(self):
        return len(self.mFacetMaps)

    def _regName(self, name):
        assert name not in self.mNames, (
            f"Name {name} duplication in facet declaration")
        self.mNames.add(name)

    def declareFacet(self, idx, facet_title, name_title_pairs):
        assert idx == len(self.mFacetMaps) + 1, (
            "Facets should be declared one by one")

        val_titles = []
        facet_map = dict()
        for name, title in name_title_pairs:
            self._regName(name)
            facet_map[name] = len(val_titles)
            val_titles.append(title)

        self.mDescr.append({
            "title": facet_title,
            "values": val_titles})
        self.mFacetMaps.append(facet_map)

    def mapFacetClassName(self, facet_idx, facet_name):
        if isinstance(facet_name, list):
            return sorted(self.mapFacetClassName(facet_idx, name)[0]
                for name in facet_name)

        assert facet_name in self.mFacetMaps[facet_idx], (
            f"Improper facet class name {facet_name}"
            f" for facet no {facet_idx + 1}")
        return [self.mFacetMaps[facet_idx][facet_name]]

    def getDescr(self):
        return self.mDescr

#===============================================
class VarRegistry:

    def __init__(self):
        self.mFacetClassifier = VarFacetClassifier()
        self.mVariables = dict()
        self.mTemplates = []
        self.mFixFunc = None
        self.mFixedNames = set()
        self.mCurFacets = [None, None, None]

    def setFixFunc(self, fix_func):
        self.mFixFunc = fix_func

    def relax(self, target):
        if len(self.mFixedNames) > 0:
            logging.warning(f"Fixed var names for {target}: "
                + " ".join(sorted(self.mFixedNames)))
            self.mFixedNames = set()

    def getClassificationDescr(self):
        return self.mFacetClassifier.getDescr()

    def setupClassificationFacet(self, facet_idx, title, name_title_pairs):
        self.mFacetClassifier.declareFacet(facet_idx, title, name_title_pairs)

    def predeclareClassification(self, cur_facet1, cur_facet2, cur_facet3):
        self.mCurFacets = [
            self.mFacetClassifier.mapFacetClassName(facet_idx, facet_name)
            for facet_idx, facet_name in enumerate(
                [cur_facet1, cur_facet2, cur_facet3])]

    def _prepareFacets(self, facets):
        ret = []
        for idx in range(self.mFacetClassifier.getSize()):
            if facets[idx] is not None:
                ret.append(
                    self.mFacetClassifier.mapFacetClassName(idx, facets[idx]))
            else:
                ret.append(self.mCurFacets[idx])
        return ret

    def regVar(self, var_name, var_type,
            title = None, render_mode = None, tooltip = None,
            facet1 = None, facet2 = None, facet3 = None):
        assert var_name not in self.mVariables, (
            "Variable name duplication: " + var_name)
        descr = {
            "name": var_name,
            "classes": self._prepareFacets([facet1, facet2, facet3])}
        assert all(info is not None for info in descr["classes"]), (
            "Facet classes are not correcly defined for: " + var_name)
        if title:
            descr["title"] = title
        if render_mode:
            descr["render-mode"] = render_mode
        if tooltip:
            descr["tooltip"] = tooltip
        self.mVariables[var_name] = [var_type, descr]

    def regVarTemplate(self, var_type, prefix, postfix = None,
            title = None, render_mode = None, tooltip = None,
            facet1 = None, facet2 = None, facet3 = None):
        assert title is None or '%' in title, (
            "Improper template: " + str(title))
        self.mTemplates.append([var_type, prefix, postfix,
            title, render_mode, tooltip,
            self._prepareFacets([facet1, facet2, facet3])])

    def getVarInfo(self, var_name, attempt = 0):
        if var_name in self.mVariables:
            return self.mVariables[var_name]
        for (var_type, prefix, postfix, title,
                render_mode, _tooltip, facets) in self.mTemplates:
            if not var_name.startswith(prefix):
                continue
            nm = var_name[len(prefix):]
            if postfix:
                if not var_name.endswith(postfix):
                    continue
                nm = var_name[:-len(postfix)]
            descr = {
                "name": var_name,
                "classes": facets}
            if title:
                descr["title"] = title % nm
            if render_mode:
                descr["render"] = render_mode
            return [var_type, descr]
        if attempt == 0 and self.mFixFunc is not None:
            fix_var_name = self.mFixFunc(var_name)
            if fix_var_name:
                self.mFixedNames.add(var_name)
                return self.getVarInfo(fix_var_name, 1)
        assert False, "No variable registered: " + str(var_name)
        return None


#===============================================
