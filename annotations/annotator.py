import argparse
import json
import os
import time

from annotations import case_utils, liftover
from annotations.clinvar import ClinVar
from annotations.gnomad import GnomAD
from annotations.spliceai import SpliceAI
from annotations.gtf import GTF
from annotations.hgmd import HGMD
from annotations.record import Variant
from beacons.beacon import Beacon

VEP_HOME = "/db/vep-93/ensembl-vep/"
DB_HOME = "/db/data"
TMP = "/data/tmp"

sample_command = "{vep_home}/vep" \
                 " --cache --merged --dir_cache {db_home}/vep/cache --dir {db_home}/vep/cache --port 3337 " \
                 "--force_overwrite --everything --json -i {input} -o {output} " \
                 "--plugin dbNSFP,{db_home}/dbNSFPa/dbNSFP_hg19.gz,Polyphen2_HDIV_pred,Polyphen2_HVAR_pred,Polyphen2_HDIV_score,Polyphen2_HVAR_score,SIFT_pred,SIFT_score,MutationTaster_pred,MutationTaster_score,FATHMM_pred,FATHMM_score,REVEL_score,CADD_phred,CADD_raw,MutationAssessor_score,MutationAssessor_pred,clinvar_rs,clinvar_clnsig " \
                 "--plugin Conservation " \
                 "--plugin ExACpLI,{db_home}/misc/ExACpLI_values.txt " \
                 "--plugin MaxEntScan,{db_home}/MaxEntScan/fordownload " \
                 "--plugin LoFtool,{db_home}/loftoll/LoFtool_scores.txt  " \
                 "--plugin SpliceRegion " \
                 "--plugin GeneSplicer,{db_home}/GeneSplicer/bin/linux/genesplicer,{db_home}/GeneSplicer/human,context=200,tmpdir={tmp} " \
                 "--fasta {db_home}/vep/cache/homo_sapiens/93_GRCh37/Homo_sapiens.GRCh37.75.dna.primary_assembly.fa.gz " \
                 "--buffer_size 50000 " \
                 "--fork {fork}"


def execute_vep(input, output = None, fork = 8):
    if (not output):
        x = input.split('.')
        if (x[-1].lower() == 'vcf'):
            x = x[:-1]
        x.append("vep")
        x.append("json")
        output = '.'.join(x)
    t0 = time.time()
    cmd_string = sample_command.format(vep_home=VEP_HOME, db_home=DB_HOME, input=input, output=output, tmp=TMP, fork=fork)
    print cmd_string
    os.system(cmd_string)
    print "VEP has completed annotation. Duration: {} s.".format(time.time() - t0)
    return output


def annotate_json(f, out = None, vcf_header = None, samples = None, case = None, limit = None, start = 1):
    n_out = limit / 20 if limit > 0 else 100
    if (not n_out):
        n_out = 1
    n = 0
    l = 0
    hg19_to_38_converter = liftover.Converter()
    beacon = None ## Beacon(resJson=False)
    with open(f) as input, open(out, "w") as out1, HGMD() as hgmd, \
                    GnomAD() as gnomAD,  \
                    GTF() as gtf, \
                    SpliceAI() as spliceAI, \
                    ClinVar() as clinvar:
        cns = {
            "hgmd": hgmd,
            "gnomAD": gnomAD,
            "spliceAI": spliceAI,
            "liftover": hg19_to_38_converter,
            "clinvar": clinvar,
            "gtf": gtf.prepare_lookup(transcript=True),
            "beacon": beacon
        }
        metadata = Variant.get_metadata(vcf_header=vcf_header, samples=samples, case = case)
        print metadata["versions"]
        out1.write(json.dumps(metadata) + '\n')
        while(True):
            line = input.readline()
            if (not line):
                break
            l += 1
            if (l < start):
                continue
            try:
                v = Variant(line, vcf_header=vcf_header, samples=samples, case = case, connectors=cns)
            except:
                print "Line = {}".format(l)
                raise
            n += 1
            if (n%n_out == 0):
                print n

            out1.write(v.get_view_json() + '\n')

            if (limit and n >= limit):
                break
            # if (msq in ["frameshift_variant", "missense_variant"] and key == 'Singleton'):
            #     print "{}: {}, {}:{}".format(v.get('id'), msq, v.get("seq_region_name"), v.get('start'))

    print "Variants processed: {}".format(n)


