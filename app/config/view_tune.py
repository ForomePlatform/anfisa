# -*- coding: utf-8 -*-

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
from xml.sax.saxutils import escape

from app.view.attr import AttrH
from app.config.a_config import AnfisaConfig
from .favor import FavorSchema
import app.config.view_op_tune as view_op
#===============================================
def tuneAspects(ds_h, aspects):
    if ds_h.getDataSchema() == "FAVOR":
        FavorSchema.tuneAspects(ds_h, aspects)
        return

    if ds_h.getDataSchema() == "CASE":
        if ds_h.testRequirements({"WS"}):
            aspects.setAspectColumnMarkup("view_transcripts",
                view_op.markupTranscriptTab)
        ds_h.addConditionVisitorType(view_op.SamplesConditionVisitor)
        aspects.setAspectColumnMarkup("view_qsamples",
                view_op.SamplesColumnsMarkup(ds_h))

    view_gen = aspects["view_gen"]
    view_db = aspects["view_db"]
    view_t = aspects["view_transcripts"]
    view_pkgb = aspects["view_pharmagkb"]
    view_gnomad = aspects["view_gnomAD"]

    _resetupAttr(view_gen, UCSC_AttrH(view_gen, ds_h))
    _resetupAttr(view_gen, SymbolPanels_AttrH(view_gen, ds_h))
    attr_gnomad = _resetupAttr(view_gnomad, GnomAD_AttrH(view_gnomad))
    ds_h.regNamedAttr("gnomAD", attr_gnomad)
    attr_gtex = _resetupAttr(view_db, GTEx_AttrH(view_gen))
    ds_h.regNamedAttr("GTEx", attr_gtex)
    _resetupAttr(view_db, OMIM_AttrH(view_gen))
    _resetupAttr(view_db, GREV_AttrH(view_gen))
    _resetupAttr(view_db, MEDGEN_AttrH(view_gen))
    _resetupAttr(view_db, GENE_CARDS_AttrH(view_gen))
    _resetupAttr(view_db, BEACONS_AttrH(view_gen))
    _resetupAttr(view_db, PMID_AttrH(view_db))
    _resetupAttr(view_db, HGMD_PMID_AttrH(view_db))
    _resetupAttr(view_t,  UNIPROT_AttrH(view_t))
    _resetupAttr(view_t, TrSymbolPanels_AttrH(view_t, ds_h))
    _resetupAttr(view_pkgb, PGKB_AttrH(view_pkgb, "diseases", True))
    _resetupAttr(view_pkgb, PGKB_AttrH(view_pkgb, "chemicals", True))
    _resetupAttr(view_pkgb, PGKB_AttrH(view_pkgb, "pmids", True))
    _resetupAttr(view_pkgb, PGKB_AttrH(view_pkgb, "notes", False))

    attr_igv = _resetupAttr(view_gen, IGV_AttrH(ds_h, view_gen))
    ds_h.regNamedAttr("IGV", attr_igv)

    view_gen[view_gen.find("transcripts")].setReprFunc(
        view_op.reprGenTranscripts)
    _resetupAttr(view_gen, view_op.OpHasVariant_AttrH(view_gen, ds_h))
    if ds_h.getDSKind() == "ws":
        _resetupAttr(view_gen, view_op.OpFilters_AttrH(view_gen, ds_h))
        _resetupAttr(view_gen, view_op.OpDTrees_AttrH(view_gen, ds_h))

    setupNamedAttr(ds_h, "Samples", evalSamplesInfo)
    setupNamedAttr(ds_h, "GeneColored", evalGeneColored)
    setupNamedAttr(ds_h, "ColorCode", evalColorCode)

#===============================================
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
    return attr_h

#===============================================
class _AttributeProc:
    def __init__(self, process_func):
        self.mProcessFunc = process_func

    def makeValue(self, rec_data):
        return self.mProcessFunc(rec_data)

def setupNamedAttr(ds_h, name, process_func):
    ds_h.regNamedAttr(name, _AttributeProc(process_func))

#===============================================
class SymbolPanels_AttrH(AttrH):
    def __init__(self, view, ds_h):
        AttrH.__init__(self, "GENE_LISTS",
            title = "Gene lists",
            tooltip = "Gene lists positive on variant")
        self.mDS = ds_h
        self.setAspect(view)

    def htmlRepr(self, obj, v_context):
        genes = obj["genes"]
        return (' '.join(self.mDS.symbolsToPanels("Symbol", genes)), "norm")

