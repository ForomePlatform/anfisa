# -*- coding: latin-1 -*-

from app.view.attr import AttrH

#===============================================
def _resetupAttr(aspect_h, attr_h):
    idx1 = aspect_h.find(attr_h.getName().lower())
    idx2 = aspect_h.find(attr_h.getName())
    if idx1 >= 0:
        aspect_h.delAttr(aspect_h[idx1])
    if idx2 >= 0:
        aspect_h.delAttr(aspect_h[idx2])
    aspect_h.addAttr(attr_h, min(idx1, idx2)
        if min(idx1, idx2) >=0 else max(idx1, idx2))

#===============================================
def tuneAspects(dataset, aspects):
    view_gen = aspects["view_gen"]
    view_db = aspects["view_db"]

    _resetupAttr(view_gen, UCSC_AttrH(view_gen))
    _resetupAttr(view_db, GTEx_AttrH(view_gen))
    _resetupAttr(view_db, OMIM_AttrH(view_gen))
    _resetupAttr(view_db, GREV_AttrH(view_gen))
    _resetupAttr(view_db, MEDGEN_AttrH(view_gen))

    if "meta" not in dataset.getDataInfo():
        return
    case = dataset.getDataInfo()["meta"].get("case")
    samples = dataset.getDataInfo()["meta"].get("samples")
    _resetupAttr(view_gen,
        IGV_AttrH(dataset.getApp(), view_gen, case, samples))

#===============================================
class UCSC_AttrH(AttrH):
    UCSC_URL = ("https://genome.ucsc.edu/cgi-bin/hgTracks?" +
               "db={assembly}&position={a}%3A{a}%2D{a}"
                   .format(assembly="hg19", a="{}"))

    def __init__(self, view_gen):
        AttrH.__init__(self, "UCSC")
        self.setAspect(view_gen)

    def htmlRepr(self, obj, top_rec_obj):
        start = int(top_rec_obj["data"]["start"])
        end = int(top_rec_obj["data"]["end"])
        link1 = self.UCSC_URL.format(
            top_rec_obj["data"]["seq_region_name"],
            max(0, start - 10), end + 10)
        link2 = self.UCSC_URL.format(
            top_rec_obj["data"]["seq_region_name"],
            max(0, start - 250), end + 250)
        return ('<table cellpadding="50"><tr><td>' +
                '<span title="Max Zoom In, 20bp range">' +
                ('<a href="%s" target="UCSC">Close Up</a>' % link1) +
                '</span> </td><td>' +
                '<span title="Zoom Out, 500bp range">' +
                ('<a href="%s" target="UCSC">Zoom Out</a>' % link2) +
                '</span> </td><td></table>',
                "norm")

#===============================================
class GTEx_AttrH(AttrH):
    GTEx_URL = ("https://www.gtexportal.org/home/gene/{}")

    def __init__(self, view):
        AttrH.__init__(self, "GTEx", title = "View on GTEx",
            tooltip = "View this gene on GTEx portal")
        self.setAspect(view)

    def htmlRepr(self, obj, top_rec_obj):
        genes = top_rec_obj["view"]["general"]["genes"]
        if (not genes):
            return None
        links = []
        for gene in genes:
            url = self.GTEx_URL.format(gene)
            links.append('<span title="GTEx">' +
            '<a href="{}" target="GTEx">{}</a>'.format(url, gene) +
            '</span>')
        return ('<br>'.join(links), "norm")

#===============================================
class OMIM_AttrH(AttrH):
    OMIM_URL = ("https://omim.org/search/?index=geneMap&feild=approved_gene_symbol&search={}")

    def __init__(self, view):
        AttrH.__init__(self, "OMIM")
        self.setAspect(view)

    def htmlRepr(self, obj, top_rec_obj):
        genes = top_rec_obj["view"]["general"]["genes"]
        if (not genes):
            return None
        links = []
        for gene in genes:
            url = self.OMIM_URL.format(gene)
            links.append('<span title="Search OMIM Gene Map for {}">'.format(gene) +
            '<a href="{}" target="OMIM">{}</a>'.format(url, gene) +
            '</span>')
        return ('<br>'.join(links), "norm")

#===============================================
class GREV_AttrH(AttrH):
    GeneRiveiws_URL = ("https://www.ncbi.nlm.nih.gov/books/NBK1116/?term={}")

    def __init__(self, view):
        AttrH.__init__(self, "GREV", title="GeneReviews", tooltip="Search GeneReviews")
        self.setAspect(view)

    def htmlRepr(self, obj, top_rec_obj):
        genes = top_rec_obj["view"]["general"]["genes"]
        if (not genes):
            return None
        links = []
        for gene in genes:
            url = self.GeneRiveiws_URL.format(gene)
            links.append('<span title="Search GeneReviews&reg; for {}">'.format(gene) +
            '<a href="{}" target="GREV">{}</a>'.format(url, gene) +
            '</span>')
        return ('<br>'.join(links), "norm")

#===============================================
class MEDGEN_AttrH(AttrH):
    MEDGEN_URL = ("https://www.ncbi.nlm.nih.gov/medgen/?term={}%5BGene%20Name%5D")

    def __init__(self, view):
        AttrH.__init__(self, "MEDGEN", title="MedGen", tooltip="Search MedGen")
        self.setAspect(view)

    def htmlRepr(self, obj, top_rec_obj):
        genes = top_rec_obj["view"]["general"]["genes"]
        if (not genes):
            return None
        links = []
        for gene in genes:
            url = self.MEDGEN_URL.format(gene)
            links.append('<span title="Search MedGen for {}">'.format(gene) +
            '<a href="{}" target="MEDGEN">{}</a>'.format(url, gene) +
            '</span>')
        return ('<br>'.join(links), "norm")


#===============================================
class IGV_AttrH(AttrH):
    def __init__(self, app, view_gen, case, samples):
        bam_base = app.getOption("http-bam-base")
        AttrH.__init__(self, "IGV",
            kind = "hidden" if bam_base is None else None)
        self.setAspect(view_gen)
        if bam_base is None:
            self.mPreUrl = None
            return
        samples_ids = [info["id"] for info in samples.values()]
        file_urls = ','.join([
            "{bam_base}/{case}/{sample}.hg19.bam".format(
                bam_base = bam_base,
                case = case,
                sample = sample_id)
            for sample_id in sorted(samples_ids)])
        name = ",".join(sorted([info["name"]
            for info in samples.values()]))
        self.mPreUrl = ("http://localhost:60151/load?file={file}"
            "&genome=hg19&merge=false&name={name}").format(
                file = file_urls, name = name)

    def htmlRepr(self, obj, top_rec_obj):
        if self.mPreUrl is None:
            return None
        start = int(top_rec_obj["data"]["start"])
        end = int(top_rec_obj["data"]["end"])
        link = self.mPreUrl + "&locus=%s:%d-%d" % (
            top_rec_obj["data"]["seq_region_name"],
            max(0, start - 250), end + 250)
        return ('<table><tr><td><span title="For this link to work, ' +
            'make sure that IGV is running on your computer">' +
            ('<a href="%s">View Variant in IGV</a>' % link) +
            ' </span></td><td><a href=' +
            '"https://software.broadinstitute.org/software/igv/download" ' +
            'target="_blank">' + 'Download IGV</a></td></tr></table>', "norm")