def output_raw_calls(infile, outfile, limit = None, start = 1):
    n_out = limit / 20 if limit > 0 else 100
    n = 0
    l = 0
    result = list()
    with open(infile) as source, open(outfile, "w") as destination:
        while(True):
            line = source.readline()
            if (not line):
                break
            l += 1
            if (l < start):
                continue
            v = Variant(line)
            n += 1
            if (n%n_out == 0):
                print n

            alleles = v.alt_list()
            for allele in alleles:
                variant = dict()
                variant["chromosome"] = v.chr_num()
                variant["position"]   = v.start()
                variant["reference"]  = v.ref()
                variant["alternative"] = allele
                result.append(variant)
        json.dump(result, destination)
    print "Variants processed: {}".format(n)


def get_md(f):
    with open(f) as source:
        while(True):
            line = source.readline()
            if (not line):
                break
            data = json.loads(line)
            if (not "record_type" in data):
                return None
            if (data["record_type"] == "metadata"):
                return data
    return None

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Annotate VCF file with VEP and output results as JSON")
    parser.add_argument("-i", "--input", dest = "input", help="Input JSON file, with VEP annotations")
    parser.add_argument("-o", "--output", dest="output", help="Output file")
    parser.add_argument("--vep", action='store_true', help="Annotate with VEP first")
    parser.add_argument("--raw", action='store_true', help="Do not annotate, just output raw calls")
    parser.add_argument("-c", "--case", dest="case", help="Case name, default is determined from directory name")
    parser.add_argument("-d", "--dir", dest="dir", help="Work directory", default=os.getcwd())
    parser.add_argument("-l", "--limit", dest="limit", type=int, help="Maximum number of variants to process")
    parser.add_argument("-s", "--start", dest="start", type=int, help="Start position: first variant to process", default=1)
    parser.add_argument("--header", help="VCF Header file", default="header.vcf")
    parser.add_argument("--fork", help="Number of parallel processes", default=16, type=int)
    parser.add_argument("--force", help="Force re-annotation even if the same version", action='store_true')

    args = parser.parse_args()
    print args

    header_file = args.header
    dir =  args.dir

    case = args.case if args.case else os.path.basename(dir).split('_')[0]

    platform = None
    if (args.input):
        x = args.input.lower().split('_')
        if ('wgs' in x):
            platform = 'wgs'
        elif ('wes'in x):
            platform = 'wes'
    if (platform):
        print "Platform: {}".format(platform)
    else:
        platform = "wgs"
        print "Could not determine platform (WES or WGS), assuming: ".format(platform)
    case_id = "{}_{}".format(case, platform)
    fam_file = "{}.fam".format(case)
    if (args.vep):
        filtered_by_bed_vep_input = args.input if args.input else "{}_xbrowse.vep.filtered.vcf".format(case_id)
        filtered_by_bed_vep_output = execute_vep(filtered_by_bed_vep_input, None, args.fork)
    else:
        filtered_by_bed_vep_output = args.input if args.input else "{}_xbrowse.vep.filtered.vep.json".format(case_id)
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
    if (args.raw):
        output_raw_calls(filtered_by_bed_vep_output, outfile=output, limit=limit, start=args.start)
        exit(0)

    if (not args.force and os.path.exists(output)):
        metadata = get_md(output)
        if (metadata):
            version = Variant.get_version()
            old_version = metadata["versions"]["annotations"]
            if (old_version == version):
                print "Case is already annotated with the same version"
                exit(0)

    annotate_json(filtered_by_bed_vep_output, out=output,
                  vcf_header=header, samples=samples, case=case_id, limit=limit, start=args.start)
