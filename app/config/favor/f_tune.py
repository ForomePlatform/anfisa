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

from app.view.attr import AttrH
from app.model.region_func import RegionFuncUnit

# ===============================================
def tuneFavorAspects(ds_h, aspects):
    assert ds_h.getDataSchema() == "FAVOR", (
        "FAVOR fata schema expected: " + ds_h.getDataSchema())

    #  view_bas = aspects["view_bas"]
    # _resetupAttr(view_bas, HGMD_PMID_AttrH(view_bas))
    pass


# ===============================================
def tuneFavorUnits(ds_h):
    assert ds_h.getDataSchema() == "FAVOR", (
        "FAVOR fata schema expected: " + ds_h.getDataSchema())

    RegionFuncUnit.makeIt(ds_h,
        {
            "name":     "GeneRegion",
            "title":    "Gene Region",
            "vgroup":   "Coordinates"},
        {
            "chrom":    "Chromosome",
            "start":    "Position",
            "end":      "Position",
            "symbol":   "Symbol"
        }, before = "Chromosome")

# ===============================================
def completeFavorDS(ds_h):
    pass

# ===============================================
def _resetupAttr(aspect_h, attr_h):
    assert attr_h.getName().lower() != attr_h.getName(), (
        "Attribute " + attr_h.getName()
        + ": attributes for tuning resetup must contain uppercase letters")
    idx1 = aspect_h.find(attr_h.getName().lower())
    idx2 = aspect_h.find(attr_h.getName())
    if idx1 >= 0:
        aspect_h.delAttr(aspect_h[idx1])
    if idx2 >= 0:
        aspect_h.delAttr(aspect_h[idx2])
    aspect_h.addAttr(attr_h, min(idx1, idx2)
    if min(idx1, idx2) >= 0 else max(idx1, idx2))


# ===============================================
class PMID_AttrH(AttrH):

    @staticmethod
    def makeLink(pmid):
        return ("https://www.ncbi.nlm.nih.gov/pubmed/%s" % pmid)

    def __init__(self, view):
        AttrH.__init__(self, "REFERENCES",
            title = "Found in PubMed", tooltip = "PubMed Abstracts")
        self.setAspect(view)

    def get_pmids(self, v_context):
        return v_context["data"]["_view"]["hgmd_pmids"]

    def htmlRepr(self, obj, v_context):
        pmids = self.get_pmids(v_context)
        if (not pmids):
            return None
        links = []
        for pmid in pmids:
            url = self.makeLink(pmid)
            links.append(('<span title="PubMed abstracts for %s">' % pmid)
                + ('<a href="%s" target="PubMed">%s</a>' % (url, pmid))
                + '</span>')
        return (', '.join(links), "norm")

# ===============================================
class HGMD_PMID_AttrH(PMID_AttrH):
    def __init__(self, view):
        AttrH.__init__(self, "HGMD_PMIDs",
            title = "HGMD PMIDs", tooltip = "PubMed Abstracts (from HGMD)")
        self.setAspect(view)

    def get_pmids(self, v_context):
        return v_context["data"]["_view"]["general"]["hgmd_pmids"]
