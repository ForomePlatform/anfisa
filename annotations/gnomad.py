import json

from annotations import positions
from annotations.db_connect import Connection

def get_af_from_row(ref, alt, REF, ALT, MAX_AF, AFs):
    try:
        if (ref != REF):
            if (REF[0] == ref):
                alt = alt + REF[1:]
            elif (ref in REF):
                s = REF.split(ref)
                alt = alt.join(s)
            else:
                return None

        alts = ALT.split(',')
        l = len(alts)
        if (l == 1 and ALT == alt):
            return MAX_AF
        i2 = alts.index(alt)
    except:
        return None
    return float(AFs.split(',')[i2])


def af_(an, ac):
    af = float(ac) / an if an > 0 else 0
    return af


def diff(s1, s2):
    if (s1 == s2):
        return ""
    if (s1 in s2):
        idx = s2.find(s1)
        return s2[0:idx] + s2[idx+len(s1):]
    elif (len(s1) < len(s2)):
        x = []
        y = []
        for i in range(0, len(s2)):
            j = len(x)
            if (j < len(s1) and s1[j] == s2[i]):
                x.append(s2[i])
            else:
                y.append(s2[i])
        if (y):
            return "".join(y)
        return None
    elif (len(s2) < len(s1)):
        return "-" + diff(s2, s1)
    else:
        return None


def diff3(s1, s2, d):
    if (not d):
        return s1 == s2
    if (d[0] == '-'):
        return diff3(s2, s1, d[1:])
    if (len(s1) + len(d) != len(s2)):
        return False
    for i in range(0, len(s1)):
        x = s1[:i]
        y = s1[i:]
        if (x + d + y == s2):
            return True
    return False


