from annotations import filters, gnomad
from annotations.record import Variant


class Filter:
    DATA_PATH = "/opt/data/"
    def __init__(self, data_dir = None):
        if (not data_dir):
            data_dir = Filter.DATA_PATH
        self.hgmd_filter = filters.Filter_HGMD(data_dir)
        self.clinvar_filter = filters.Filter_ClinVar(data_dir)
        self.gnomad_filter1 = filters.Filter_gnomAD_AF_local(0.01)
        self.gnomad_filter5 = filters.Filter_gnomAD_AF_local(0.05)

    def accept(self, vcf_record, info = dict()):
        ok = False
        if (self.hgmd_filter.accept(vcf_record)):
            ok = True
            info['HGMD'] = True
        else:
            info['HGMD'] = False

        if (self.clinvar_filter.accept(vcf_record)):
            ok = True
            info['ClinVar'] = True
        else:
            info['ClinVar'] = False

        if (ok):
            ok = self.gnomad_filter5.accept(vcf_record)
            info['gnomAD(5%)'] = ok
        else:
            ok = self.gnomad_filter1.accept(vcf_record)
            info['gnomAD(1%)'] = ok

        return ok



def process_file(f, out = None, vcf_header = None):
    n = 0
    n_accepted = 0
    n1 = 0
    n2 = 0
    cube = dict()
    KEYs = ['HGMD only', 'ClinVar only', 'HGMD & ClinVar', 'gnomAD: AF<1%', 'Singleton']

    clinical_filter = Filter()

    with open(f) as input:
        while(True):
            line = input.readline()
            if (not line):
                break
            v = Variant(line, vcf_header=vcf_header)
            n += 1
            info = {}
            if (not clinical_filter.accept(v, info)):
                continue
            n_accepted += 1
            if (v.get_gnomad_af()):
                n1 += 1
                if (info['HGMD'] and info['ClinVar']):
                    key = 'HGMD & ClinVar'
                elif (info['HGMD']):
                    key = 'HGMD only'
                elif (info['ClinVar']):
                    key = 'ClinVar only'
                elif (info['gnomAD(1%)']):
                    key = 'gnomAD: AF<1%'
                else:
                    key = "UNKNOWN"
            else:
                rows = gnomad.get_data(v.chr_num(), v.start())
                if (rows):
                    pass
                key = 'Singleton'
                if (info['HGMD']):
                    key = "{} & HGMD".format(key)
                if (info['ClinVar']):
                    key = "{} & ClinVar".format(key)

            if (info['ClinVar']):
                v.data["ClinVar"] = ""

            if (info['HGMD']):
                v.data["HGMD"] = ""

            if (not key in KEYs):
                KEYs.append(key)

            msq = v.get_msq()

            f = cube.get((msq, key),0)
            cube[(msq, key)] = f + 1

            out.write(v.get_view_json() + '\n')

            # if (msq in ["frameshift_variant", "missense_variant"] and key == 'Singleton'):
            #     print "{}: {}, {}:{}".format(v.get('id'), msq, v.get("seq_region_name"), v.get('start'))


    print "{}: {}/{}/{}".format(n, n_accepted, n1, n2)

    format = "{:40} "
    for key in KEYs:
        format = format + " {:>16}"
    print format.format("", *KEYs)
    for csq in Variant.consequences:
        values = [cube.get((csq, k)) for k in KEYs]
        print format.format(csq, *values)



if __name__ == '__main__':
    ##process_file("/Users/misha/projects/bgm/cases/BGM9001/tmp/f1.json")
    with open ("/Users/misha/projects/bgm/cases/BGM9001/header.vcf") as vcf:
        header = vcf.read()

    with open ("/Users/misha/projects/bgm/cases/BGM9001/bgm9001_wgs_final.json", "w") as output:
        process_file("/Users/misha/projects/bgm/cases/BGM9001/bgm9001_wgs_xbrowse.vep.filtered.vep.json", out=output, vcf_header=header)
