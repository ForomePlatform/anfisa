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

    _resetupAttr(view_gen, UCSC_AttrH(view_gen))
    _resetupAttr(view_gnomad, GnomAD_AttrH(view_gnomad))
    _resetupAttr(view_db, GTEx_AttrH(view_gen))
    _resetupAttr(view_db, OMIM_AttrH(view_gen))
    _resetupAttr(view_db, GREV_AttrH(view_gen))
    _resetupAttr(view_db, MEDGEN_AttrH(view_gen))
    _resetupAttr(view_db, GENE_CARDS_AttrH(view_gen))
    _resetupAttr(view_db, BEACONS_AttrH(view_gen))
    _resetupAttr(view_db, PMID_AttrH(view_db))
    _resetupAttr(view_db, HGMD_PMID_AttrH(view_db))
    _resetupAttr(view_t,  UNIPROT_AttrH(view_t))
    _resetupAttr(view_pkgb, PGKB_AttrH(view_pkgb, "diseases", True))
    _resetupAttr(view_pkgb, PGKB_AttrH(view_pkgb, "chemicals", True))
    _resetupAttr(view_pkgb, PGKB_AttrH(view_pkgb, "pmids", True))
    _resetupAttr(view_pkgb, PGKB_AttrH(view_pkgb, "notes", False))

    meta_info = ds_h.getDataInfo()["meta"]
    _resetupAttr(view_gen, IGV_AttrH(ds_h.getApp(), view_gen,
        meta_info.get("case"), meta_info.get("samples"),
        meta_info["versions"].get("reference")))

    view_gen[view_gen.find("transcripts")].setReprFunc(
        view_op.reprGenTranscripts)
    _resetupAttr(view_gen, view_op.OpHasVariant_AttrH(view_gen, ds_h))
    if ds_h.getDSKind() == "ws":
        _resetupAttr(view_gen, view_op.OpFilters_AttrH(view_gen, ds_h))
        _resetupAttr(view_gen, view_op.OpDTreess_AttrH(view_gen, ds_h))

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

#===============================================
class UCSC_AttrH(AttrH):

    @staticmethod
    def makeLink(region_name, start, end, delta, assembly = "hg19"):
        return ("https://genome.ucsc.edu/cgi-bin/hgTracks?"
            + ("db=%s" % assembly)
            + ("&position=%s" % region_name)
            + "%3A" + str(max(0, start - delta))
            + "%2D" + str(end + delta))

    def __init__(self, view_gen):
        AttrH.__init__(self, "UCSC")
        self.setAspect(view_gen)

    def htmlRepr(self, obj, v_context):
        start = int(v_context["data"]["__data"]["start"])
        end = int(v_context["data"]["__data"]["end"])
        region_name = v_context["data"]["__data"]["seq_region_name"]
        link1 = self.makeLink(region_name, start, end, 10)
        link2 = self.makeLink(region_name, start, end, 250)
        return ('<table cellpadding="50"><tr><td>'
                + '<span title="Max Zoom In, 20bp range">'
                + ('<a href="%s" target="UCSC">Close Up</a>' % link1)
                + '</span> </td><td>'
                + '<span title="Zoom Out, 500bp range">'
                + ('<a href="%s" target="UCSC">Zoom Out</a>' % link2)
                + '</span> </td><td></table>', "norm")

#===============================================
class GnomAD_AttrH(AttrH):

    @staticmethod
    def makeLink(region_name, start, end, delta):
        return ("https://gnomad.broadinstitute.org/region/"
            + ("%s" % region_name)
            + "%3A" + str(max(0, start - delta))
            + "%2D" + str(end + delta))

    @staticmethod
    def wrap(url, text = "gnomAD Browser"):
        link = ('<span title="View in gnomAD browser">'
               + ('<a href="%s" target="gnomAD">%s</a>' % (url, text))
               + '</span>')
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

    def htmlRepr(self, obj, v_context):
        url = v_context["data"]["_view"]["gnomAD"]["url"]
        if url:
            return self.make_attr(url)
        hg19 = v_context["data"]["_view"]["general"]["hg19"]
        if (not hg19) or hg19.lower() == 'none':
            return ("No HG19 mapping", "norm")
        try:
            region_name = v_context["data"]["__data"]["seq_region_name"]
            region = (v_context["data"]["_view"]["general"]["hg19"].
                split(':')[1].split('-'))
            start = int(region[0])
            if (len(region) > 1):
                end = int(region[1])
            else:
                end = start
            url = self.makeLink(region_name, start, end, 3)
            return self.make_attr(url)
        except Exception:
            return ("error", "norm")

#===============================================
class GTEx_AttrH(AttrH):

    @staticmethod
    def makeLink(gene):
        return "https://www.gtexportal.org/home/gene/" + gene

    def __init__(self, view):
        AttrH.__init__(self, "GTEx", title = "View on GTEx",
            tooltip = "View this gene on GTEx portal")
        self.setAspect(view)

    def htmlRepr(self, obj, v_context):
        genes = v_context["data"]["_view"]["general"]["genes"]
        if (not genes):
            return None
        links = []
        for gene in genes:
            url = self.makeLink(gene)
            links.append('<span title="GTEx">'
                + ('<a href="%s" target="GTEx">%s</a>' % (url, gene))
                + '</span>')
        return ('<br>'.join(links), "norm")