class GnomAD(Connection):
    ANCESTRIES = [
        "AFR",
        "AMR",
        "ASJ",
        "EAS",
        "FIN",
        "NFE",
        "OTH",
    ]

    SEX = [
        "Male",
        "Female"
    ]

    POP_GROUPS = ANCESTRIES + SEX

    DATA_SUFFIXES = [
        "raw",
        "POPMAX"
    ] + POP_GROUPS

    TABLE = "gnomad.VARIANTS"
    KEY_COLUMNS = [
            "CHROM",
            "POS",
            "ID",
            "REF",
            "ALT"
    ]
    DATA_PREFIXES = ["AN", "AC", "Hom"]

    hom = ['_'.join(["Hom", a]) for a in ANCESTRIES]
    hom_column = " + ".join(hom)

    AGGREGATE_DATA_COLUMNS = [
        "AN_Female + AN_Male as AN",
        "AC_Female + AC_Male as AC",
        hom_column + " as Hom",
        "AN_POPMAX",
        "AC_POPMAX",
        "POPMAX"
    ]
    DATA_COLUMNS = ['_'.join([a,b]) for a in DATA_PREFIXES for b in DATA_SUFFIXES if (not (a == "Hom" and b == "POPMAX"))]

    COLUMNS = KEY_COLUMNS + AGGREGATE_DATA_COLUMNS + DATA_COLUMNS
    C_DICT = dict()
    for i in range(0, len(COLUMNS)):
        c = COLUMNS[i]
        if (" as " in c):
            c = c.split(" as ")[1]
        C_DICT[c] = i

    def __init__(self, host = "anfisa.forome.org:ip-172-31-24-96",
            database = "gnomad", port = None, user = "hgmd",
            password = "hgmd", dbms = "MySQL",
            ssh_user = None, driver = None,
            java_class_path = None, connect_now = True):
        Connection.__init__(self, host = host,
            database = database, port = port, user = user,
            password = password, dbms = dbms,
            ssh_user = ssh_user, driver = driver,
            java_class_path = java_class_path, connect_now = connect_now)

    def fetch_data(self, sql, args, ref=None, alt=None):
        if (ref or alt):
            sql = sql.format(ref=ref, alt=alt)
        c = self.connection.cursor()
        c.execute(sql, args)
        rows = c.fetchall()
        return rows

    def get_data(self, chr, pos, ref=None, alt=None, from_what = None, exact = False):
        args = (chr, pos)
        p = self.parameter()
        select_list = ', '.join(self.COLUMNS)
        base_sql = "SELECT {columns} FROM {table} WHERE CHROM = {chrom} and POS = {pos}".\
            format(columns=select_list, table=self.TABLE, chrom=p, pos=p)

        if (ref and alt):
            if (exact):
                sql = base_sql + " and REF = '{ref}' and ALT = '{alt}'"
            else:
                sql = base_sql + " and (REF LIKE '%{ref}%' and ALT LIKE '%{alt}%')"

        if (from_what):
            q = from_what.lower().split(',')
            if (len(q) == 1):
                if ("exome" in q[0]):
                    s = 'e'
                elif ("genome" in q[0]):
                    s = 'g'
                else:
                    s = q[0]
            if not ('e' in q and 'g' in q):
                sql = "{} and `SOURCE` = '{}'".format(sql, s)

        rows = self.fetch_data(sql, ref=ref, alt=alt, args=args)

        if (not exact and len(rows) == 0 and ref and alt):
            rows = self.fetch_data(base_sql, (chr, pos - 1), None, None)

            # if (len(ref) > len(alt)):
            #     if (alt in ref):
            #         idx = ref.find(alt)
            #         if (idx == 0):
            #             n = len(alt) - 1
            #             new_alt = alt[n]
            #             new_ref = ref[n:]
            #             # new_alt = alt[0]
            #             # new_ref = ref[0] + ref[len(alt):]
            #         else:
            #             new_ref = None
            #             new_alt = None
            #         rows = self.fetch_data(sql, (chr, pos + idx - 1), new_ref, new_alt)
            # elif (len(alt) > len(ref)):
            #     if (ref in alt):
            #         idx = alt.find(ref)
            #         if (idx == 0):
            #             n = len(ref) - 1
            #             new_ref = ref[n]
            #             new_alt = alt[n:]
            #         else:
            #             new_ref = None
            #             new_alt = None
            #         rows = self.fetch_data(sql, (chr, pos + idx - 1), new_ref, new_alt)

        if (not exact and rows):
            diff_ref_alt = diff(ref, alt)
            rows = [r for r in rows if (diff_ref_alt == diff(r[3], r[4]) or diff3(r[3], r[4], diff_ref_alt))]

        return rows

    def get_from_row(self, column, row):
        return row[self.C_DICT[column]]

    def get_int_from_row(self, column, row):
        v = self.get_from_row(column, row)
        if (not v):
            return 0
        return int(v)

    def get_an_and_ac(self, rows, group = None):
        an = 0
        ac = 0
        an_column = '_'.join(["AN",group]) if group else "AN"
        ac_column = '_'.join(["AC",group]) if group else "AC"
        for row in rows:
            an += self.get_int_from_row(an_column, row)
            ac += self.get_int_from_row(ac_column, row)

        return an, ac

    def get_hom(self, rows, group = None):
        hom = 0
        column = '_'.join(["Hom",group]) if group else "Hom"
        for row in rows:
            hom += self.get_int_from_row(column, row)

        return hom

    def get_af(self, chr, pos, ref, alt, group = None, from_what = 'e,g'):
        rows = self.get_data(chr, pos, ref, alt, from_what)
        if (len(rows) == 0):
            return None

        an, ac = self.get_an_and_ac(rows, group)
        af = af_(an, ac)

        return af

    def popmax_from_rows(self, rows):
        popmax = None
        popmax_af = None
        popmax_an = None

        for group in self.ANCESTRIES:
            an, ac = self.get_an_and_ac(rows, group)
            if (not an):
                continue
            af = float(ac) / an
            if (af > popmax_af):
                popmax = group
                popmax_af = af
                popmax_an = an

        return popmax, popmax_af, popmax_an

    def get_popmax(self, chr, pos, ref, alt, from_what = 'e,g'):
        rows = self.get_data(chr, pos, ref, alt, from_what)
        if (len(rows) == 0):
            return None
        return self.popmax_from_rows(rows)

    def get_all(self, chr, pos, ref, alt):
        data = dict()
        exomes = self.get_data(chr, pos, ref, alt, from_what='e')
        genomes = self.get_data(chr, pos, ref, alt, from_what='g')
        rows = exomes + genomes
        if (len(rows) == 0):
            return data

        for key, row_set in {"overall": rows, "exomes":exomes, "genomes":genomes}.items():
            if (len(row_set) == 0):
                continue
            an, ac = self.get_an_and_ac(row_set)
            af = af_(an, ac)
            data[key] = dict()
            data[key]["AN"] = an
            data[key]["AC"] = ac
            data[key]["AF"] = af
            data[key]["HOM"] = self.get_hom(row_set)
            if (chr in ['x', 'X']):
                junk, data[key]["HEM"] = self.get_an_and_ac(row_set, "Male")

        popmax, popmax_af, popmax_an= self.popmax_from_rows(rows)
        data["popmax"] = popmax
        data["popmax_af"] = popmax_af
        data["popmax_an"] = popmax_an

        unique_rows = set()
        for row in rows:
            chrom = self.get_from_row("CHROM", row)
            pos = self.get_from_row("POS", row)
            ref = self.get_from_row("REF", row)
            alt = self.get_from_row("ALT", row)

            new_ref, new_alt = positions.transform_ref_alt(ref, alt)

            unique_rows.add((chrom, pos, new_ref, new_alt))

        data["url"] = [
            "http://gnomad.broadinstitute.org/variant/{}-{}-{}-{}".format(chrom, pos, ref, alt)
            for (chrom, pos, ref, alt) in unique_rows
        ]

        return data

    def less_than(self, chr, pos, ref, alt, threshold):
        af = self.get_af(chr, pos, ref, alt)

        if (not af):
            return True
        return (af < threshold)


