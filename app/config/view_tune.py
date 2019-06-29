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

    _resetupAttr(view_gen, UCSC_AttrH(view_gen))

    if "meta" not in dataset.getDataInfo():
        return
    case = dataset.getDataInfo()["meta"].get("case")
    samples = dataset.getDataInfo()["meta"].get("samples")
    _resetupAttr(view_gen, IGV_AttrH(view_gen, case, samples))

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
            max(0, start - 250), end + 250)
        return ('<span title="UCSC">' +
            ('<a href="%s" target="UCSC">View in UCSC</a>' % link) +
            '</span>', "norm")

#===============================================
class IGV_AttrH(AttrH):
    def __init__(self, view_gen, case, samples):
        AttrH.__init__(self, "IGV")
        self.setAspect(view_gen)
        host_name = AttrH.normLink("anfisa.forome.org")
        file_urls = ','.join([
            "http://{host}/anfisa/links/{case}/{sample}.hg19.bam".format(
                host = host_name,
                case = case,
                sample = sample)
            for sample in sorted(samples.keys())])
        name = ",".join(sorted([info["name"] for info in samples.values()]))
        self.mPreUrl = ("http://localhost:60151/load?file={file}"
            "&genome=hg19&merge=false&name={name}").format(
                file = file_urls, name = name)

    def htmlRepr(self, obj, top_rec_obj):
        start = int(top_rec_obj["data"]["start"])
        end = int(top_rec_obj["data"]["end"])
        link = self.mPreUrl + "&locus=%s:%d-%d" % (
            top_rec_obj["data"]["seq_region_name"],
            max(0, start - 250), end + 250)
        # return ('<span title="Run IGV application...">' +
        #     ('<a href="%s">link</a>' % link) +
        #     '<span class="igv_comment">(for this link to work, make sure ' +
        #     '<a href="https://software.broadinstitute.org/software/igv/' +
        #     'download" target="_blank"> the IGV app</a> '+
        #     'is running on your computer)</span></span>', "norm")
        return ('<table><tr><td><span title="For this link to work, ' +
            'make sure that IGV is running on your computer">' +
            ('<a href="%s">View Variant in IGV</a>' % link) +
            ' </span></td><td><a href=' +
            '"https://software.broadinstitute.org/software/igv/download" ' +
            'target="_blank">' + 'Download IGV</a></td></tr></table>', "norm")
