import argparse
import gzip
import time

from annotations.gtf import GTF


class GTF_Import(GTF):

    def __init__(self, *args, **kvargs):
        GTF.__init__(self, *args, **kvargs)
        self.columns = {
            "chromosome":"varchar(4)",
            "source":"varchar(50)",
            "feature":"varchar(50)",
            "start":"INT",
            "end":"INT",
            "score":"FLOAT",
            "strand":"varchar(1)",
            "frame":"INT",
            "attribute":"varchar(2048)",
            "gene":"varchar(64)",
            "biotype":"varchar(64)",
            "exon":"INT",
            "transcript":"varchar(64)"
        }
        self.insert_sql = None

    def initialize(self):
        self.create_table(self.table, self.columns)
        self.create_indices()
        self.insert_sql = "INSERT INTO {} ({}) VALUES ({})".format(self.table, ", ".join(self.COLUMNS),
                                ", ".join([self.parameter() for c in self.COLUMNS]))

    def create_indices(self):
        self.create_index(self.table, "PosIdx",
                          columns=["chromosome", "source", "feature", "start", "end", "strand"],
                          unique=False)
        self.create_index(self.table, "SIdx", columns=["start"])
        self.create_index(self.table, "EIdx", columns=["end"])
        self.create_index(self.table, "FIdx", columns=["feature"])
        self.create_index(self.table, "GIdx", columns=["gene"])
        self.create_index(self.table, "TIdx", columns=["transcript"])

    def ingest(self, gtf):
        print "Ingesting: {}".format(gtf)
        if (gtf.endswith(".gz")):
            with gzip.open(gtf, "rb") as gtf_file:
                self.ingest_stream(gtf_file)
        else:
            with open(gtf, "rb") as gtf_file:
                self.ingest_stream(gtf_file)

    def ingest_stream(self, gtf_stream):
        BATCH_SIZE = 1000
        l = 0
        n = 0
        m = 0
        t0 = time.time()
        list_of_values = []
        for line in gtf_file:
            l += 1
            if (line[0] == '#'):
                continue
            data = line.split('\t')
            c = data[0].strip()
            if (len(c)>4):
                continue
            s = data[1].strip()
            f = data[2].strip()
            p1 = int(data[3].strip())
            p2 = int(data[4].strip())
            score = data[5].strip()
            if (score == '.'):
                score = None
            strand = data[6].strip()
            frame  = data[7].strip()
            if (frame == '.'):
                frame = None
            attr = data[8].strip()

            attr_data = attr.split(';')
            gene = None
            biotype = None
            exon = None
            transcript = None
            for a in attr_data:
                t = a.strip().split(' ')
                key = t[0]
                if (len(t) > 1):
                    v = t[1].strip().strip('"')
                else:
                    v = None
                    continue
                if (key == "gene_name"):
                    gene = v
                elif (key == "exon_number"):
                    exon = int(v)
                elif (key == "gene_biotype"):
                    biotype = v
                elif (key == "transcript_id"):
                    transcript = v
            list_of_values.append((c, s, f, p1, p2, score, strand, frame, attr, gene, biotype, exon, transcript))

            if (l%BATCH_SIZE == 0):
                try:
                    m += self.execute_insert(self.insert_sql, list_of_values)
                except:
                    #print "ERROR: line #{}: {}".format(l, line)
                    raise
                del list_of_values[:]
                if (l % 50000 == 0):
                    t = time.time() - t0
                    print "{} ==> {} [{}]. Time: {}; Rate: {}".format(l, n, m, t, int(m/t))

    def execute_insert(self, sql, list_of_values):
        rowcount = 0
        if (not self.is_connected()):
            self.connect()
        cursor = self.connection.cursor()
        if (len(list_of_values) == 1):
            try:
                cursor.execute(sql, list_of_values[0])
            except:
                raise
            rowcount += cursor.rowcount
        else:
            cursor.executemany(sql, list_of_values)
            rowcount += cursor.rowcount
        cursor.close()
        return rowcount


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Import VCF files into gnomAD database")
    parser.add_argument("--files", "-f", "--input", "-i", help="Path to files to import",
                        default=["/db/data/misc/Homo_sapiens.GRCh37.87.gtf.gz"],
                        required=False, nargs='+')
    parser.add_argument("--dbms", help="DBMS type to import into", default="MySQL")
    parser.add_argument("--database", help="Database/Namespace", default="ensembl")
    parser.add_argument("--host", help="DBMS host", default="localhost")
    parser.add_argument("--port", help="DBMS port, defualt depends on DBMS type")
    parser.add_argument("--user", "-u", help="DBMS user, defualt depends on DBMS type")
    parser.add_argument("--password", "-p", help="DBMS password, defualt depends on DBMS type")
    parser.add_argument("--options", "-o", help="Options to pass to database driver", nargs='*')

    args = parser.parse_args()
    print args

    files = args.files

    if (args.dbms == "MySQL"):
        if (not args.user):
            args.user = "hgmd"
        if (not args.password):
            args.password = "hgmd"
    elif (args.dbms == "IRIS"):
        if (not args.user):
            args.user = "_SYSTEM"
        if (not args.password):
            args.password = "SYS"
    else:
        raise Exception("Unsupported DBMS type: {}".format(args.dbms))

    connector = GTF_Import(args.host, dbms=args.dbms, database=args.database, port=args.port, user=args.user, password=args.password)
    if (args.options):
        for key in args.options:
            option = key.split(':')
            connector.set_option(option[0], option[1])
    connector.connect()
    connector.initialize()
    for file in files:
        connector.ingest(file)
