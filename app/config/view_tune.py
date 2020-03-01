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
import json
from xml.sax.saxutils import escape
from bitarray import bitarray

from app.view.attr import AttrH
from .favor import FavorSchema
#===============================================
def tuneAspects(ds_h, aspects):
    if ds_h.getDataSchema() == "FAVOR":
        FavorSchema.tuneAspects(ds_h, aspects)
        return
    view_gen = aspects["view_gen"]
    view_db = aspects["view_db"]

    _resetupAttr(view_gen, UCSC_AttrH(view_gen))
    _resetupAttr(view_db, GTEx_AttrH(view_gen))
    _resetupAttr(view_db, OMIM_AttrH(view_gen))
    _resetupAttr(view_db, GREV_AttrH(view_gen))
    _resetupAttr(view_db, MEDGEN_AttrH(view_gen))
    _resetupAttr(view_db, GENE_CARDS_AttrH(view_gen))
    _resetupAttr(view_db, BEACONS_AttrH(view_gen))
    _resetupAttr(view_db, PMID_AttrH(view_db))
    _resetupAttr(view_db, HGMD_PMID_AttrH(view_db))

    if "meta" not in ds_h.getDataInfo():
        return
    meta_info = ds_h.getDataInfo()["meta"]
    reference = meta_info["versions"].get("reference", "")
    if not reference:
        reference = ""
    _resetupAttr(view_gen, IGV_AttrH(ds_h.getApp(), view_gen,
        meta_info.get("case"), meta_info.get("samples"),
        "hg38" if "38" in reference else "hg19"))

    view_gen[view_gen.find("transcripts")].setReprFunc(reprGenTranscripts)

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
                ('<span title="Search OMIM Gene Map for %s">' % gene)
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
                ('<span title="Search GeneReviews&reg; for %s">' % gene)
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
            links.append(('<span title="Search MedGen for %s">' % gene)
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
            links.append(('<span title="Read GeneCards for %s">' % gene)
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
class PMID_AttrH(AttrH):

    @staticmethod
    def makeLink(pmid):
        return ("https://www.ncbi.nlm.nih.gov/pubmed/%s" % pmid)

    def __init__(self, view):
        AttrH.__init__(self, "REFERENCES",
            title = "Found in PubMed", tooltip = "PubMed Abstracts")
        self.setAspect(view)

    def get_pmids(self, v_context):
        return v_context["data"]["_view"]["databases"]["references"]

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

#===============================================
class HGMD_PMID_AttrH(PMID_AttrH):
    def __init__(self, view):
        AttrH.__init__(self, "HGMD_PMIDs",
            title = "HGMD PMIDs", tooltip = "PubMed Abstracts (from HGMD)")
        self.setAspect(view)

    def get_pmids(self, v_context):
        return v_context["data"]["__data"]["hgmd_pmids"]

#===============================================
class IGV_AttrH(AttrH):
    def __init__(self, app, view_gen, case, samples, base_ref = "hg19"):
        bam_base = app.getOption("http-bam-base")
        AttrH.__init__(self, "IGV",
            kind = "hidden" if bam_base is None else None)
        self.mBaseRef = "hg19"
        self.setAspect(view_gen)
        if bam_base is None:
            self.mPreUrl = None
            return

        # we are not sure what is the key to samples, so have to repackage
        samples = {info["id"]: info["name"] for info in samples.values()}
        samples_ids = sorted(samples)
        samples_names = [samples[id] for id in samples_ids]

        file_urls = ','.join([
            "%s/%s/%s.%s.bam" % (bam_base, case, sample_id, self.mBaseRef)
            for sample_id in samples_ids])
        self.mPreUrl = ("http://localhost:60151/load?file=%s"
            "&genome=%s&merge=false&name=%s") % (
                file_urls, self.mBaseRef, ",".join(samples_names))

    def htmlRepr(self, obj, v_context):
        if self.mPreUrl is None:
            return None
        if self.mBaseRef == "hg38":
            # ???
            pass
        else:
            start = int(v_context["data"]["__data"]["start"])
            end = int(v_context["data"]["__data"]["end"])
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
def reprGenTranscripts(val, v_context):
    if not val:
        return None
    if "details" in v_context:
        details = bitarray(v_context["details"])
    else:
        details = None

    ret_handle = ['<ul>']
    for idx, it in enumerate(val):
        if details is not None and details[idx]:
            mod = ' class="hit"'
        else:
            mod = ''
        ret_handle.append(
            "<li%s><b>%s</b>, <b>gene=</b>%s, <b>annotations</b>: %s </li>"
            % (mod, escape(it.get("id", "?")), escape(it.get("gene", "?")),
            escape(json.dumps(it.get("transcript_annotations", "?")))))
    ret_handle.append("</ul>")
    return ('\n'.join(ret_handle), "norm")