#===============================================
class TrSymbolPanels_AttrH(AttrH):
    def __init__(self, view, ds_h):
        AttrH.__init__(self, "TR_GENE_LISTS",
            title = "Gene lists",
            tooltip = "Gene lists positive on transcript variant")
        self.mDS = ds_h
        self.setAspect(view)

    def htmlRepr(self, obj, v_context):
        genes = [obj.get("gene")]
        return (' '.join(self.mDS.symbolsToPanels("Symbol", genes)), "norm")

#===============================================
class UCSC_AttrH(AttrH):

    def makeLink(self, region_name, start, end, delta):
        return ("https://genome.ucsc.edu/cgi-bin/hgTracks?"
            f"db={self.mBase}&position={region_name}"
            f"%3A{max(0, start - delta)}%2D{end + delta}")

    def __init__(self, view_gen, ds_h):
        AttrH.__init__(self, "UCSC")
        self.setAspect(view_gen)
        meta_info = ds_h.getDataInfo()["meta"]
        reference = meta_info["versions"].get("reference")
        self.mBase = "hg38" if reference and "38" in reference else "hg19"

    def htmlRepr(self, obj, v_context):

        start = int(v_context["data"]["__data"]["start"])
        end = int(v_context["data"]["__data"]["end"])
        start, end = sorted([start, end])
        region_name = v_context["data"]["__data"]["seq_region_name"]
        link1 = self.makeLink(region_name, start, end, 10)
        link2 = self.makeLink(region_name, start, end, 250)
        return ('<table cellpadding="50"><tr><td>'
                '<span title="Max Zoom In, 20bp range">'
                f'<a href="{link1}" target="UCSC">Close Up</a>'
                '</span> </td><td>'
                '<span title="Zoom Out, 500bp range">'
                f'<a href="{link2}" target="UCSC">Zoom Out</a>'
                '</span> </td><td></table>', "norm")

#===============================================
class GnomAD_AttrH(AttrH):

    @staticmethod
    def makeLink(region_name, start, end, delta):
        return ("https://gnomad.broadinstitute.org/region/"
            f"{region_name}%3A{max(0, start - delta)}%2D{end + delta}")

    @staticmethod
    def wrap(url, text = "gnomAD Browser"):
        link = ('<span title="View in gnomAD browser">'
                f'<a href="{url}" target="gnomAD">{text}</a></span>')
        return link

    @staticmethod
    def make_attr(url):
        if isinstance(url, list):
            if len(url) == 1:
                url = url[0]
            else:
                links = []
                for u in url:
                    links.append(GnomAD_AttrH.wrap(u, u))
                return ('<br>'.join(links), "norm")
        return (GnomAD_AttrH.wrap(url), "norm")

    def __init__(self, view):
        AttrH.__init__(self, "URL")
        self.setAspect(view)

    def makeValue(self, rec_data):
        url = rec_data["_view"]["gnomAD"]["url"]
        if url:
            return url
        hg19 = rec_data["_view"]["general"]["hg19"]
        if (not hg19) or hg19.lower() == 'none':
            return "No HG19 mapping!"
        try:
            region_name = rec_data["__data"]["seq_region_name"]
            region = (rec_data["_view"]["general"]["hg19"].
                split(':')[1].split('-'))
            start = int(region[0])
            if (len(region) > 1):
                end = int(region[1])
                start, end = sorted([start, end])
            else:
                end = start
            return self.makeLink(region_name, start, end, 3)
        except Exception:
            return "error!"

    def htmlRepr(self, obj, v_context):
        url = self.makeValue(v_context["data"])
        if url and isinstance(url, str) and url.endswith('!'):
            return (url, "norm")
        return self.make_attr(url)

