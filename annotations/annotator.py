import argparse
import os

from annotations import case_utils, liftover
from annotations.clinvar import ClinVar
from annotations.gnomad import GnomAD
from annotations.hgmd import HGMD
from annotations.record import Variant


def process_file(f, out = None, vcf_header = None, samples = None, case = None, limit = None):
    n = 0
    hg19_to_38_converter = liftover.Converter()

    with open(f) as input, open(out, "w") as out1, HGMD() as hgmd, \
                    GnomAD() as gnomAD,  \
                    ClinVar("anfisa.forome.org:ip-172-31-24-96:MishaMBP4.local") as clinvar:
        while(True):
            line = input.readline()
            if (not line):
                break
            cns = {
                "hgmd": hgmd,
                "gnomAD": gnomAD,
                "liftover": hg19_to_38_converter,
                "clinvar": clinvar
            }
            v = Variant(line, vcf_header=vcf_header, samples=samples, case = case, connectors=cns)
            n += 1
            if (n%100 == 0):
                print n

            out1.write(v.get_view_json() + '\n')

            if (limit and n >= limit):
                break
            # if (msq in ["frameshift_variant", "missense_variant"] and key == 'Singleton'):
            #     print "{}: {}, {}:{}".format(v.get('id'), msq, v.get("seq_region_name"), v.get('start'))

    print "Variants processed: {}".format(n)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Annotate VCF file with VEP and output results as JSON")
    parser.add_argument("-i", "--input", dest = "input", help="Input JSON file, with VEP annotations")
    parser.add_argument("-o", "--output", dest="output", help="Output file")
    parser.add_argument("-c", "--case", dest="case", help="Case name, default is determined from directory name")
    parser.add_argument("-d", "--dir", dest="dir", help="Work directory", default=os.getcwd())
    parser.add_argument("-l", "--limit", dest="limit", type=int, help="Maximum number of variants top process")
    parser.add_argument("--header", help="VCF Header file", default="header.vcf")

    args = parser.parse_args()
    print args

    header_file = args.header
    dir =  args.dir

    case = args.case if args.case else os.path.basename(dir).split('_')[0]

    fam_file = "{}.fam".format(case)
    filtered_by_bed_vep_output = args.input if args.input else "{}_wgs_xbrowse.vep.filtered.vep.json".format(case)
    limit = args.limit
    print "limit = {}".format(limit)
    print "file: {}".format(filtered_by_bed_vep_output)

    ##process_file("/Users/misha/projects/bgm/cases/bgm9001/tmp/f1.json")
    if (header_file == "header.vcf" and not os.path.exists(header_file)):
        if (filtered_by_bed_vep_output.endswith("vep.json")):
            f = filtered_by_bed_vep_output.split('.')
            ff = f[:-2] + ["vcf"]
            header_file = '.'.join(ff)
        with open (header_file) as vcf:
            header = ''.join([h for h in vcf if h.startswith('#')])
    else:
        with open (header_file) as vcf:
            header = vcf.read()

    samples = case_utils.parse_fam_file(fam_file)

    output = args.output if args.output else "{}/{}_anfisa.json".format(dir, case)

    process_file(filtered_by_bed_vep_output, out=output,
                     vcf_header=header, samples=samples, case="{}_wgs".format(case), limit =limit)
