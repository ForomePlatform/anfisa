from app.view.attr import AttrH

#===============================================
def tuneAspects(dataset, aspects):
    if "meta" not in dataset.getDataInfo():
        return
    case = dataset.getDataInfo()["meta"].get("case")
    samples = dataset.getDataInfo()["meta"].get("samples")
    view_gen = aspects["view_gen"]
    igv_idx = view_gen.find("igv")
    if igv_idx >= 0:
        view_gen.delAttr(view_gen[igv_idx])
    view_gen.addAttr(IGV_AttrH(view_gen, case, samples), igv_idx)

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
        return ('<table><tr><td><span title="For this link to work, make sure that IGV is running on your computer">' +
            ('<a href="%s">View Variant in IGV</a>' % link) + ' </span></td>' +
            '<td><a href="https://software.broadinstitute.org/software/igv/download" target="_blank">' +
            'Download IGV</a></td></tr></table>', "norm")
