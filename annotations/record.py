import json
from StringIO import StringIO

import vcf

from annotations import liftover


def link_to_pmid(pmid):
    return "https://www.ncbi.nlm.nih.gov/pubmed/{}".format(pmid)


def vstr(c, s, e):
    if (s == e):
        strng = "{}:{}".format(c, s)
    else:
        strng = "{}:{}-{}".format(c, s, e)
    return strng


proteins_3_to_1 = {
 "Ala":"A",
 "Arg":"R",
 "Asn":"N",
 "Asp":"D",
 "Cys":"C",
 "Gln":"Q",
 "Glu":"E",
 "Gly":"G",
 "His":"H",
 "Ile":"I",
 "Leu":"L",
 "Lys":"K",
 "Met":"M",
 "Phe":"F",
 "Pro":"P",
 "Ser":"S",
 "Thr":"T",
 "Trp":"W",
 "Tyr":"Y",
 "Val":"V",
}

trusted_submitters = {
    #"lmm": "Laboratory for Molecular Medicine,Laboratory for Molecular Medicine (Partners HealthCare Personalized Medicine)",
    "lmm": "Laboratory for Molecular Medicine,Partners HealthCare Personalized Medicine",
    "gene_dx": "GeneDx"
}


def unique(lst, replace_None=None):
    if (not lst):
        return lst
    s = set()
    for element in lst:
        if (isinstance(element, list)):
            s.update(element)
        else:
            s.add(element)
    if (replace_None == None):
        s.discard(None)
    elif None in s:
        s.discard(None)
        s.add(replace_None)

    return list(s)


def convert_p(x):
    protein1 = []
    pos = []
    protein2 = []
    state = 0
    for c in x:
        if (state == 0):
            if (c.isalpha()):
                protein1.append(c)
                continue
            state = 2
        if (state == 2):
            if (c.isdigit()):
                pos.append(c)
                continue
            state = 3
        if (state == 3):
            protein2.append(c)
        else:
            break

    p1 = ''.join(protein1)
    p2 = ''.join(protein2)
    pos = ''.join(pos)
    protein1 = proteins_3_to_1.get(p1, p1)
    protein2 = proteins_3_to_1.get(p2, p2)
    x = "{}{}{}".format(protein1, pos, protein2)
    return x


def hgvcs_pos(str, type, with_pattern = True):
    pattern = ":{}.".format(type)
    if (not pattern in str):
        return None
    x = str.split(pattern)[1]
    if (type == 'p'):
        x = convert_p(x)

    if (with_pattern):
        return "{}{}".format(pattern[1:], x)
    return x

def get_from_transcripts(transcripts, key, source):
    return unique([t.get(key) for t in transcripts if (t.get("source") == source)])

hgvs_signs = ['-', '+', '*']
def get_distance_hgvsc(hgvsc):
    coord = hgvsc.split(':')[1]
    xx = coord.split('.')
    d = None
    try:
        for x in xx[1].split('_'):
            sign = None
            p1 = None
            p2 = None
            while (not x[0].isdigit() and not x[0] in hgvs_signs):
                x = x[1:]
            end = len(x)
            for i in range(0, end):
                c = x[i]
                if (c.isdigit()):
                    continue
                if (c in hgvs_signs):
                    p0 = 0 if (sign == None) else sign + 1
                    p1 = int(x[p0:i]) if i>p0 else 0
                    sign = i
                if (c.isalpha()):
                    end = i
                    break
            if (p1 != None and sign != None):
                p2 = int(x[sign + 1:end])
            if (p2):
                if (not d or d > p2):
                    d = p2
    except Exception as e:
        print e
        d = None
    return d

## TO-DO:
## Remove CALLED_BY and CMPD-HET
## Beside Worst Annotation add canonical annotation
## cPos: break into worst/canonical/rest
## gnomAD AF: CLCNKB, 0.003*??
## Move pLI to gnomAD
## No popmax?
## Explore SPlicing, add MaxEntTool
## HGMD put "NO"
## Add LoFTool

class DBConnectors:
    def __init__(self, array):
        if not array:
            array = dict()
        self.gnomAD = array.get("gnomAD")
        self.hgmd = array.get("hgmd")
        self.clinvar = array.get("clinvar")
        self.liftover = array.get("liftover")
        self.beacon = array.get("beacon")