#===============================================
class OMIM_AttrH(AttrH):

    @staticmethod
    def makeLink(gene):
        return ("https://omim.org/search/?"
            + "index=geneMap&feild=approved_gene_symbol"
            + "&search=" + str(gene))

    def __init__(self, view):
        AttrH.__init__(self, "OMIM")
        self.setAspect(view)

    def htmlRepr(self, obj, v_context):
        genes = v_context["data"]["_view"]["general"]["genes"]
        if (not genes):
            return None
        links = []
        for gene in genes:
            url = self.makeLink(gene)
            links.append(
                ('<span title="Search OMIM Gene Map for %s">' % escape(gene))
                + ('<a href="%s" target="OMIM">%s</a>' % (url, gene))
                + '</span>')
        return ('<br>'.join(links), "norm")

#===============================================
class GREV_AttrH(AttrH):

    @staticmethod
    def makeLink(gene):
        return "https://www.ncbi.nlm.nih.gov/books/NBK1116/?term=" + gene

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
                ('<span title="Search GeneReviews&reg; for %s">'
                    % escape(gene))
                + ('<a href="%s" target="GREV">%s</a>' % (url, gene))
                + '</span>')
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
            links.append(('<span title="Search MedGen for %s">' % escape(gene))
                + ('<a href="%s" target="MEDGEN">%s</a>' % (url, gene))
                + '</span>')
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
                ('<span title="Read GeneCards for %s">' % escape(gene))
                + ('<a href="%s" target="GeneCards">%s</a>' % (url, gene))
                + '</span>')
        return ('<br>'.join(links), "norm")

#===============================================
class BEACONS_AttrH(AttrH):
    sBase = "https://beacon-network.org/#/search?"
    sArgs = "pos={pos}&chrom={chrom}&allele={alt}&ref={ref}&rs=GRCh37"

    @classmethod
    def makeLink(cls, chrom, pos, ref, alt):
        return cls.sBase + (cls.sArgs.format(
            chrom = chrom, pos = pos, ref = ref, alt = alt))

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
        link = (('<span title="Search Beacons">')
            + ('<a href="%s" target="Beacons">Search Beacons</a>' % (url))
            + '</span>')
        return (link, "norm")

#===============================================
class _PMID_AttrH(AttrH):

    @staticmethod
    def makeLink(pmid):
        return ("https://www.ncbi.nlm.nih.gov/pubmed/%s" % pmid)

    def __init__(self, view, name, title, tooltip):
        AttrH.__init__(self, name, title = title, tooltip = tooltip)
        self.setAspect(view)

    @classmethod
    def make_span(cls, pmid):
        url = cls.makeLink(pmid)
        return (('<span title="PubMed abstracts for %s">' % escape(pmid))
                + ('<a href="%s" target="PubMed">%s</a>' % (url, pmid))
                + '</span>')

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
    def __init__(self, app, view_gen, case, samples, reference):
        bam_base = app.getOption("http-bam-base")
        AttrH.__init__(self, "IGV",
            kind = "hidden" if bam_base is None else None)
        self.mBase = "hg38" if reference and "38" in reference else "hg19"
        self.setAspect(view_gen)
        if bam_base is None:
            self.mPreUrl = None
            return

        # we are not sure what is the key to samples, so have to repackage
        samples = {info["id"]: info["name"] for info in samples.values()}
        samples_ids = sorted(samples)
        samples_names = [samples[id] for id in samples_ids]

        file_urls = ','.join([
            "%s/%s/%s.%s.bam" % (bam_base, case, sample_id, self.mBase)
            for sample_id in samples_ids])
        self.mPreUrl = ("http://localhost:60151/load?file=%s"
            "&genome=%s&merge=false&name=%s") % (
                file_urls, self.mBase, ",".join(samples_names))

    def htmlRepr(self, obj, v_context):
        if self.mPreUrl is None:
            return None

        if self.mBase == "hg19":
            start = int(v_context["data"]["__data"]["start"])
            end = int(v_context["data"]["__data"]["end"])
        else:
            assert self.mBase == "hg38"
            pos = -1
            try:
                pos = v_context["data"]["_view"]["general"]["hg38"]
                _, _, coors = pos.partition(':')
                coors = coors.split(' ')[0]
                p0, _, p1 = coors.partition('-')
                start = int(p0.strip())
                end = int(p1.strip()) if p1 else start
            except Exception:
                logging.error("Error creating IGV link for " + str(pos))
                return ("ERROR", "norm")
        link = self.mPreUrl + "&locus=%s:%d-%d" % (
            v_context["data"]["__data"]["seq_region_name"],
            max(0, start - 250), end + 250)
        return ('<table><tr><td><span title="For this link to work, '
            + 'make sure that IGV is running on your computer">'
            + ('<a href="%s">View Variant in IGV</a>' % link)
            + ' </span></td><td><a href='
            + '"https://software.broadinstitute.org/software/igv/download"'
            + ' target="_blank">'
            + 'Download IGV</a></td></tr></table>', "norm")

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
            + ('<a href="%s" target="Uniprot">%s</a>' % (url, escape(uniprot)))
            + '</span>')
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
        html = "<table>"
        for key in items:
            html += "<tr><td>"
            html += key
            html += "</td><td>"
            html += f(key, items)
            html += "</td></tr>"
        html += "</table>"
        return html

    def draw_simple_table(self, items):
        return self.draw_table(items,
            lambda key, entries: ", ".join(entries[key]))

    def draw_nested_table(self, items):
        return self.draw_table(items, self.draw_inner_table)

    def draw_inner_table(self, key, items):
        html = "<ul>"
        for item in items[key]:
            html += "<li>" + item + "</li>"
        html += "</ul>"
        return html

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
        html = ('<span title="PKGB_%s"> %s </span>' % (self.key, table))
        return (html, "norm")
