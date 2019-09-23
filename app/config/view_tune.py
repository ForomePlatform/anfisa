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
        link = self.UCSC_URL.format(
            top_rec_obj["data"]["seq_region_name"],
            max(0, start - 50), end + 50)
        return ('<span title="UCSC">' +
            ('<a href="%s" target="UCSC">View in UCSC</a>' % link) +
            '</span>', "norm")

#===============================================
class GTEx_AttrH(AttrH):
    GTEx_URL = ("https://www.gtexportal.org/home/gene/{}")

    def __init__(self, view):
        AttrH.__init__(self, "GTEx")
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
class IGV_AttrH(AttrH):
    def __init__(self, app, view_gen, case, samples):
        bam_base = app.getOption("http-bam-base")
        AttrH.__init__(self, "IGV",
            kind = "hidden" if bam_base is None else None)
        self.setAspect(view_gen)
        if bam_base is None:
            self.mPreUrl = None
            return
        file_urls = ','.join([
            "{bam_base}/{case}/{sample}.hg19.bam".format(
                bam_base = bam_base,
                case = case,
                sample = sample)
            for sample in sorted(samples.keys())])
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