#===============================================
class GTEx_AttrH(AttrH):

    @staticmethod
    def makeLink(gene):
        return "https://www.gtexportal.org/home/gene/" + gene

    def __init__(self, view):
        AttrH.__init__(self, "GTEx", title = "View on GTEx",
            tooltip = "View this gene on GTEx portal")
        self.setAspect(view)

    def makeValue(self, rec_data):
        genes = rec_data["_view"]["general"]["genes"]
        if (not genes):
            return None
        links = []
        for gene in genes:
            links.append([gene, self.makeLink(gene)])
        return links

    def htmlRepr(self, obj, v_context):
        links = self.makeValue(v_context["data"])
        if not links:
            return None
        ret = []
        for gene, url in links:
            ret.append('<span title="GTEx">'
                f'<a href="{url}" target="GTEx">{gene}</a></span>')
        return ('<br>'.join(ret), "norm")

#===============================================
class OMIM_AttrH(AttrH):

    @staticmethod
    def makeLink(gene):
        return ("https://omim.org/search/?"
            "index=geneMap&feild=approved_gene_symbol"
            f"&search={gene}")

    def __init__(self, view):
        AttrH.__init__(self, "OMIM")
        self.setAspect(view)

    def makeValue(self, rec_data):
        genes = rec_data["_view"]["general"]["genes"]
        if (not genes):
            return None
        links = []
        for gene in genes:
            links.append([gene, self.makeLink(gene)])
        return links

    def htmlRepr(self, obj, v_context):
        links = self.makeValue(v_context["data"])
        if links is None:
            return None
        ret = []
        for gene, url in links:
            ret.append(
                f'<span title="Search OMIM Gene Map for {escape(gene)}">'
                f'<a href="{url}" target="OMIM">{gene}</a></span>')
        return ('<br>'.join(ret), "norm")
#===============================================
class GREV_AttrH(AttrH):

    @staticmethod
    def makeLink(gene):
        return f"https://www.ncbi.nlm.nih.gov/books/NBK1116/?term={gene}"

    def __init__(self, view):
        AttrH.__init__(self, "GREV", title = "GeneReviews®",
            tooltip = "Search GeneReviews®")
        self.setAspect(view)

    def htmlRepr(self, obj, v_context):
        genes = v_context["data"]["_view"]["general"]["genes"]
        if (not genes):
            return None
        links = []
        for gene in genes:
            url = self.makeLink(gene)
            links.append(
                f'<span title="Search GeneReviews&reg; for {escape(gene)}">'
                f'<a href="{url}" target="GREV">{gene}</a></span>')
        return ('<br>'.join(links), "norm")

#===============================================
class MEDGEN_AttrH(AttrH):

    @staticmethod
    def makeLink(gene):
        return ("https://www.ncbi.nlm.nih.gov/medgen/?term="
            + gene + "%5BGene%20Name%5D")

    def __init__(self, view):
        AttrH.__init__(self, "MEDGEN",
            title = "MedGen", tooltip = "Search MedGen")
        self.setAspect(view)

    def htmlRepr(self, obj, v_context):
        genes = v_context["data"]["_view"]["general"]["genes"]
        if (not genes):
            return None
        links = []
        for gene in genes:
            url = self.makeLink(gene)
            links.append(
                f'<span title="Search MedGen for {escape(gene)}'
                f'<a href="{url}" target="MEDGEN">{gene}</a></span>')
        return ('<br>'.join(links), "norm")

#===============================================
class GENE_CARDS_AttrH(AttrH):

    @staticmethod
    def makeLink(gene):
        return ("https://www.genecards.org/cgi-bin/carddisp.pl?gene=" + gene)

    def __init__(self, view):
        AttrH.__init__(self, "GENE_CARDS",
            title = "GeneCards", tooltip = "Read GeneCards")
        self.setAspect(view)

    def htmlRepr(self, obj, v_context):
        genes = v_context["data"]["_view"]["general"]["genes"]
        if (not genes):
            return None
        links = []
        for gene in genes:
            url = self.makeLink(gene)
            links.append(
                f'<span title="Read GeneCards for {escape(gene)}">'
                f'<a href="{url}" target="GeneCards">{gene}</a></span>')
        return ('<br>'.join(links), "norm")

