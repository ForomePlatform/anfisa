import json
from StringIO import StringIO

import vcf

from annotations import liftover


def link_to_pmid(pmid):
    return "https://www.ncbi.nlm.nih.gov/pubmed/{}".format(pmid)


def unique(lst):
    s = set()
    for element in lst:
        if (isinstance(element, list)):
            s.update(element)
        else:
            s.add(element)
    s.discard(None)
    list2 = []
    list2.extend(s)
    return list2

def hgvcs_pos(str, type, with_pattern = True):
    pattern = ":{}.".format(type)
    if (not pattern in str):
        return None
    x = str.split(pattern)[1]
    if (type == 'p'):
        x1 = []
        x2 = []
        x3 = []
        state = 0
        for c in x:
            if (state == 0):
                x1.append(c)
                state = 1
                continue
            elif (state == 1):
                if (c.isalpha()):
                    continue
                state = 2
            if (state == 2):
                if (c.isdigit()):
                    x2.append(c)
                    continue
                state = 3
            if (state == 3):
                x3.append(c)
                state = 4
            else:
                break
        x = ''.join(x1 + x2 + x3)

    if (with_pattern):
        return "{}{}".format(pattern[1:], x)
    return x

def get_from_transcripts(transcripts, key, source):
    return unique([t.get(key) for t in transcripts if (t.get("source") == source)])

