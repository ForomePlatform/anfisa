import json
from StringIO import StringIO

import vcf


class Variant:
    consequences = [
        "frameshift_variant",
        "inframe_insertion",
        "inframe_deletion",
        "missense_variant",
        "splice_region_variant",
        "synonymous_variant",
        "5_prime_UTR_variant",
        "3_prime_UTR_variant",
        "non_coding_transcript_exon_variant",
        "intron_variant"
    ]

    def __init__(self, json_string, vcf_header = None):
        self.data = json.loads(json_string)
        if (not vcf_header):
            vcf_header = "#"
        vcf_string = "{}\n{}\n".format(vcf_header, self.data.get("input"))
        if vcf_string:
            fsock = StringIO(vcf_string)
            vcf_reader = vcf.Reader(fsock)
            self.vcf_record = vcf_reader.next()
        else:
            self.vcf_record = None


    def same(self,c, p1, p2 = None):
        if (p2 == None):
            p2 = p1
        if (c == self.chr_num() and p1 == self.start() and p2 == self.end()):
            return True
        return False

    def key(self):
        return (self.chr_num(), self.start(), self.end())

    def rs_id(self):
        return self.data.get("id")

    def chromosome(self):
        return self.data.get("seq_region_name")

    def chr_num(self):
        chr_str = self.chromosome()
        if (chr_str.startswith('chr')):
            return chr_str[3:]
    
    def start(self):
        return self.data.get("start")

    def end(self):
        return self.data.get("end")

    def get_allele(self):
        return self.data.get("allele_string")

    def ref(self):
        s = self.data.get("allele_string")
        return s.split('/')[0]

    def alt_string(self):
        return ",".join(self.alt_list())

    def alt_list(self):
        s = self.get_allele()
        return s.split('/')[1:]

    def info(self):
        if (self.vcf_record):
            return self.vcf_record.INFO
        return {}

    def __str__(self):
        return "{}:{}  {}>{}".format(self.chromosome(), self.start(),self.ref(), self.alt_string())
    
    def get_msq(self):
        return self.data.get("most_severe_consequence")

    def get_transcripts(self):
        return self.data.get("transcript_consequences", [])

    def get_colocated_variants(self):
        return self.data.get("colocated_variants", [])

    def get_from_transcripts_list(self, key):
        return [t.get(key) for t in self.get_transcripts() if (t.has_key(key))]

    def get_from_transcript_consensus(self, key):
        value = None
        transcripts = self.get_transcripts()
        for transcript in transcripts:
            v = transcript.get(key)
            if (not v):
                continue
            if (not value):
                value = v
            if (v <> value):
                raise Exception("Inconsistent values for {} in transcripts: {} != {} in self.data {}".
                                format(key, value, v, str(self)))
            return value
    
    def get_most_severe_transcripts(self):
        msq = self.get_msq()
        return [t for t in self.get_transcripts() if (msq in t.get("consequence_terms"))]

    def get_canonical_transcripts(self):
        return [t for t in self.get_transcripts() if (t.get("canonical"))]

    def get_genes(self):
        return self.get_from_transcripts_list("gene_symbol")

    def get_gnomad_af(self):
        gm_af = None
        alt_alleles = set(self.alt_list())
        collocated_variants = self.get_colocated_variants()
        for v in collocated_variants:
            alts = set(v.get("allele_string").split('/')[1:])
            if (not alts.intersection(alt_alleles)):
                continue
            if (v.get("somatic")):
                continue
            af = v.get("gnomad_maf")
            if (af == None):
                af = v.get("minor_allele_freq")
            if (af == None):
                continue
            if (gm_af):
                gm_af = min(gm_af, af)
            else:
                gm_af = af

        if (gm_af):
            return gm_af

        transcripts = self.get_transcripts()
        for t in transcripts:
            af_e = t.get("gnomad_exomes_af")
            af_g = t.get("gnomad_genomes_af")
            if (af_g <> None and af_e <> None):
                af = min(af_g, af_e)
            elif (af_e <> None):
                af = af_e
            elif (af_g <> None):
                af = af_g
            else:
                continue

            if (gm_af):
                gm_af = min(gm_af, af)
            else:
                gm_af = af


        return gm_af
