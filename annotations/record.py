import json
from StringIO import StringIO

import vcf

def unique(list):
    s = set(list)
    s.discard(None)
    list2 = []
    list2.extend(s)
    return list2

def hgvcs_pos(str, type, with_pattern = True):
    pattern = ":{}.".format(type)
    if (not pattern in str):
        return None
    x = str.split(pattern)[1]
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

    def __init__(self, json_string, vcf_header = None, case = None, samples = None):
        self.original_json = json_string
        self.data = json.loads(json_string)
        self.case = case
        self.samples = samples
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
        str = "{}:{}".format(self.chromosome(), self.start())
        if (self.is_snv()):
            return "{}  {}>{}".format(str, self.ref(), self.alt_string())
        return "{} {}".format(str, self.get_variant_class())
    
    def get_msq(self):
        return self.data.get("most_severe_consequence")

    def is_snv(self):
        return self.get_variant_class() == "SNV"

    def get_variant_class(self):
        return self.data.get("variant_class")

    def get_transcripts(self):
        return self.data.get("transcript_consequences", [])

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
    
    def get_most_severe_transcripts(self):
        msq = self.get_msq()
        return [t for t in self.get_transcripts() if (msq in t.get("consequence_terms"))]

    def get_from_transcripts_list(self, key):
        return unique([t.get(key) for t in self.get_transcripts() if (t.has_key(key))])

    def get_from_worst_transcript(self, key):
        return unique([t.get(key) for t in self.get_most_severe_transcripts() if (t.has_key(key))])

    def get_from_canonical_transcript(self, key):
        return unique([t.get(key) for t in self.get_canonical_transcripts() if (t.has_key(key))])

    def get_canonical_transcripts(self):
        return [t for t in self.get_transcripts() if (t.get("canonical"))]

    def get_genes(self):
        return unique(self.get_from_transcripts_list("gene_symbol"))

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

    def get_distance_from_exon(self, kind):
        return unique([get_distance_hgvsc(hgvcs) for hgvcs in self.get_hgvs_list(kind) if hgvcs])

    def get_gnomad_pop_max(self):
        ancestries = dict()
        collocated_variants = self.get_colocated_variants()
        for v in collocated_variants:
            if (v.get("somatic")):
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
        for t in transcripts:
            af1_str = t.get("gnomad_{}_af".format(exomes_or_genomes))
            af1 = float(af1_str) if (af1_str) else None
            if (af):
                af = min(af1, af)
            else:
                af = af1

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
        exp = ""
        if (self.data.get("EXPECTED")):
            exp = '+ '
        if (self.data.get("SEQaBOO")):
            pss = "* "
        else:
            pss = ""
        return "{}{}[{}] {}".format(exp, pss, gene, vstr)

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

        return code

    def get_pLI(self):
        list = self.get_from_transcripts_list("exacpli")
        if (len(list) > 0):
            return list
        return None

    def get_view_json(self):
        data = self.data.copy()
        data['label'] = self.get_label()
        data['color_code'] = self.get_color_code()
        view = dict()
        data["view"] = view

        proband = self.get_proband()
        proband_genotype = self.vcf_record.genotype(proband)
        mother = self.samples[proband]['mother']
        father = self.samples[proband]['father']
        genotypes = [self.vcf_record.genotype(s) for s in self.samples]

        tab1 = dict()
        #view['general'] = tab1
        data["view.general"] = tab1
        tab1['Gene(s)'] = self.get_genes()
        tab1['header'] = str(self)
        if (not self.is_snv()):
            tab1["Ref"] = self.ref()
            tab1["Alt"] = self.alt_string()
        tab1['BGM_CMPD_HET'] = self.vcf_record.INFO.get("BGM_CMPD_HET")
        callers = ['BGM_AUTO_DOM', 'BGM_DE_NOVO', 'BGM_HOM_REC', 'BGM_CMPD_HET',
                   'BGM_BAYES_DE_NOVO', 'BGM_BAYES_CMPD_HET', 'BGM_BAYES_HOM_REC']
        tab1['Called by'] = [caller for caller in callers if (self.vcf_record.INFO.has_key(caller))]
        tab1['cPos'] = self.get_pos('c')
        tab1['pPos'] = self.get_pos('p')
        tab1['Proband Genotype'] = proband_genotype.gt_bases
        tab1['Maternal Genotype'] = self.vcf_record.genotype(mother).gt_bases
        tab1['Paternal Genotype'] = self.vcf_record.genotype(father).gt_bases

        tab1['Worst Annotation'] = self.get_msq()

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
        q_all['Fisher Strand Bias'] = self.vcf_record.INFO.get("FS")
        tab2.append(q_all)

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

        if (self.get_gnomad_af()):
            tab3 = dict()
            #view['gnomAD'] = tab3
            data["view.gnomAD"] = tab3
            tab3["AF"] = self.get_gnomad_af()
            tab3["Genome AF"] = self.get_gnomad_split_af("genomes")
            tab3["Exome AF"] = self.get_gnomad_split_af("exomes")
            pop_max = self.get_gnomad_pop_max()
            if (pop_max[0]):
                tab3["PopMax #1"] = "{}: {}={}".format(pop_max[0], pop_max[1], pop_max[2])
            if (pop_max[3]):
                tab3["PopMax #2"] = "{}: {}={}".format(pop_max[3], pop_max[4], pop_max[5])

            alt_list = self.alt_string().split(',')
            tab3["URL"] = [
                "http://gnomad.broadinstitute.org/variant/{}-{}-{}-{}".format(self.chr_num(), self.start(), self.ref(), alt)
                for alt in alt_list
            ]
        else:
            data["view.gnomAD"] = None

        tab4 = dict()
        #view['Databases'] = tab4
        data["view.Databases"] = tab4
        tab4["OMIM"] = ""
        tab4["pLI"] = self.get_pLI()
        if (self.data.get("HGMD")):
            tab4["HGMD"] = self.data.get("HGMD")
            tab4["HGMD PMIDs"] = ""
        if (self.data.get("ClinVar") <> None):
            tab4["ClinVar"] = "https://www.ncbi.nlm.nih.gov/clinvar/?term={}[chr]+AND+{}%3A{}[chrpos37]".\
                format(self.chr_num(), self.start(), self.end())
        tab4['ClinVar Significance'] = unique(self.get_from_transcripts_list('clinvar_clnsig') +
                                              self.get_from_transcripts_list('clin_sig'))

        tab5 = dict()
        #view['Predictions'] = tab5
        data["view.Predictions"] = tab5
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
        tab6["Distance From Intron/Exon Boundary (Worst)"] = self.get_distance_from_exon("worst")
        tab6["Distance From Intron/Exon Boundary (Canonical)"] = self.get_distance_from_exon("canonical")
        tab6["Conservation"] = unique(self.get_from_transcripts_list("conservation"))
        tab6["Species with variant"] = ""
        tab6["Species with other variants"] = ""
        tab6["MaxEntScan"] = ""
        tab6["NNSplice"] = ""
        tab6["Human Splicing Finder"] = ""

        tab7 = dict()
        #view['Inheritance'] = tab7
        data["view.Inheritance"] = tab7


        return json.dumps(data)