def get_distance_hgvsc(hgvsc):
    coord = hgvsc.split(':')[1]
    xx = coord.split('.')
    t = xx[0]
    d = None
    for x in xx[1].split('_'):
        sign = None
        p1 = None
        p2 = None
        while (not x[0].isdigit()):
            x = x[1:]
        end = len(x)
        for i in range(0, end):
            c = x[i]
            if (c.isdigit()):
                continue
            if (c in ['-', '+']):
                p1 = int(x[0:i])
                sign = i
            if (c.isalpha()):
                end = i
                break
        if (p1 and sign):
            p2 = int(x[sign + 1:end])
        if (p2):
            if (not d or d > p2):
                d = p2
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

    consequences = sum(severity)

    @classmethod
    def most_severe(cls, csq):
        for i in range(0, len(cls.consequences)):
            if (cls.consequences[i] in csq):
                return cls.consequences[i]
        return None

    def __init__(self, json_string, vcf_header = None, case = None, samples = None, gnomAD_connection = None,
                 HGMD_connector = None):
        self.original_json = json_string
        self.data = json.loads(json_string)
        self.case = case
        self.samples = samples
        self.hg38_start = None
        self.hg38_end = None
        if (not vcf_header):
            vcf_header = "#"
        vcf_string = "{}\n{}\n".format(vcf_header, self.data.get("input"))
        if vcf_string:
            fsock = StringIO(vcf_string)
            vcf_reader = vcf.Reader(fsock)
            self.vcf_record = vcf_reader.next()
        else:
            self.vcf_record = None
        if (gnomAD_connection):
            gm_af = None
            em_af = None
            for alt in self.alt_list():
                af = gnomAD_connection.get_af(self.chr_num(), self.lowest_coord(), self.ref(), alt, 'e')
                self.data["_private.gnomad_db_exomes_{}_af".format(alt)] = af
                if (self.is_proband_has_allele(alt)):
                    gm_af = min(gm_af, af) if gm_af else af
                af = gnomAD_connection.get_af(self.chr_num(), self.lowest_coord(), self.ref(), alt, 'g')
                self.data["_private.gnomad_db_genomes_{}_af".format(alt)] = af
                if (self.is_proband_has_allele(alt)):
                    em_af = min(em_af, af) if em_af else af

            self.data["_private.gnomad_db_exomes_af"] = em_af
            self.data["_private.gnomad_db_genomes_af"] = gm_af
            self.data['_filters.gnomaAD_AF'] = max(em_af, gm_af)

        if (HGMD_connector):
            accession_numbers = HGMD_connector.get_acc_num(self.chr_num(), self.start(), self.end())
            if (len(accession_numbers) > 0):
                (phenotypes, pmids) = HGMD_connector.get_data_for_accession_numbers(accession_numbers)
                self.data["_private.HGMD_phenotypes"] = phenotypes
                self.data["_private.HGMD_PIMIDs"] = pmids
                self.data['HGMD'] = ','.join(accession_numbers)
                hg_38 = HGMD_connector.get_hg38(accession_numbers)
                self.data['HGMD_HG38'] = ', '.join(["{}-{}".format(c[0],c[1]) for c in hg_38])

        self.data['_filters.Min_GQ'] = self.get_min_GQ()
        self.data['_filters.Proband_GQ'] = self.get_proband_GQ()
        self.data['_filters.Proband_has_Variant'] = self.is_proband_has_variant()
        self.data['_filters.Severity'] = self.get_severity()



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
        return int(self.data.get("start"))

    def end(self):
        return int(self.data.get("end"))

    def lowest_coord(self):
        return min(self.start(), self.end())

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
         return [s.sequence for s in self.vcf_record.ALT]

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
        return unique([t.get(key) for t in self.get_transcripts(biotype = biotype) if (t.has_key(key))])

    def get_from_worst_transcript(self, key):
        return unique([t.get(key) for t in self.get_most_severe_transcripts() if (t.has_key(key))])

    def get_from_canonical_transcript(self, key):
        return unique([t.get(key) for t in self.get_canonical_transcripts() if (t.has_key(key))])

    def get_canonical_transcripts(self):
        return [t for t in self.get_transcripts() if (t.get("canonical"))]

    def get_genes(self):
        return unique(self.get_from_transcripts_list("gene_symbol"))

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

    def get_hgvs_list(self, kind):
        if (kind == 'c'):
            hgvs_list = self.get_from_transcripts("hgvsc", kind)
        elif (kind == 'p'):
            hgvs_list = self.get_from_transcripts("hgvsp", kind)
        else:
            hgvs_list = self.get_from_transcripts("hgvsc", kind) + self.get_from_transcripts("hgvsp", kind)
        return hgvs_list

    def get_pos(self, type, kind = "all"):
        pos_list = unique([hgvcs_pos(hgvcs, type) for hgvcs in self.get_hgvs_list(kind) if hgvcs])
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

    def get_distance_from_exon(self, kind):
        return unique([get_distance_hgvsc(hgvcs) for hgvcs in self.get_hgvs_list(kind) if hgvcs])

    def get_gnomad_pop_max(self, allele = None):
        ancestries = dict()
        collocated_variants = self.get_colocated_variants()
        for v in collocated_variants:
            if (v.get("somatic")):
                continue
            if (allele and v.get("minor_allele") != allele):
                continue
            for key in v.keys():
                if (not 'gnomad' in key):
                    continue
                g = key.split('_')
                if (len(g) <> 3):
                    continue
                a = g[1]
                tpl = ancestries.get(a, [None, None])
                if (g[2] == 'allele'):
                    tpl[0] = v[key]
                elif (g[2] == 'maf'):
                    tpl[1] = v[key]
                else:
                    raise Exception("Unrecognized key: {}".format(key))
                ancestries[a] = tpl
            if (v.has_key("frequencies")):
                array = v["frequencies"]
                for allele in array:
                    frequencies = array[allele]
                    for a in frequencies:
                        f = float(frequencies[a])
                        ancestries[a] = (allele, f)


        pop_max_a_1 = None
        pop_max_f_1 = None
        pop_max_a_2 = None
        pop_max_f_2 = None
        a1 = None
        a2 = None
        for a in ancestries.keys():
            f = ancestries[a][1]
            if (not pop_max_f_1 or f > pop_max_f_1):
                if (pop_max_f_1):
                    pop_max_f_2 = pop_max_f_1
                    pop_max_a_2 = pop_max_a_1
                    a2 = a1
                pop_max_f_1 = f
                pop_max_a_1 = ancestries[a][0]
                a1 = a

        return (a1, pop_max_a_1, pop_max_f_1, a2, pop_max_a_2, pop_max_f_2)

    def get_gnomad_af(self):
        gm_af = None
        alt_alleles = set(self.alt_list())
        collocated_variants = self.get_colocated_variants()
        # if (self.start() == 16378047):
        #     pass
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

            if (af):
                af = float(af)
            if (gm_af):
                gm_af = min(gm_af, af)
            else:
                gm_af = af

        if (gm_af):
            return gm_af

        af_e = self.get_gnomad_split_af("exomes")
        af_g = self.get_gnomad_split_af("genomes")

        return max(af_e, af_g)

    def get_gnomad_split_af(self, exomes_or_genomes):
        transcripts = self.get_transcripts()
        af = None
        if (False):
            for t in transcripts:
                af1_str = t.get("gnomad_{}_af".format(exomes_or_genomes))
                af1 = float(af1_str) if (af1_str) else None
                if (af):
                    af = min(af1, af)
                else:
                    af = af1

        if (not af):
            af = self.data.get("_private.gnomad_db_{}_af".format(exomes_or_genomes))

        return af

    def get_gnomad_split_af_by_alt(self, exomes_or_genomes, alt):
        af = self.data.get("_private.gnomad_db_{}_{}_af".format(exomes_or_genomes, alt))
        return af

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
        name = ",".join(self.samples)
        args = "file={}&genome=hg19&merge=false&name={}&locus={}:{}-{}".\
            format(','.join(file_urls), name, self.chromosome(), self.start()-250, self.end()+250)
        return "{}{}".format(url, args)

    def get_label(self):
        genes = self.get_genes()
        if (len(genes) == 0):
            gene = "None"
        elif (len(genes) < 3):
            gene = ",".join(genes)
        else:
            gene = "..."

        vstr = str(self)
        if (False):
            exp = ""
            if (self.data.get("EXPECTED")):
                exp = '+ '
            if (self.data.get("SEQaBOO")):
                pss = "* "
            else:
                pss = ""
            return "{}{}[{}] {}".format(exp, pss, gene, vstr)
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
        if (self.start() == self.end()):
            str = "{}:{}".format(self.chromosome(), self.start())
        else:
            str = "{}:{}-{}".format(self.chromosome(), self.start(), self.end())
        return str

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
                return n - s
        return None

    def get_pLI_by_allele(self, allele):
        transcripts = self.get_transcripts()
        key = "exacpli"
        list = unique([t.get(key) for t in transcripts if (t.has_key(key) and allele == t.get("variant_allele"))])
        if (len(list) > 0):
            return list
        return None

    def get_proband_GQ(self):
        return self.vcf_record.genotype(self.get_proband()).data.GQ

    def get_min_GQ(self):
        GQ = None
        for s in self.samples:
            genotype = self.vcf_record.genotype(s)
            GQ = min(genotype.data.GQ, GQ) if GQ else genotype.data.GQ
        return GQ

    def is_proband_has_variant(self):
        genotype = self.get_genotypes()[0]
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
        father = self.samples[proband]['father']
        maternal_genotype = self.vcf_record.genotype(mother).gt_bases
        paternal_genotype = self.vcf_record.genotype(father).gt_bases

        genotypes = {self.vcf_record.genotype(s).gt_bases for s in self.samples}
        other_genotypes = genotypes.difference({proband_genotype, maternal_genotype, paternal_genotype})

        return proband_genotype, maternal_genotype, paternal_genotype, other_genotypes

    def get_zygosity(self):
        genotype = self.get_genotypes()[0]
        if (not genotype):
            return None
        set1 = set(genotype.split('/'))
        if (self.chr_num().upper() == 'X' and self.proband_sex() == 1):
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

    def get_callers(self):
        bgm_callers = ['BGM_AUTO_DOM', 'BGM_DE_NOVO', 'BGM_HOM_REC', 'BGM_CMPD_HET',
                   'BGM_BAYES_DE_NOVO', 'BGM_BAYES_CMPD_HET', 'BGM_BAYES_HOM_REC']
        callers = [caller for caller in bgm_callers if (self.vcf_record.INFO.has_key(caller))]

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

    def get_view_json(self):
        data = self.data.copy()
        data['_filters.RareVariantFilter'] = "PASS" if (self.data.get("SEQaBOO")) else "False"
        data['label'] = self.get_label()
        data['color_code'] = self.get_color_code()
        view = dict()
        data["view"] = view

        proband_genotype, maternal_genotype, paternal_genotype, other = self.get_genotypes()
        tab1 = dict()
        #view['general'] = tab1
        data["view.general"] = tab1
        tab1['Gene(s)'] = self.get_genes()
        tab1['hg19'] = str(self)
        tab1['hg38'] = self.get_hg38_coordinates()
        if (not self.is_snv()):
            tab1["Ref"] = self.ref()
            tab1["Alt"] = self.alt_string()
        tab1['BGM_CMPD_HET'] = self.vcf_record.INFO.get("BGM_CMPD_HET")
        tab1['Called by'] = self.get_callers()

        (c_worst,  c_canonical, c_other) = self.get_pos_tpl('c')
        tab1['cPos (Worst)'] = c_worst
        tab1['cPos (Canonical)'] = c_canonical
        tab1['cPos (Other)'] = c_other

        (c_worst,  c_canonical, c_other) = self.get_pos_tpl('p')
        tab1['pPos (Worst)'] = c_worst
        tab1['pPos (Canonical)'] = c_canonical
        tab1['pPos (Other)'] = c_other

        tab1['Proband Genotype'] = proband_genotype
        tab1['Maternal Genotype'] = maternal_genotype
        tab1['Paternal Genotype'] = paternal_genotype

        tab1['Worst Annotation'] = self.get_msq()
        consequence_terms = self.get_from_canonical_transcript("consequence_terms")
        tab1['Canonical Annotation'] = self.most_severe(consequence_terms)

        tab1["Splice Region"] = self.get_from_transcripts("spliceregion")
        tab1["GeneSplicer"] = self.get_from_transcripts("genesplicer")

        transcripts = self.get_most_severe_transcripts()
        tab1['RefSeq Transcript (Worst)'] = get_from_transcripts(transcripts, "transcript_id", source="RefSeq")
        tab1['Ensembl Transcripts (Worst)'] = get_from_transcripts(transcripts, "transcript_id", source="Ensembl")

        transcripts = self.get_canonical_transcripts()
        tab1['RefSeq Transcript (Canonical)'] = get_from_transcripts(transcripts, "transcript_id", source="RefSeq")
        tab1['Ensembl Transcripts (Canonical)'] = get_from_transcripts(transcripts, "transcript_id", source="Ensembl")

        tab1['Variant Exon (Worst Annotation)'] = self.get_from_worst_transcript("exon")
        tab1['Variant Intron (Worst Annotation)'] = self.get_from_worst_transcript("intron")
        tab1['Variant Exon (Canonical)'] = self.get_from_canonical_transcript("exon")
        tab1['Variant Intron (Canonical)'] = self.get_from_canonical_transcript("intron")
        tab1["IGV"] = self.get_igv_url()

        tab2 = list()
        #view['quality'] = tab2
        #data["view.quality"] = tab2
        data["quality.samples"] = tab2
        q_all = dict()
        q_all["Title"] = "All"
        q_all['Strand Odds Ratio'] = self.vcf_record.INFO.get("SOR")
        q_all['Mapping Quality'] = self.vcf_record.INFO["MQ"]
        q_all['Variant Call Quality'] = self.vcf_record.QUAL

        q_all['Quality by Depth'] = self.vcf_record.INFO.get("QD")
        data['_filters.QD'] = self.vcf_record.INFO.get("QD")
        q_all['Fisher Strand Bias'] = self.vcf_record.INFO.get("FS")
        data['_filters.FS'] = self.vcf_record.INFO.get("FS")


        tab2.append(q_all)

        proband = self.get_proband()
        mother = self.samples[proband]['mother']
        father = self.samples[proband]['father']
        for s in self.samples:
            genotype = self.vcf_record.genotype(s)
            q_s = dict()
            if (s == proband):
                q_s["Title"] = "Proband: {}".format(s)
            elif (s == mother):
                q_s["Title"] = "Mother: {}".format(s)
            elif (s == father):
                q_s["Title"] = "Father: {}".format(s)
            else:
                q_s["Title"] = s

            q_s['Allelic Depth'] = genotype.data.AD
            q_s['Read Depth'] = genotype.data.DP
            q_s['Genotype Quality'] = genotype.data.GQ
            tab2.append(q_s)

        tab3 = list()
        # view['gnomAD'] = tab3
        data["view.gnomAD"] = tab3
        if (self.get_gnomad_af()):
            alt_list = self.alt_list()
            for allele in alt_list:
                gr = dict()
                tab3.append(gr)
                gr["Allele"] = allele
                gr["Proband"] = "Yes" if (self.is_proband_has_allele(allele)) else "No"
                gr["pLI"] = self.get_pLI_by_allele(allele)
                gr["Proband AF"] = self.get_gnomad_af()
                gr["Genome AF"] = self.get_gnomad_split_af_by_alt("genomes", allele)
                gr["Exome AF"] = self.get_gnomad_split_af_by_alt("exomes", allele)
                pop_max = self.get_gnomad_pop_max(allele=allele)
                if (pop_max[0]):
                    gr["PopMax #1"] = "{}: {}={}".format(pop_max[0], pop_max[1], pop_max[2])
                if (pop_max[3]):
                    gr["PopMax #2"] = "{}: {}={}".format(pop_max[3], pop_max[4], pop_max[5])

                gr["URL"] = \
                    "http://gnomad.broadinstitute.org/variant/{}-{}-{}-{}".format(self.chr_num(), self.start(), self.ref(), allele)

        tab4 = dict()
        #view['Databases'] = tab4
        data["view.Databases"] = tab4
        genes = self.get_genes()
        omim_urls = [
            "https://omim.org/search/?search=approved_gene_symbol:{}&retrieve=geneMap".format(gene) for gene in genes
        ]
        tab4["OMIM"] = omim_urls
        tab4['GeneCards'] = ["https://www.genecards.org/cgi-bin/carddisp.pl?gene={}".format(g) for g in genes]
        if (self.data.get("HGMD")):
            tab4["HGMD"] = self.data.get("HGMD")
            tab4["HGMD (HG38)"] = self.data.get("HGMD_HG38")
        else:
            tab4["HGMD"] = "Not Present"
        pmids = self.data.get("_private.HGMD_PIMIDs")
        tab4["HGMD TAGs"] = [link_to_pmid(pmid[2]) for pmid in pmids] if pmids else None
        tab4["HGMD PMIDs"] = [link_to_pmid(pmid[1]) for pmid in pmids] if pmids else None
        phenotypes = self.data.get("_private.HGMD_phenotypes")
        tab4["HGMD Phenotypes"] = [p[0] for p in phenotypes] if phenotypes else None

        if (self.data.get("ClinVar") <> None):
            tab4["ClinVar"] = "https://www.ncbi.nlm.nih.gov/clinvar/?term={}[chr]+AND+{}%3A{}[chrpos37]".\
                format(self.chr_num(), self.start(), self.end())
        tab4['ClinVar Significance'] = unique(self.get_from_transcripts_list('clinvar_clnsig') +
                                              self.get_from_transcripts_list('clin_sig'))

        tab5 = dict()
        #view['Predictions'] = tab5
        data["view.Predictions"] = tab5
        lof_score = self.get_from_transcripts("loftool")
        lof_score.sort(reverse=True)
        tab5["LoF Score"] = lof_score
        lof_score = self.get_from_canonical_transcript("loftool")
        lof_score.sort(reverse=True)
        tab5["LoF Score (Canonical)"] = lof_score

        tab5["MaxEntScan"] = self.get_max_ent()

        tab5['Polyphen'] = unique(self.get_from_transcripts_list("polyphen_prediction"))
        tab5['Polyphen 2 HVAR'] = unique(self.get_from_transcripts_list("Polyphen2_HVAR_pred".lower()))
        tab5['Polyphen 2 HDIV'] = unique(self.get_from_transcripts_list("Polyphen2_HDIV_pred".lower()))
        tab5['Polyphen 2 HVAR score'] = unique(self.get_from_transcripts_list("Polyphen2_HVAR_score".lower()))
        tab5['Polyphen 2 HDIV score'] = unique(self.get_from_transcripts_list("Polyphen2_HDIV_score".lower()))
        tab5['SIFT'] = unique(self.get_from_transcripts_list("sift_prediction"))
        tab5['SIFT score'] = unique(self.get_from_transcripts_list("sift_score"))
        tab5["REVEL"] = unique(self.get_from_transcripts_list("revel_score"))
        tab5["Mutation Taster"] = unique(self.get_from_transcripts_list("mutationtaster_pred"))
        tab5["FATHMM"] = unique(self.get_from_transcripts_list("fathmm_pred"))
        tab5["CADD (Phred)"] = unique(self.get_from_transcripts_list("cadd_phred"))
        tab5["CADD (Raw)"] = unique(self.get_from_transcripts_list("cadd_raw"))
        tab5["Mutation Assessor"] = unique(self.get_from_transcripts_list("mutationassessor_pred"))

        tab6 = dict()
        #view['Genetics'] = tab6
        data["view.Genetics"] = tab6
        tab6["Zygosity"] = self.get_zygosity()
        tab6["Inherited from"] = self.inherited_from()
        tab6["Distance From Intron/Exon Boundary (Worst)"] = self.get_distance_from_exon("worst")
        tab6["Distance From Intron/Exon Boundary (Canonical)"] = self.get_distance_from_exon("canonical")
        tab6["Conservation"] = unique(self.get_from_transcripts_list("conservation"))
        tab6["Species with variant"] = ""
        tab6["Species with other variants"] = ""
        tab6["MaxEntScan"] = self.get_max_ent()
        tab6["NNSplice"] = ""
        tab6["Human Splicing Finder"] = ""
        tab6["other_genes"] = self.get_other_genes()

        tab7 = dict()
        #view['Inheritance'] = tab7
        data["view.Inheritance"] = tab7


        return json.dumps(data)