class Variant:
    csq_damaging = [
        'transcript_ablation',
        'splice_acceptor_variant',
        'splice_donor_variant',
        'stop_gained',
        "frameshift_variant",
        'stop_lost',
        'start_lost',
        "transcript_amplification",
        "inframe_insertion",
        "inframe_deletion"
    ]
    csq_missense = [
        "missense_variant"
    ]
    csq_benign1 = [
        "splice_region_variant",
        "synonymous_variant",
    ]
    csq_benign2 = [
        "5_prime_UTR_variant",
        "3_prime_UTR_variant",
        'non_coding_transcript_exon_variant',
        "non_coding_transcript_exon_variant",
        "intron_variant",
        'upstream_gene_variant',
        'downstream_gene_variant',
        'regulatory_region_variant'
    ]

    severity = [
        csq_damaging, csq_missense, csq_benign1, csq_benign2
    ]

    consequences = []
    for c in severity:
        consequences += c

    callers = ['BGM_AUTO_DOM', 'BGM_DE_NOVO', 'BGM_HOM_REC', 'BGM_CMPD_HET',
                   'BGM_BAYES_DE_NOVO', 'BGM_BAYES_CMPD_HET', 'BGM_BAYES_HOM_REC',
                   'BGM_PIPELINE_A', 'BGM_PIPELINE', 'LMM', 'SANGER']


    @classmethod
    def most_severe(cls, csq):
        for i in range(0, len(cls.consequences)):
            if (cls.consequences[i] in csq):
                return cls.consequences[i]
        return None

    def __init__(self, json_string, vcf_header = None, case = None, samples = None, connectors = None):
        self.original_json = json_string
        self.data = json.loads(json_string)
        self.filters = dict()
        self.private_data = dict()
        self.case = case
        self.samples = samples
        self.hg38_start = None
        self.hg38_end = None
        self.alt_alleles = None
        self.connectors = DBConnectors(connectors)
        if (not vcf_header):
            vcf_header = "#"
        vcf_string = "{}\n{}\n".format(vcf_header, self.data.get("input"))
        if vcf_string:
            fsock = StringIO(vcf_string)
            vcf_reader = vcf.Reader(fsock)
            self.vcf_record = vcf_reader.next()
        else:
            self.vcf_record = None

        self.call_liftover()
        self.call_gnomAD()
        self.call_hgmd()
        self.call_clinvar()
        self.call_beacon()

        self.filters['min_gq'] = self.get_min_GQ()
        self.filters['proband_gq'] = self.get_proband_GQ()
        self.filters['severity'] = self.get_severity()
        self.filters['has_variant'] = list()

        proband = self.get_proband()
        mother = self.samples[proband]['mother']
        father = self.samples[proband]['father']
        for sample in self.samples:
            name = self.samples[sample]["name"]
            if (sample == proband):
                label = "proband [{}]".format(name)
            elif (sample == mother):
                label = "mother [{}]".format(name)
            elif (sample == father):
                label = "father [{}]".format(name)
            else:
                label = sample

            if (self.sample_has_variant(sample)):
                self.filters['has_variant'].append(label)


        d = self.get_distance_from_exon("worst", none_replacement=0)
        self.filters['dist_from_exon'] = min(d) if (len(d)> 0) else 0

    def call_liftover(self):
        connection = self.connectors.liftover
        if (not connection):
            return
        self.hg38_start = connection.hg38(self.chr_num(), self.start())
        self.hg38_end = connection.hg38(self.chr_num(), self.end())

    def call_beacon(self):
        connection = self.connectors.beacon
        if (not connection):
            return
        self.data["beacon"] = dict()
        beacon_names = []
        for alt in self.alt_list():
            beacons = connection.search_individually(pos=self.start() - 1,
                        chrom=self.chr_num(),
                        allele=alt,
                        referenceAllele=self.ref(),
                        ref="hg19")

            self.data["beacon"][alt] = [b for b in beacons if b.response]
            beacon_names += [b.get("name") for b in self.data["beacon"][alt]]
        self.data["beacon_names"] = unique(beacon_names)

    def call_gnomAD(self):
        gnomAD = self.connectors.gnomAD
        if (not gnomAD):
            return
        gm_af = None
        em_af = None
        _af = None
        gm_af_pb = None
        em_af_pb = None
        _af_pb = None

        popmax = None
        popmax_af = None
        popmax_an = None

        self.private_data["gnomad"] = dict()
        for alt in self.alt_list():
            gnomad_data = gnomAD.get_all(self.chr_num(), self.lowest_coord(), self.ref(), alt)
            if len(gnomad_data) == 0:
                continue
            self.private_data["gnomad"][alt] = gnomad_data

            if "exomes" in gnomad_data:
                af = gnomad_data["exomes"]["AF"]
                em_af = min(em_af, af) if em_af else af
                if (self.is_proband_has_allele(alt)):
                    em_af_pb = min(em_af_pb, af) if em_af_pb else af

            if "genomes" in gnomad_data:
                af = gnomad_data["genomes"]["AF"]
                gm_af = min(gm_af, af) if gm_af else af
                if (self.is_proband_has_allele(alt)):
                    gm_af_pb = min(gm_af_pb, af) if gm_af_pb else af

            af = gnomad_data["overall"]["AF"]
            if (self.is_proband_has_allele(alt)):
                _af_pb = min(_af_pb, af) if _af_pb else af

            if (af < _af or _af == None):
                _af = af
                popmax = gnomad_data.get("popmax")
                popmax_af = gnomad_data.get("popmax_af")
                popmax_an = gnomad_data.get("popmax_an")

        self.filters["gnomad_db_exomes_af"] = em_af
        self.filters["gnomad_db_genomes_af"] = gm_af
        self.filters['gnomad_af_fam'] = _af
        self.filters['gnomad_af_pb'] = _af_pb

        self.filters['gnomad_popmax'] = popmax
        self.filters['gnomad_popmax_af'] = popmax_af
        self.filters['gnomad_popmax_an'] = popmax_an

    def call_hgmd(self):
        connection = self.connectors.hgmd
        if (not connection):
            return
        accession_numbers = connection.get_acc_num(self.chr_num(), self.start(), self.end())
        if (len(accession_numbers) > 0):
            (phenotypes, pmids) = connection.get_data_for_accession_numbers(accession_numbers)
            self.private_data["HGMD_phenotypes"] = phenotypes
            self.private_data["HGMD_PIMIDs"] = pmids
            tags = [pmid[2] for pmid in pmids] if pmids else None
            self.private_data["HGMD_TAGs"] = tags
            self.data['HGMD'] = ','.join(accession_numbers)
            hg_38 = connection.get_hg38(accession_numbers)
            self.data['HGMD_HG38'] = ', '.join(["{}-{}".format(c[0],c[1]) for c in hg_38])
            self.filters["hgmd_benign"] = len([t for t in tags if t]) == 0 if tags else True

    def call_clinvar(self):
        connection = self.connectors.clinvar
        if (not connection):
            return
        if (self.is_snv()):
            rows = connection.get_data(self.chr_num(), self.start(), self.end(), self.alt_list())
        else:
            rows = connection.get_expanded_data(self.chr_num(), self.start())
        if (len(rows) == 0):
            return

        variants = [
            "{} {}>{}".format(vstr(self.chromosome(), row[0], row[1]), self.ref(), row[2])
            for row in rows
        ]
        significance = []
        submissions = dict()
        ids = dict()
        for row in rows:
            significance.extend(row[4].split('/'))
            id_list = [row[5].split(',') + row[7].split(',')  for row in rows]
            for id in id_list:
                if (not ':' in id):
                    continue
                x = id.split(':')
                if (not x[0] in ids):
                    ids[x[0]] = x[1]
                else:
                    ids[x[0]] = ids[x[0]].append(x[1])
            submissions.update(row[-1])

        self.data["ClinVar"] = "True"
        self.data["clinvar_variants"] = variants
        self.data["clinvar_phenotypes"] = [row[6] for row in rows]
        self.data["clinvar_significance"] = significance
        self.data["clinvar_submitters"] = submissions
        self.private_data["clinvar_other_ids"] = ids
        benign = True
        for prediction in significance:
            if not "benign" in prediction.lower():
                benign = False
                break
        self.filters["clinvar_benign"] = benign
        benign = None
        for submitter in trusted_submitters:
            full_name = trusted_submitters[submitter]
            if (full_name in submissions):
                prediction = submissions[full_name].lower()
                self.data[submitter] = prediction
                if not "benign" in prediction:
                    benign = False
                elif benign == None:
                    benign = True
        self.filters["clinvar_trusted_benign"] = benign


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
        return chr_str.upper()

    def start(self):
        return int(self.data.get("start"))

    def end(self):
        return int(self.data.get("end"))

    def lowest_coord(self):
        return min(self.start(), self.end())

    def highest_coord(self):
        return max(self.start(), self.end())

    def get_allele(self):
        return self.data.get("allele_string")

    def ref(self):
        return self.vcf_record.REF

    def ref1(self):
        s = self.data.get("allele_string")
        return s.split('/')[0]

    def alt_string(self):
        return ",".join(self.alt_list())

    def alt_list(self):
        if (self.alt_alleles == None):
            alleles = [str(s) for s in self.vcf_record.alleles]
            alt_allels = [s.sequence for s in self.vcf_record.ALT]
            counts = dict()
            #.gt_bases
            genotypes = {self.vcf_record.genotype(s) for s in self.samples}
            for g in genotypes:
                ad = g.data.AD if 'AD' in g.data._asdict() else None
                if (not ad):
                    self.alt_alleles = alt_allels
                    return self.alt_alleles
                for i in range(0, len(alleles)):
                    al = alleles[i]
                    n = ad[i]
                    counts[al] = counts.get(al, 0) + n

            self.alt_alleles = [a for a in alt_allels if counts.get(a) > 0]

        return self.alt_alleles

    def alt_list1(self):
        s = self.get_allele()
        return s.split('/')[1:]

    def info(self):
        if (self.vcf_record):
            return self.vcf_record.INFO
        return {}

    def __str__(self):
        str = self.get_hg19_coordinates()
        if (self.is_snv()):
            return "{}  {}>{}".format(str, self.ref(), self.alt_string())
        return "{} {}".format(str, self.get_variant_class())

    def get_msq(self):
        return self.data.get("most_severe_consequence")

    def is_snv(self):
        return self.get_variant_class() == "SNV"

    def get_variant_class(self):
        return self.data.get("variant_class")

    def get_transcripts(self, biotype = "protein_coding"):
        transcripts = self.data.get("transcript_consequences", [])
        if (biotype == None or biotype.upper() == "ALL"):
            return transcripts
        return [t for t in transcripts if t.get('biotype') == biotype]

    def get_colocated_variants(self):
        return self.data.get("colocated_variants", [])

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

    def get_max_ent(self):
        transcripts = self.get_transcripts()
        x = set()
        for transcript in transcripts:
            m1 = transcript.get("maxentscan_ref")
            m2 = transcript.get("maxentscan_alt")
            m3 = transcript.get("maxentscan_diff")
            if (m1 and m2 and m3):
                v = "{}={}-{}".format(m3, m1, m2)
                x.add(v)
        if (x):
            ret = []
            ret.extend(x)
            return ret
        else:
            return None

    def get_most_severe_transcripts(self):
        msq = self.get_msq()
        return [t for t in self.get_transcripts() if (msq in t.get("consequence_terms"))]

    def get_from_transcripts_list(self, key):
        return unique([t.get(key) for t in self.get_transcripts() if (t.has_key(key))])

    def get_from_transcripts_by_biotype(self, key, biotype):
        return unique([t.get(key) for t in self.get_transcripts(biotype=biotype) if (t.has_key(key))])

    def get_from_worst_transcript(self, key):
        return unique([t.get(key) for t in self.get_most_severe_transcripts() if (t.has_key(key))])

    def get_from_canonical_transcript(self, key):
        return unique([t.get(key) for t in self.get_canonical_transcripts() if (t.has_key(key))])

    def get_canonical_transcripts(self):
        return [t for t in self.get_transcripts() if (t.get("canonical"))]

    def get_genes(self):
        return unique(self.get_from_transcripts_list("gene_symbol"))

    def get_hgnc_ids(self):
        return unique(self.get_from_transcripts_list("hgnc_id"))

    def get_beacons(self):
        if not "beacon" in self.data:
            return None
        beacons = []
        for alt in self.alt_list():
            for beacon in self.data["beacon"][alt]:
                if (len(self.alt_list()) < 2):
                    allele = ""
                else:
                    allele = "{}: ".format(alt)
                label = "{}{}: {}".format(allele, beacon.get("organization", ""), beacon.get("name", ""))
                beacons.append(label)
        return beacons


    def get_tenwise_link(self):
        hgnc_ids = self.get_hgnc_ids()
        return ["https://www.tenwiseapps.nl/publicdl/variant_report/" +
            "HGNC_{}_variant_report.html".format(id)
            for id in hgnc_ids]

    def get_other_genes(self):
        genes = set(self.get_genes())
        all_genes = set(self.get_from_transcripts_by_biotype("gene_symbol", "all"))
        other_genes = all_genes - genes
        l = []
        l.extend(other_genes)
        return l

    def get_from_transcripts(self, key, type = "all"):
        if (type == "all"):
            v = self.get_from_transcripts_list(key)
        elif (type == "canonical"):
            v = self.get_from_canonical_transcript(key)
        elif (type == "worst"):
            v = self.get_from_worst_transcript(key)
        else:
            raise Exception("Unknown type: {}".format(type))
        return v

    def get_hgvs_list(self, type, kind):
        if (type == 'c'):
            hgvs_list = self.get_from_transcripts("hgvsc", kind)
        elif (type == 'p'):
            hgvs_list = self.get_from_transcripts("hgvsp", kind)
        else:
            hgvs_list = self.get_from_transcripts("hgvsc", kind) + self.get_from_transcripts("hgvsp", kind)
        return hgvs_list

    def get_pos(self, type, kind = "all"):
        pos_list = unique([hgvcs_pos(hgvcs, type) for hgvcs in self.get_hgvs_list(type, kind) if hgvcs])
        return pos_list

    def get_pos_tpl(self, type):
        c_worst = self.get_pos(type, "worst")
        c_canonical = self.get_pos(type, "canonical")
        ss = set()
        if (c_worst):
            ss.update(c_worst)
        if (c_canonical):
            ss.update(c_canonical)
        c_other = self.get_pos(type)
        if (c_other):
            ss = ss - set(c_other)
            c_other = [].extend(ss)
        return (c_worst, c_canonical, c_other)

    def get_distance_from_exon(self, kind, none_replacement = "Exonic"):
        return unique([get_distance_hgvsc(hgvcs) for hgvcs in self.get_hgvs_list('c', kind) if hgvcs],
                      replace_None=none_replacement)

    def get_gnomad_af(self):
        return self.filters.get('gnomad_af_fam')

    def get_gnomad_split_by_alt(self, what, exomes_or_genomes, alt):
        gnomad_data = self.private_data.get("gnomad")
        if (not gnomad_data):
            return None
        if not exomes_or_genomes:
            exomes_or_genomes = "overall"
        data = gnomad_data.get(alt)
        if (not data):
            return None
        if exomes_or_genomes in data:
            return data[exomes_or_genomes][what.upper()]
        return None

    def get_igv_url(self):
        if (not self.case or not self.samples):
            return None
        url = "http://localhost:60151/load?"
        path = "/anfisa/links/"
        host = "anfisa.forome.org"
        file_urls = [
            "http://{host}{path}{case}/{sample}.hg19.bam".format(host=host,path=path,case=self.case,sample=sample)
                     for sample in self.samples
        ]
        name = ",".join([sample["name"] for sample in self.samples.values()])
        args = "file={}&genome=hg19&merge=false&name={}&locus={}:{}-{}".\
            format(','.join(file_urls), name, self.chromosome(), self.start()-250, self.end()+250)
        return "{}{}".format(url, args)

    def get_label(self):
        try:
            genes = map(lambda g: str(g), self.get_genes())
            if (len(genes) == 0):
                gene = "None"
            elif (len(genes) < 3):
                gene = ",".join(genes)
            else:
                gene = "..."

            vstr = str(self)
        except:
            raise
        return "[{}] {}".format(gene, vstr)

    def get_hg38_coordinates(self):
        if (self.hg38_start == None or self.hg38_end == None):
            lo = liftover.Converter()
            c = self.chr_num()
            self.hg38_start = lo.hg38(c, self.start())
            self.hg38_end = lo.hg38(c, self.end())
        if (self.hg38_start == self.hg38_end):
            str = "{}:{}".format(self.chromosome(), self.hg38_start)
        else:
            str = "{}:{}-{}".format(self.chromosome(), self.hg38_start, self.hg38_end)
        return str

    def get_hg19_coordinates(self):
        return vstr(self.chromosome(), self.start(), self.end())

    def get_proband(self):
        if (not self.samples):
            return None
        for sample in self.samples.values():
            if (sample['id'].endswith('a1')):
                return sample['id']
        return None

    def get_color_code(self):
        pp = unique(self.get_from_transcripts_list("polyphen_prediction"))
        ss = unique(self.get_from_transcripts_list("sift_prediction"))
        best = None
        worst = None
        if (self.start() == 21238413):
            pass
        for p in pp:
            if ('benign' in  p):
                best = 'B'
            elif ('possibly_damaging' in p):
                if (worst <> 'D'):
                    worst = 'PD'
            elif ('damaging' in p):
                worst = 'D'
        for s in ss:
            if ('tolerated' in s):
                best = 'B'
            if ('deleterious' in s):
                worst = 'D'

        code = None
        if (best <> 'B' and worst == 'D'):
            code = 'red'
        elif (best == 'B' and not worst):
            code = 'green'
        elif (best or worst):
            code = 'yellow'

        if (code):
            return code

        csq = self.get_msq()
        if (csq in self.csq_damaging):
            code = 'red-cross'
        elif (csq in self.csq_missense):
            code = 'yellow-cross'

        return code

    def get_pLI(self):
        list = self.get_from_transcripts_list("exacpli")
        if (len(list) > 0):
            return list
        return None

    def get_severity(self):
        csq = self.get_msq()
        n = len(self.severity)
        for s in range(0,n):
            if (csq in self.severity[s]):
                return n - s - 1
        return None

    def get_pLI_by_allele(self, allele):
        transcripts = self.get_transcripts()
        key = "exacpli"
        list = unique([t.get(key) for t in transcripts if (t.has_key(key) and allele == t.get("variant_allele"))])
        if (len(list) > 0):
            return list
        return None

    @classmethod
    def get_from_genotype(cls, genotype, field):
        return genotype.data._asdict().get(field)

    def get_proband_GQ(self):
        return self.get_from_genotype(self.vcf_record.genotype(self.get_proband()), 'GQ')

    def get_min_GQ(self):
        GQ = None
        for s in self.samples:
            genotype = self.vcf_record.genotype(s)
            gq = self.get_from_genotype(genotype, 'GQ')
            if (gq):
                GQ = min(gq, GQ) if GQ else gq
        return GQ

    def sample_has_variant(self, sample=None):
        idx = None

        if (isinstance(sample, int)):
            idx = int(sample)
        elif (sample.lower() == "proband"):
            idx = 0
        elif (sample.lower() == "mother"):
            idx = 1
        elif (sample.lower() == "father"):
            idx = 2

        if (idx == None):
            genotype = self.vcf_record.genotype(sample).gt_bases
        else:
            genotypes = self.get_genotypes()
            if (len(genotypes) <= idx):
                return False
            genotype = genotypes[idx]

        if (not genotype):
            return False
        set1 = set(genotype.split('/'))
        set2 = set(self.alt_list())
        if (set1 & set2):
            return True
        return False

    def is_proband_has_allele(self, allele):
        genotype = self.get_genotypes()[0]
        if (not genotype):
            return False
        set1 = set(genotype.split('/'))
        return (allele in set1)

    def proband_sex(self):
        proband = self.get_proband()
        return self.samples[proband]['sex']


    def get_genotypes(self):
        proband = self.get_proband()
        proband_genotype = self.vcf_record.genotype(proband).gt_bases
        mother = self.samples[proband]['mother']
        if (mother == '0'):
            mother = None
        father = self.samples[proband]['father']
        if (father == '0'):
            father = None

        maternal_genotype = self.vcf_record.genotype(mother).gt_bases if mother else None
        paternal_genotype = self.vcf_record.genotype(father).gt_bases if father else None

        genotypes = {self.vcf_record.genotype(s).gt_bases for s in self.samples}
        other_genotypes = genotypes.difference({proband_genotype, maternal_genotype, paternal_genotype})

        return proband_genotype, maternal_genotype, paternal_genotype, other_genotypes

    def get_zygosity(self):
        genotype = self.get_genotypes()[0]
        if (not genotype):
            return None
        set1 = set(genotype.split('/'))
        if (self.chr_num() == 'X' and self.proband_sex() == 1):
            return "X-linked"
        if (len(set1) == 1):
            return "Homozygous"
        if (len(set1) == 2):
            return "Heterozygous"
        return "Unknown"

    def inherited_from(self):
        proband_genotype, maternal_genotype, paternal_genotype, other = self.get_genotypes()

        if (self.chr_num().upper() == 'X' and self.proband_sex() == 1):
            if (proband_genotype == maternal_genotype):
                return "Mother"
            else:
                return "Inconclusive"

        if (maternal_genotype == paternal_genotype):
            if (proband_genotype == maternal_genotype):
                return "Both parents"
            else:
                return "Both parents"
        if (proband_genotype == maternal_genotype):
            return "Mother"
        if (proband_genotype == paternal_genotype):
            return "Father"
        return "Inconclusive"

    def affected_alt_list(self):
        genotypes = {self.vcf_record.genotype(s).gt_bases for s in self.samples if self.samples[s]['affected']}
        alleles_affected = set()
        for g in genotypes:
            if (g):
                alleles_affected.update(g.split('/'))
        alleles_alt = set(self.alt_list())
        alt_set = alleles_affected & alleles_alt
        return [a for a in alt_set]

    def get_raw_callers(self):
        return [caller for caller in self.callers if (self.info().has_key(caller))]

    def get_callers(self):
        callers = self.get_raw_callers()

        # GATK callers
        proband_genotype, maternal_genotype, paternal_genotype, other = self.get_genotypes()
        if (not proband_genotype or not maternal_genotype or not paternal_genotype):
            return callers

        ref = self.ref()
        alt_set = set(self.alt_list())
        p_set = set(proband_genotype.split('/'))
        m_set = set(maternal_genotype.split('/'))
        f_set = set(paternal_genotype.split('/'))

        for alt in alt_set:
            if (alt in p_set and not (alt in (m_set | f_set))):
                callers.append('GATK_DE_NOVO')
                break

        if (len(p_set) == 1 and len(alt_set&p_set) > 0):
            if (len(m_set) == 2 and len(f_set) == 2 and len(alt_set&m_set) > 0 and len(alt_set&f_set) > 0):
                callers.append('GATK_HOMO_REC')

        if (len(p_set) == 1 and ref in p_set):
            if (len(m_set) == 2 and len(f_set) == 2 and ref in (m_set&f_set)):
                callers.append('GATK_HOMOZYGOUS')

        if (len(callers) == 0):
            inheritance = self.inherited_from()
            if (inheritance == "De-Novo"):
                raise Exception("Inconsistent inheritance")
            if (inheritance != "Inconclusive"):
                callers.append("INHERITED_FROM: {}".format(inheritance))

        return callers

    def get_intron_or_exon(self, kind):
        introns = self.get_from_transcripts("intron", kind)
        exons = self.get_from_transcripts("exon", kind)
        e = exons if len(exons) > 0 else introns
        if (not e):
            return None, None
        index = []
        total = []
        for x in e:
            if (not x):
                continue
            split = x.split('/')
            index.append(split[0])
            if (len(split) > 1):
                total.append(split[1])

        return ','.join(index), ','.join(total)

    def get_callers_data(self):
        callers = self.get_raw_callers()
        data = dict()
        for c in callers:
            v = self.info().get(c)
            if (v):
                data[c] = v
        return data

    def create_general_tab(self, data_info, view_info, filters):
        tab1 = dict()
        view_info["general"] = tab1
        tab1['genes'] = self.get_genes()
        tab1['hg19'] = str(self)
        tab1['hg38'] = self.get_hg38_coordinates()
        if (self.is_snv()):
            data_info["ref"] = self.ref()
            data_info["alt"] = self.alt_string()
        else:
            tab1["ref"] = self.ref()
            tab1["alt"] = self.alt_string()

        (c_worst,  c_canonical, c_other) = self.get_pos_tpl('c')
        tab1['cpos_worst'] = c_worst
        tab1['cpos_canonical'] = c_canonical
        tab1['cpos_other'] = c_other

        (c_worst,  c_canonical, c_other) = self.get_pos_tpl('p')
        tab1['ppos_worst'] = c_worst
        tab1['ppos_canonical'] = c_canonical
        tab1['ppos_other'] = c_other

        proband_genotype, maternal_genotype, paternal_genotype, other = self.get_genotypes()
        tab1['proband_genotype'] = proband_genotype
        tab1['maternal_genotype'] = maternal_genotype
        tab1['paternal_genotype'] = paternal_genotype

        tab1['worst_annotation'] = self.get_msq()
        consequence_terms = self.get_from_canonical_transcript("consequence_terms")
        canonical_annotation = self.most_severe(consequence_terms)
        if (len(consequence_terms) > 1):
            other_terms = list(set(consequence_terms) - {canonical_annotation})
            canonical_annotation = "{} [{}]".format(canonical_annotation, ', '.join(other_terms))
        tab1['canonical_annotation'] = canonical_annotation

        tab1["splice_region"] = self.get_from_transcripts("spliceregion")
        tab1["gene_splicer"] = self.get_from_transcripts("genesplicer")

        transcripts = self.get_most_severe_transcripts()
        tab1['refseq_transcript_worst'] = get_from_transcripts(transcripts, "transcript_id", source="RefSeq")
        tab1['ensembl_transcripts_worst'] = get_from_transcripts(transcripts, "transcript_id", source="Ensembl")

        transcripts = self.get_canonical_transcripts()
        tab1['refseq_transcript_canonical'] = get_from_transcripts(transcripts, "transcript_id", source="RefSeq")
        tab1['ensembl_transcripts_canonical'] = get_from_transcripts(transcripts, "transcript_id", source="Ensembl")

        tab1['variant_exon_worst'] = self.get_from_worst_transcript("exon")
        tab1['variant_intron_worst'] = self.get_from_worst_transcript("intron")
        tab1['variant_exon_canonical'] = self.get_from_canonical_transcript("exon")
        tab1['variant_intron_canonical'] = self.get_from_canonical_transcript("intron")

        data_info["variant_exon_intron_canonical"], data_info["total_exon_intron_canonical"] = self.get_intron_or_exon("canonical")
        data_info["variant_exon_intron_worst"], data_info["total_exon_intron_worst"] = self.get_intron_or_exon("worst")

        tab1["igv"] = self.get_igv_url()

    def create_quality_tab(self, data_info, view_info, filters):
        tab2 = list()
        view_info["quality_samples"] = tab2
        q_all = dict()
        q_all["title"] = "All"
        q_all['strand_odds_ratio'] = self.info().get("SOR")
        q_all['mq'] = self.info().get("MQ")
        q_all['variant_call_quality'] = self.vcf_record.QUAL

        q_all['qd'] = self.info().get("QD")
        q_all['fs'] = self.info().get("FS")
        filters['qd'] = self.info().get("QD")
        filters['fs'] = self.info().get("FS")
        tab2.append(q_all)

        proband = self.get_proband()
        mother = self.samples[proband]['mother']
        father = self.samples[proband]['father']
        for sample in self.samples:
            genotype = self.vcf_record.genotype(sample)
            s = self.samples[sample]["name"]
            q_s = dict()
            if (sample == proband):
                q_s["title"] = "Proband: %s" % s
            elif (sample == mother):
                q_s["title"] = "Mother: %s" % s
            elif (sample == father):
                q_s["title"] = "Father: %s" % s
            else:
                q_s["title"] = s

            q_s['allelic_depth'] = self.get_from_genotype(genotype, 'AD')
            q_s['read_depth'] = self.get_from_genotype(genotype, 'DP')
            q_s['genotype_quality'] = self.get_from_genotype(genotype, 'GQ')
            tab2.append(q_s)

    def create_gnomad_tab(self, data_info, view_info, filters):
        tab3 = list()
        view_info["gnomAD"] = tab3
        if (self.get_gnomad_af()):
            alt_list = self.alt_list()
            for allele in alt_list:
                gr = dict()
                tab3.append(gr)
                gr["allele"] = allele
                gr["proband"] = "Yes" if (self.is_proband_has_allele(allele)) else "No"
                gr["pli"] = self.get_pLI_by_allele(allele)

                gr["af"] = self.get_gnomad_split_by_alt("af", "overall", allele)
                gr["genome_af"] = self.get_gnomad_split_by_alt("af", "genomes", allele)
                gr["exome_af"] = self.get_gnomad_split_by_alt("af", "exomes", allele)
                gr["genome_an"] = self.get_gnomad_split_by_alt("AN", "genomes", allele)
                gr["exome_an"] = self.get_gnomad_split_by_alt("AN", "exomes", allele)
                gnomad_data = self.private_data["gnomad"].get(allele)
                if (gnomad_data):
                    pop_max = gnomad_data["popmax"]
                    pop_max_af = gnomad_data["popmax_af"]
                    pop_max_an = gnomad_data["popmax_an"]
                    gr["pop_max"] = "{}: {} [{}]".format(pop_max, pop_max_af, pop_max_an)

                    gr["url"] = gnomad_data["url"]


    def create_databases_tab(self, data_info, view_info, filters):
        tab4 = dict()
        view_info["databases"] = tab4
        genes = self.get_genes()
        clinvar_ids = self.private_data.get("clinvar_other_ids")
        omim_ids = None
        if (clinvar_ids):
            omim_ids = clinvar_ids.get("OMIM")

        if (omim_ids):
            omim_urls = ["https://www.omim.org/entry/{}".format(omim_id) for omim_id in omim_ids]
            data_info["omim_ids"] = omim_ids
        else:
            omim_urls = [
                "https://omim.org/search/?search=approved_gene_symbol:{}&retrieve=geneMap".format(gene) for gene in genes
            ]
        tab4["omim"] = omim_urls
        tab4['gene_cards'] = ["https://www.genecards.org/cgi-bin/carddisp.pl?gene={}".format(g) for g in genes]
        if (self.data.get("HGMD")):
            tab4["hgmd"] = self.data.get("HGMD")
            tab4["hgmd_hg38"] = self.data.get("HGMD_HG38")
        else:
            tab4["hgmd"] = "Not Present"
        pmids = self.private_data.get("HGMD_PIMIDs")
        tab4["hgmd_tags"] = self.private_data.get("HGMD_TAGs")
        tab4["hgmd_pmids"] = [link_to_pmid(pmid[1]) for pmid in pmids] if pmids else None
        data_info["hgmd_pmids"] = [pmid[1]for pmid in pmids] if pmids else None
        phenotypes = self.private_data.get("HGMD_phenotypes")
        tab4["hgmd_phenotypes"] = [p[0] for p in phenotypes] if phenotypes else None

        if (self.data.get("ClinVar") <> None):
            tab4["clinVar"] = "https://www.ncbi.nlm.nih.gov/clinvar/?term={}[chr]+AND+{}%3A{}[chrpos37]".\
                format(self.chr_num(), self.start(), self.end())
        tab4['clinVar_variants'] = unique(self.data.get("clinvar_variants"))
        tab4['clinVar_significance'] = unique(self.data.get("clinvar_significance"))
        tab4['clinVar_phenotypes'] = unique(self.data.get("clinvar_phenotypes"))
        tab4['clinVar_submitters'] = unique([
                "{}: {}".format(str(k),str(v)) for k,v in self.data["clinvar_submitters"].iteritems()
            ])  if "clinvar_submitters" in self.data else None
        for submitter in trusted_submitters:
            tab4["{}_significance".format(submitter)] = self.data.get(submitter)
        tab4["pubmed_search"] = self.get_tenwise_link()
        tab4["beacons"] = self.get_beacons()

    def create_predictions_tab(self, data_info, view_info, filters):
        tab5 = dict()
        #view['Predictions'] = tab5
        view_info["predictions"] = tab5
        lof_score = self.get_from_transcripts("loftool")
        lof_score.sort(reverse=True)
        tab5["lof_score"] = lof_score
        lof_score = self.get_from_canonical_transcript("loftool")
        lof_score.sort(reverse=True)
        tab5["lof_score_canonical"] = lof_score

        tab5["max_ent_scan"] = self.get_max_ent()

        tab5['polyphen'] = unique(self.get_from_transcripts_list("polyphen_prediction"))
        tab5['polyphen2_hvar'] = unique(self.get_from_transcripts_list("Polyphen2_HVAR_pred".lower()))
        tab5['polyphen2_hdiv'] = unique(self.get_from_transcripts_list("Polyphen2_HDIV_pred".lower()))
        tab5['polyphen2_hvar_score'] = unique(self.get_from_transcripts_list("Polyphen2_HVAR_score".lower()))
        tab5['polyphen2_hdiv_score'] = unique(self.get_from_transcripts_list("Polyphen2_HDIV_score".lower()))
        tab5['sift'] = unique(self.get_from_transcripts_list("sift_prediction"))
        tab5['sift_score'] = unique(self.get_from_transcripts_list("sift_score"))
        tab5["revel"] = unique(self.get_from_transcripts_list("revel_score"))
        tab5["mutation_taster"] = unique(self.get_from_transcripts_list("mutationtaster_pred"))
        tab5["fathmm"] = unique(self.get_from_transcripts_list("fathmm_pred"))
        tab5["cadd_phred"] = unique(self.get_from_transcripts_list("cadd_phred"))
        tab5["cadd_raw"] = unique(self.get_from_transcripts_list("cadd_raw"))
        tab5["mutation_assessor"] = unique(self.get_from_transcripts_list("mutationassessor_pred"))

    def create_bioinformatics_tab(self, data_info, view_info, filters):
        tab6 = dict()
        view_info["bioinformatics"] = tab6
        tab6["zygosity"] = self.get_zygosity()
        tab6["inherited_from"] = self.inherited_from()
        tab6["dist_from_exon_worst"] = self.get_distance_from_exon("worst")
        tab6["dist_from_exon_canonical"] = self.get_distance_from_exon("canonical")
        tab6["conservation"] = unique(self.get_from_transcripts_list("conservation"))
        tab6["species_with_variant"] = ""
        tab6["species_with_others"] = ""
        tab6["max_ent_scan"] = self.get_max_ent()
        tab6["nn_splice"] = ""
        tab6["human_splicing_finder"] = ""
        tab6["other_genes"] = self.get_other_genes()
        tab6['called_by'] = self.get_callers()
        tab6['caller_data'] = self.get_callers_data()


    def get_view_json(self):
        data_info = self.data.copy()
        view_info = dict()
        filters   = self.filters.copy()

        data_info['label'] = self.get_label()
        data_info['color_code'] = self.get_color_code()
        self.create_general_tab(data_info, view_info, filters)
        self.create_quality_tab(data_info, view_info, filters)
        self.create_gnomad_tab(data_info, view_info, filters)
        self.create_databases_tab(data_info, view_info, filters)
        self.create_predictions_tab(data_info, view_info, filters)
        self.create_bioinformatics_tab(data_info, view_info, filters)


        tab7 = dict()
        view_info["inheritance"] = tab7

        ret = {"data": data_info,
            "view": view_info, "_filters": filters}
        return json.dumps(ret)
