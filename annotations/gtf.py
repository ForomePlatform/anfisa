import bisect

from annotations.db_connect import Connection



class GTF(Connection):
    TABLE = "GTF"
    GENE_BUCKET_SIZE = 1000000
    COLUMNS = [
        "chromosome",
        "source",
        "feature",
        "start",
        "end",
        "score",
        "strand",
        "frame",
        "attribute",
        "gene",
        "biotype",
        "exon",
        "transcript"
    ]

    def __init__(self, host = "anfisa.forome.org:ip-172-31-24-96:MishaMBP3.mmcentre.org", *args, **kvargs):
        if (not "database" in kvargs):
            kvargs["database"] = "ensembl"
        if (not "user" in kvargs):
            kvargs["user"] = "hgmd"
        if (not "password" in kvargs):
            kvargs["password"] = "hgmd"
        Connection.__init__(self, host, connect_now=True, *args, **kvargs)
        self.table = "{}.{}".format(self.database, self.TABLE)

    def prepare_lookup(self, chromosome=None, gene=None, transcript=None, feature="exon"):
        if (chromosome == None and gene == None and transcript == None):
            raise Exception("At least one of: chromosome, gene or transcript is required")
        select = "SELECT {}, {}, {} from {}".format(self.quote("start"), self.quote("end"), "feature", self.table)
        conditions = []
        if (chromosome != None):
            conditions.append("chromosome")
        if (gene != None):
            conditions.append("gene")
        if (transcript != None):
            conditions.append("transcript")

        ccc = ["{} = {}".format(c, self.parameter()) for c in conditions]
        if (feature != None):
            ccc.append("feature = '{}'".format(feature))
        condition = " AND ".join(ccc)
        order = "{}, {}".format(self.quote("start"), self.quote("end"))
        sql = "{} WHERE {} ORDER BY {}".format(select, condition, order)
        return Lookup(self.connection, sql, conditions)

    def get_gene(self, chromosome, pos):
        sql = "SELECT gene FROM {}_gene WHERE chromosome = {} AND bucket = {} AND {} between {} and {}" \
            .format(self.table, self.parameter(), self.parameter(), self.parameter(), self.quote("start"),
                    self.quote("end"))
        bucket = (pos / self.GENE_BUCKET_SIZE) * self.GENE_BUCKET_SIZE
        cursor = self.connection.cursor()
        cursor.execute(sql, (chromosome, bucket, pos))
        rows = cursor.fetchall()
        if (rows):
            return rows[0][0]


class Lookup:
    def __init__(self, connection, sql, conditions):
        self.sql = sql
        self.conditions = conditions
        self.connection = connection
        self.verbose = False

    def get_rows(self, args):
        if (len(set(self.conditions) & set(args.keys())) != len(args)):
            e = ",".join(self.conditions)
            a = ",".join(args.keys())
            raise Exception("Incorrect Arguments: Expected: {}, Actual: {}".format(e, a))
        paramaters = tuple([args[c] for c in self.conditions])
        cursor = self.connection.cursor()
        cursor.execute(self.sql, paramaters)
        rows = cursor.fetchall()
        return rows

    def lookup(self, pos, args):
        rows = self.get_rows(args)
        n = len(rows)
        if (n == 0):
            return None
        inf = rows[0][0]
        if (pos < inf):
            return (inf-pos), "upstream"
        sup = rows[-1][1]
        if (pos > sup):
            return (pos-sup), "downstream"

        a = []
        for row in rows:
            a.append(row[0])
            a.append(row[1])
        i = bisect.bisect(a, pos)

        if (pos == inf or pos == sup):
            d = 0
        else:
            try:
                d = min(pos - a[i-1], a[i] - pos)
            except:
                raise

        if ((i%2) == 1):
            index = (i+1)/2
            region = "exon"
        else:
            index = i/2
            region = "intron"
        if (self.verbose):
            return d, region, "{}/{}".format(index, n), inf, sup
        else:
            return d, region, index, n


if __name__ == '__main__':
    with GTF() as gtf:
        lookup = gtf.prepare_lookup(gene=True, transcript=True)
        lookup.verbose = True
        print lookup.lookup(pos=6484880, args={"gene":"HES2", "transcript":"ENST00000377834"})
        print lookup.lookup(pos=6484880, args={"gene":"ESPN", "transcript":"ENST00000377828"})
        print lookup.lookup(pos=6500660, args={"gene":"ESPN", "transcript":"ENST00000377828"})
        print lookup.lookup(pos=6501044, args={"gene":"ESPN", "transcript":"ENST00000377828"})
        print lookup.lookup(pos=6520312, args={"gene":"ESPN", "transcript":"ENST00000377828"})
        print lookup.lookup(pos=12058802, args={"gene":"MFN2", "transcript":"ENST00000235329"})
        print lookup.lookup(pos=12062017, args={"gene":"MFN2", "transcript":"ENST00000235329"})
        print lookup.lookup(pos=12065841, args={"gene":"MFN2", "transcript":"ENST00000235329"})
        print lookup.lookup(pos=16360550, args={"gene":"CLCNKA", "transcript":"ENST00000331433"})
        print lookup.lookup(pos=16370215, args={"gene":"CLCNKB", "transcript":"ENST00000375679"})
        print lookup.lookup(pos=16371067, args={"gene":"CLCNKB", "transcript":"ENST00000375679"})

        print gtf.get_gene(5, 70818177)

        print "==================================="

        lookup = gtf.prepare_lookup(gene=True)
        lookup.verbose = True
        print lookup.lookup(pos=6484880, args={"gene":"HES2"})
        print lookup.lookup(pos=6484880, args={"gene":"ESPN"})
        print lookup.lookup(pos=6500660, args={"gene":"ESPN"})
        print lookup.lookup(pos=6501044, args={"gene":"ESPN"})
        print lookup.lookup(pos=6520312, args={"gene":"ESPN"})
        print lookup.lookup(pos=12058802, args={"gene":"MFN2"})
        print lookup.lookup(pos=12062017, args={"gene":"MFN2"})
        print lookup.lookup(pos=12065841, args={"gene":"MFN2"})
        print lookup.lookup(pos=16360550, args={"gene":"CLCNKA"})
        print lookup.lookup(pos=16370215, args={"gene":"CLCNKB"})
        print lookup.lookup(pos=16371067, args={"gene":"CLCNKB"})

        print "==================================="

        lookup = gtf.prepare_lookup(chromosome=True)
        lookup.verbose = True
        print lookup.lookup(pos=6484880, args={"chromosome":"1"})
        print lookup.lookup(pos=6484880, args={"chromosome":"1"})
        print lookup.lookup(pos=6500660, args={"chromosome":"1"})
        print lookup.lookup(pos=6501044, args={"chromosome":"1"})
        print lookup.lookup(pos=6520312, args={"chromosome":"1"})
        print lookup.lookup(pos=12058802, args={"chromosome":"1"})
        print lookup.lookup(pos=12062017, args={"chromosome":"1"})
        print lookup.lookup(pos=16360550, args={"chromosome":"1"})
        print lookup.lookup(pos=16370215, args={"chromosome":"1"})
        print lookup.lookup(pos=16371067, args={"chromosome":"1"})