#===============================================
class BEACONS_AttrH(AttrH):
    @classmethod
    def makeLink(cls, chrom, pos, ref, alt):
        return ("https://beacon-network.org/#/search?"
            f"pos={pos}&chrom={chrom}&allele={alt}&ref={ref}&rs=GRCh37")

    def __init__(self, view):
        AttrH.__init__(self, "BEACONS",
            title = "Beacons",
            tooltip = "Search what other organizations have "
                      "observed the same variant")
        self.setAspect(view)

    def htmlRepr(self, obj, v_context):
        chrom = v_context["data"]["__data"]["seq_region_name"]
        pos = v_context["data"]["__data"]["start"]
        ref = v_context["data"]["_filters"]["ref"]
        alt = v_context["data"]["_filters"]["alt"]

        url = self.makeLink(chrom, pos, ref, alt)
        link = ('<span title="Search Beacons">'
            f'<a href="{url}" target="Beacons">Search Beacons</a></span>')
        return (link, "norm")

#===============================================
class _PMID_AttrH(AttrH):

    @staticmethod
    def makeLink(pmid):
        return f"https://www.ncbi.nlm.nih.gov/pubmed/{pmid}"

    def __init__(self, view, name, title, tooltip):
        AttrH.__init__(self, name, title = title, tooltip = tooltip)
        self.setAspect(view)

    @classmethod
    def make_span(cls, pmid):
        url = cls.makeLink(pmid)
        return (f'<span title="PubMed abstracts for {escape(pmid)}">'
            f'<a href="{url}" target="PubMed">{pmid}</a></span>')

    def htmlRepr(self, obj, v_context):
        pmids = self.get_pmids(v_context)
        if (not pmids):
            return None
        links = []
        for pmid in pmids:
            if pmid:
                links.append(self.make_span(pmid))
        return (', '.join(links), "norm")

#===============================================
class PMID_AttrH(_PMID_AttrH):
    def __init__(self, view):
        _PMID_AttrH.__init__(self, view, "REFERENCES",
            title = "Found in PubMed", tooltip = "PubMed Abstracts")

    def get_pmids(self, v_context):
        return v_context["data"]["_view"]["databases"]["references"]

#===============================================
class HGMD_PMID_AttrH(_PMID_AttrH):
    def __init__(self, view):
        _PMID_AttrH.__init__(self, view, "HGMD_PMIDs",
            title = "HGMD PMIDs", tooltip = "PubMed Abstracts (from HGMD)")

    def get_pmids(self, v_context):
        return v_context["data"]["__data"]["hgmd_pmids"]

#===============================================
class IGV_AttrH(AttrH):
    def __init__(self, ds_h, view_gen):
        AttrH.__init__(self, "IGV")
        self.mDataVault = ds_h.getDataVault()
        self.mDsRootName = ds_h.getRootDSName()
        self.setAspect(view_gen)

        meta_info = ds_h.getDataInfo()["meta"]

        # we are not sure what is the key to samples, so have to repackage
        samples_data = meta_info.get("samples")
        samples = {info["id"]: info["name"] for info in samples_data.values()}
        self.mSamplesIds = sorted(samples.keys())
        self.mSamplesNames = ",".join([samples[id] for id in self.mSamplesIds])

        reference = meta_info["versions"].get("reference")
        self.mBase = "hg38" if reference and "38" in reference else "hg19"
        self.mIGV_Url = False
        self.mPreUrl = None
        self._checkPreUrl()

    def _checkPreUrl(self):
        igv_url = self.mDataVault.getIGVUrl(self.mDsRootName)
        if igv_url == self.mIGV_Url:
            return self.mPreUrl is not None
        self.mIGV_Url = igv_url
        if not self.mIGV_Url:
            self.reset("hidden", False)
            self.mPreUrl = None
            return False
        self.reset(None, False)
        file_urls = ','.join([
            f"{igv_url}/{sample_id}.{self.mBase}.bam"
            for sample_id in self.mSamplesIds])
        self.mPreUrl = (f"http://localhost:60151/load?file={file_urls}"
            f"&genome={self.mBase}&merge=false&name={self.mSamplesNames}")
        return True

    def makeValue(self, rec_data):
        if not self._checkPreUrl():
            return None

        if self.mBase == "hg19":
            start = int(rec_data["__data"]["start"])
            end = int(rec_data["__data"]["end"])
        else:
            assert self.mBase == "hg38", (
                "Position base not supported: " + self.mBase)
            pos = -1
            try:
                pos = rec_data["_view"]["general"]["hg38"]
                _, _, coors = pos.partition(':')
                coors = coors.split(' ')[0]
                p0, _, p1 = coors.partition('-')
                start = int(p0.strip())
                end = int(p1.strip()) if p1 else start
            except Exception:
                logging.error("Error creating IGV link for " + str(pos))
                return "Error!"
        start, end = sorted([start, end])
        locus = rec_data["__data"]["seq_region_name"]
        return (self.mPreUrl
            + f'&locus={locus}:{max(0, start - 250)}-{end + 250}')

    def htmlRepr(self, obj, v_context):
        link = self.makeValue(v_context["data"])
        if link is None:
            return None
        if link.endswith('!'):
            return (link, "norm")
        return ('<table><tr><td><span title="For this link to work, '
            'make sure that IGV is running on your computer">'
            f'<a href="{link}">View Variant in IGV</a>'
            ' </span></td><td><a href='
            '"https://software.broadinstitute.org/software/igv/download"'
            ' target="_blank">'
            'Download IGV</a></td></tr></table>', "norm")

