import os
import sqlite3


gnomAD_dir = "/opt/data/gnomad"
db_file_genomes = os.path.join(gnomAD_dir, "gnomAD.db")
db_file_exomes = os.path.join(gnomAD_dir, "gnomAD_exomes.db")


def get_data(chr, pos, ref=None, alt=None):
    if (ref and alt):
        sql = '''SELECT CHROM, POS, ID, REF, ALT, MAX_AF, AFs FROM AF WHERE CHROM = ? and POS = ? and REF = ? and ALT = ?'''
        args = (chr, pos, ref, alt)
    else:
        sql = '''SELECT CHROM, POS, ID, REF, ALT, MAX_AF, AFs FROM AF WHERE CHROM = ? and POS = ?'''
        args = (chr, pos)

    conn = sqlite3.connect(db_file_genomes)
    c = conn.cursor()


    rows = [row for row in c.execute(sql, args)]

    c.close()
    conn.close()

    conn = sqlite3.connect(db_file_exomes)
    c = conn.cursor()

    rows += [row for row in c.execute(sql, args)]

    return rows

    # if (len(rows) == 0):
    #     return None
    # if (len(rows) > 1):
    #     raise Exception("Ambiguous Result: chr{}:{}".format(chr, pos))
    # return rows[0]


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
    return AFs.split(',')[i2]


def get_af(chr, pos, ref, alt):
    rows = get_data(chr, pos, ref, alt)
    if (len(rows) == 0):
        return None

    for row in rows:
        (CHROM, POS, ID, REF, ALT, MAX_AF, AFs) = row
        return get_af_from_row(ref, alt, REF, ALT, MAX_AF, AFs)


def less_than(chr, pos, ref, alt, threshold):
    rows = get_data(chr, pos, ref, alt)
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

