import argparse
import json
import sys
import time

from annotations import liftover
from annotations.clinvar import ClinVar
from annotations.gnomad import GnomAD
from annotations.gtf import GTF
from annotations.hgmd import HGMD
from annotations.record import Variant
from annotations.vep_rest_client import EnsemblRestClient

available_connectors = [
    'hgmd',
    "gnomAD",
    "clinvar",
    "beacon",
    "liftover",
    "gtf"
]

class Annotator:
    def __init__(self, connectors):
        self.connectors = dict()
        lcc = {c.lower():c for c in available_connectors}
        for connector in [c.lower() for c in connectors]:
            if (connector == 'hgmd'):
                c = HGMD()
            elif (connector == 'gnomad'):
                c = GnomAD()
            elif (connector == 'clinvar'):
                c = ClinVar()
            elif (connector == 'beacon'):
                c = None
            elif (connector == 'liftover'):
                c = liftover.Converter()
            elif (connector == 'gtf'):
                c = GTF()
            else:
                raise Exception("Unknown Connector: {}".format(connector))
            self.connectors[lcc[connector]] = c

    def close(self):
        for connector in self.connectors.values():
            if (connector):
                connector.close()

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

    def __enter__(self):
        return self

    def get_anfisa_json(self, chromosome, start, end, allele):
        region = "{}:{}:{}".format(chromosome, start, end)
        client = EnsemblRestClient()
        variants = client.get_consequences(region, allele)

        if (not variants or len(variants) == 0):
            return None

        records = [Variant(v, connectors=self.connectors).get_view_json() for v in variants]

        return records

    def get_gnomad(self, chromosome, start, ref, alt):
        data = dict()
        data["input"] = (chromosome, start, ref, alt)
        data["gnomAD"] = self.connectors["gnomAD"].get_all(chr=chromosome, pos=start, alt=alt, ref=ref)
        return [data]

    def gene_by_pos(self, chromosome, pos):
        data = dict()
        data["input"] = (chromosome, pos)
        data["gene"] = {
            "symbol": self.connectors["gtf"].get_gene(chromosome=chromosome, pos=pos)
        }
        return [data]


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Annotate variant(s) with VEP and output results as JSON")
    parser.add_argument(dest = "input", help="Variant specification", nargs="*")
    parser.add_argument("-a", "--annotations", default="anfisa", help="List of annotations to add")
    parser.add_argument("-i", "--input", dest = "file", help="Input JSON file, - for standard input")

    args = parser.parse_args()
    print args

    variants = None
    if (args.file):
        if (args.file == '-'):
            variants = json.load(sys.stdin)
        else:
            with open(args.file) as file:
                variants = json.load(file)
    else:
        if (len(args.input) > 0):
            arg = ' '.join(args.input).split(' ')
        else:
            arg = ["1:6484880:6484880", "A>G"]
        if (len(arg) != 2):
            raise Exception("Invalid variant specification. Use: c:start:end Ref>Alt")

        coords = arg[0].split(':')
        chromosome = coords[0]
        start = int(coords[1])
        if (len(coords) > 2):
            end = int(coords[2])
        else:
            end = start
        change = arg[1].split('>')
        ref = change[0]
        alt = change[1]

        variant = dict()
        variant["chromosome"] = chromosome
        variant["position"] = start
        variant["end"] = end
        variant["reference"] = ref
        variant["alternative"] = alt
        variants = [variant]

    if (args.annotations == "anfisa"):
        connectors = available_connectors
    elif (args.annotations == 'gnomad'):
        connectors = ["gnomAD"]
    elif (args.annotations == 'gene'):
        connectors = ["gtf"]
    else:
        raise Exception("Unsupported Annotation: {}".format(args.annotations))

    with Annotator(connectors) as a:
        t0 = time.time()
        for variant in variants:
            if (args.annotations == "anfisa"):
                data = a.get_anfisa_json(variant["chromosome"], variant["position"], variant["end"], variant["alternative"])
            elif (args.annotations == 'gnomad'):
                data = a.get_gnomad(variant["chromosome"], variant["position"], variant["reference"], variant["alternative"])
            elif (args.annotations == 'gene'):
                data = a.gene_by_pos(variant["chromosome"], variant["position"])
            else:
                data = None

            if data:
                for v in data:
                    print json.dumps(json.loads(v), sort_keys=True, indent=4)

        t1 = time.time()
        print (t1 - t0)