#===============================================
class UNIPROT_AttrH(AttrH):
    base_url = "https://www.uniprot.org/uniprot/%s"

    def __init__(self, view):
        AttrH.__init__(self, "UNIPROT_ACC",
            title = "Uniprot", tooltip = "View on Uniprot site")
        self.setAspect(view)

    @classmethod
    def makeLink(cls, acc):
        if '-' not in acc:
            return cls.base_url % acc
        parts = acc.split('-')
        return cls.base_url % parts[0] + "#" + acc

    def htmlRepr(self, obj, v_context):
        uniprot = obj.get("uniprot_acc")
        if (not uniprot):
            return ('-', "none")
        url = self.makeLink(uniprot)
        link = ('<span title="Uniprot">'
            f'<a href="{url}" target="Uniprot">{escape(uniprot)}</a></span>')
        return (link, "norm")


#===============================================
class PGKB_AttrH(AttrH):
    def __init__(self, view, key, is_simple):
        AttrH.__init__(self, key.upper(), title = key.title())
        self.setAspect(view)
        self.key = key
        self.simple = is_simple

    def collect(self, items):
        result = dict()
        for item in items:
            key = item["association"]
            value = item["value"]
            if self.key == "pmids":
                value = _PMID_AttrH.make_span(value)
            if key in result:
                result[key].append(value)
            else:
                result[key] = [value]
        return result

    def draw_table(self, items, f):
        content = ["<table>"]
        for key in items:
            value = f(key, items)
            content.append(
                "<tr><td>" + key + "</td><td>" + value + "</td></tr>")
        content.append("</table>")
        return "\n".join(content)

    def draw_simple_table(self, items):
        return self.draw_table(items,
            lambda key, entries: ", ".join(entries[key]))

    def draw_nested_table(self, items):
        return self.draw_table(items, self.draw_inner_table)

    def draw_inner_table(self, key, items):
        content = ["ul"]
        for item in items[key]:
            content.append("<li>" + item + "</li>")
        content.append("</ul>")
        return "\n".join(content)

    def make_table(self, obj, key):
        if not obj:
            return None
        items = obj.get(key)
        if not items:
            return None
        collection = self.collect(items)

        if self.simple:
            table = self.draw_simple_table(collection)
        else:
            table = self.draw_nested_table(collection)

        return table

    def htmlRepr(self, obj, v_context):
        table = self.make_table(obj, self.key)
        if not table:
            return None
        html = f'<span title="PKGB_{self.key}">' + table + '</span>'
        return (html, "norm")

#===============================================
def evalSamplesInfo(rec_data):
    ret = dict()
    for smp_info in rec_data["_view"]["quality_samples"][1:]:
        smp_id = smp_info["title"].split(':')[-1].strip()
        ret[smp_id] = {
            "genotype":  smp_info.get("genotype"),
            "g_quality": smp_info.get("genotype_quality")}
    return ret

#===============================================
def evalGeneColored(rec_data):
    genes = rec_data["_view"]["general"]["genes"]
    pli = rec_data["_view"]["gnomAD"].get("pLI")

    pli_value = pli[0] if (pli and len(pli) == 1 and pli[0]) else 0
    color_code = (30 if pli_value >= 0.9 else
        (20 if pli_value >= 0.5 else 10))

    return [genes, color_code]

#===============================================
def evalColorCode(rec_data):
    return AnfisaConfig.normalizeColorCode(
        rec_data["__data"].get("color_code"))

#===============================================