if __name__ == '__main__':
    with GnomAD() as gnomAD:
        print gnomAD.get_af(11, 27679011, 'GTT', 'GT')

        print gnomAD.get_af(2, 55863111, 'CTA', 'C')
        print gnomAD.get_af(7, 30051225, 'ATATT', 'AT')
        print gnomAD.get_af(1, 6484880, 'A', 'G')

        # print json.dumps(gnomAD.get_all(2, 55863111, 'CTA', 'C'), indent=2)
        # print json.dumps(gnomAD.get_all(7, 30051225, 'ATATT', 'AT'), indent=2)
        #
        # print json.dumps(gnomAD.get_all(1, 6484880, 'A', 'G'), indent=2)
        # print json.dumps(gnomAD.get_all('X', 153010066, 'C', 'T'), indent=2)
        #
        print gnomAD.get_all(1, 103471457, "CCATCAT", "CCAT")
        print gnomAD.get_af(1, 160009164, "GACACACACACACAC", "GACACACACACACACAC")
        print gnomAD.get_af(4, 88536543, "AACAGCAGTG", "A")

        print gnomAD.get_af(4, 88535832, 'A', 'ATAGCAGTGACAGCAGCAG')
        print gnomAD.get_af(4, 88535832, 'A', 'ATAGCAGTGACAGCAGCAG', group='ASJ')
        print gnomAD.get_af(4, 88535832, 'A', 'ATAGCAGTGACAGCAGCAG', group='Male')
        print gnomAD.get_af(2, 73675844, 'C', 'T', from_what='e'), gnomAD.get_af(2, 73675844, 'C', 'T', from_what='g')
        print "PopMax: ", gnomAD.get_popmax(2, 73675844, 'C', 'T')
        print gnomAD.get_af(1, 16360424, 'G', 'C')
        print gnomAD.get_af(1, 6484880, 'A', 'G')
        print gnomAD.get_all(1, 6484880, 'A', 'G')
        print gnomAD.get_all(2, 73675844, 'C', 'T')

