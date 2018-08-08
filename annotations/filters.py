import os
import abc

# from pipeline.annotations import gnomad
from annotations import gnomad
from annotations.record import Variant


class Filter:
    def __init__(self):
        self.stat = dict()
        self.stat['accepted'] = 0

    @abc.abstractmethod
    def accept_variant(self, variant):
        return

    def accept(self, vcf_record):
        if self.accept_variant(vcf_record):
            self.stat['accepted'] += 1
            return True
        return False


class DBFilter(Filter):
    def __init__(self, data_dir):
        Filter.__init__(self)
        self._data_dir = data_dir


class Filter_HGMD (DBFilter):
    def __init__(self, data_dir):
        DBFilter.__init__(self, data_dir)
        hgmd_dir = os.path.join(data_dir, "HGMD_download")

        hgmd_file = os.path.join(hgmd_dir, "hg19_coord.csv")

        self.hgmd = dict()
        with open(hgmd_file) as f:
            for line in f.readlines():
                if (line.startswith('#')):
                    continue
                data = line.split()
                c = data[1].strip()
                p1 = int(data[3].strip())
                p2 = int(data[4].strip())
                self.hgmd[(c, p1, p2)] = 1

    def accept_variant(self, variant):
        return (self.hgmd.has_key(variant.key()))


class Filter_ClinVar(DBFilter):
    def __init__(self, data_dir):
        DBFilter.__init__(self, data_dir)
        clinvar_dir = os.path.join(data_dir, "clinvar")

        clinvar_file = os.path.join(clinvar_dir, "hg19_coord.csv")
        self.clinvar = {}
        with open(clinvar_file) as f:
            for line in f.readlines():
                rs = line.split()[0].strip()
                self.clinvar[rs] = 1


    def accept_variant(self, variant):
        return (self.clinvar.has_key(variant.rs_id()))


class NumericVCFFilter(Filter):
    def __init__(self, filters):
        Filter.__init__(self)
        self.filters = filters

    def accept_variant(self, variant):
        info = variant.info()
        for key in self.filters:
            if (info.has_key(key)):
                v = float(info[key])
                op = self.filters[key][0]
                threshold = self.filters[key][1]
                if (op == '<='):
                    result = (v <= threshold)
                elif (op == '>='):
                    result = (v >= threshold)
                if (not result):
                    return False
            else:
                return False
        return True


class Filter_Quality(NumericVCFFilter):
    # QD >= 4
    # FS <= 30
    CONDITIONS =  {
        'QD':['>=', 4],
        'FS':['<=', 30]
    }
    def __init__(self):
        NumericVCFFilter.__init__(self, Filter_Quality.CONDITIONS)

    @classmethod
    def keys(self):
        return Filter_Quality.CONDITIONS.keys()


class Filter_gnomAD_AF_local(Filter):
    def __init__(self, threshold):
        Filter.__init__(self)
        self.threshold = threshold

    def accept_variant(self, variant):
        return (variant.get_gnomad_af() <= self.threshold)


class Filter_gnomAD_AF(Filter):
    def __init__(self, threshold):
        Filter.__init__(self)
        self.threshold = threshold

    def accept_variant(self, variant):
        return gnomad.less_than(variant.chromosome, variant.pos, variant.ref, variant.alt, self.threshold)


def process_header(line, output, columns):
    if (len(line) < 2):
        return True
    if (line.startswith('#')):
        if (output):
            output.write(line)
        if (not line.startswith('##')):
            cols = line.split()
            for i in range(0, len(cols)):
                col = cols[i].strip()
                if (i == 0 and col.startswith('#')):
                    col = col[1:]
                columns[col] = i
        return True
    return False


def process_vcf_header(vcf_file):
    columns = {}
    with open (vcf_file) as input:
            while(True):
                line = input.readline()
                if (not line):
                    break
                if (process_header(line, output=None, columns=columns)):
                    continue
                break
    return columns
