import os
import sqlite3
from annotations import gnomAD_path


def get_af_from_row(ref, alt, REF, ALT, MAX_AF, AFs):
    try:
        i1 = REF.split(',').index(ref)
        alts = ALT.split(',')
        l = len(alts)
        if (l == 1 and ALT == alt):
            return MAX_AF
        i2 = alts.index(alt)
    except:
        return None
    return float(AFs.split(',')[i2])


class GnomAD:
    def __init__(self, path_to_gnomad_data = None):
        if (not path_to_gnomad_data):
            path_to_gnomad_data = gnomAD_path()

        self.db_file_genomes = os.path.join(path_to_gnomad_data, "gnomAD_genomes.db")
        self.db_file_exomes = os.path.join(path_to_gnomad_data, "gnomAD_exomes.db")
        self.connection_to_exomes = sqlite3.connect(self.db_file_exomes)
        self.connection_to_genomes = sqlite3.connect(self.db_file_genomes)

    def get_data(self, chr, pos, ref=None, alt=None, from_what = 'e,g'):
        from_what = from_what.lower()
        if (ref and alt):
            sql = '''SELECT CHROM, POS, ID, REF, ALT, MAX_AF, AFs FROM AF WHERE CHROM = ? and POS = ? and REF LIKE %?% and ALT = ?'''
            args = (chr, pos, ref, alt)
        else:
            sql = '''SELECT CHROM, POS, ID, REF, ALT, MAX_AF, AFs FROM AF WHERE CHROM = ? and POS = ?'''
            args = (chr, pos)

        if ('e' in from_what):
            c = self.connection_to_exomes.cursor()
            rows = [row for row in c.execute(sql, args)]
            c.close()
        else:
            rows = []

        if ('e' in from_what):
            c = self.connection_to_genomes.cursor()
            rows += [row for row in c.execute(sql, args)]
            c.close()

        return rows

        # if (len(rows) == 0):
        #     return None
        # if (len(rows) > 1):
        #     raise Exception("Ambiguous Result: chr{}:{}".format(chr, pos))
        # return rows[0]



    def get_af(self, chr, pos, ref, alt, from_what = 'e,g'):
        rows = self.get_data(chr, pos, None, None)
        if (len(rows) == 0):
            return None

        af = None
        for row in rows:
            (CHROM, POS, ID, REF, ALT, MAX_AF, AFs) = row
            af = max(af, get_af_from_row(ref, alt, REF, ALT, MAX_AF, AFs))
        return af

    def less_than(self, chr, pos, ref, alt, threshold):
        rows = self.get_data(chr, pos, ref, alt)
        if (len(rows) == 0):
            return True

        af = None
        for row in rows:
            (CHROM, POS, ID, REF, ALT, MAX_AF, AFs) = row
            af1 = get_af_from_row(ref, alt, REF, ALT, MAX_AF, AFs)
            if (not af or (af < af1)):
                af = af1

        if (not af):
            return True
        return (af < threshold)


if __name__ == '__main__':
    gnomAD = GnomAD()
    print gnomAD.get_af(1, 16360424, 'G', 'C')
    print gnomAD.get_af(1, 6484880, 'A', 'G')