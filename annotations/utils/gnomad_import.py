import argparse
import gzip
import json
import time

import vcf as pyvcf

from annotations.db_connect import Connection


class GnomAD(Connection):
    TABLE = "VARIANTS"
    INFO_LEN = 1048576
    def __init__(self, *args, **kvargs):
        Connection.__init__(self, *args, **kvargs)
        self.store_info = kvargs.get("store_info", False)
        if (self.dbms == "IRIS"):
            self.table = "gnomad.{}".format(self.TABLE)
        else:
            self.table = "{}.{}".format(self.database, self.TABLE)

        self.columns = {}
        self.vcf_columns = {}
        self.aux_columns = {}
        self.info_columns = {}
        self.insert_sql = None
        self.setup_columns()

    def setup_columns(self):
        if (self.dbms == 'MySQL'):
            info = "text({})".format(self.INFO_LEN)
        else:
            info = "LONGVARCHAR"
        self.vcf_columns = {
            "CHROM":    "varchar(4)",
            "POS":      "INT",
            "ID":       "varchar(20)",
            "REF":      "varchar(512)",
            "ALT":      "varchar(2048)",
            "QUAL":     "real",
            "FILTER":   "varchar(64)",
            "INFO":     info
        }
        self.aux_columns = {
            "SOURCE":   "varchar(1)",
            "POPMAX":   "varchar(3)"
        }

        fields = {
            "AN":"INT",
            "AC":"INT",
            "AF":"real",
            "Hom":"INT"
        }

        ancestries = [
            "AFR",
            "AMR",
            "ASJ",
            "EAS",
            "FIN",
            "NFE",
            "OTH",
            "Male",
            "Female",
            "raw",
            "POPMAX"
        ]

        self.info_columns = {}
        for field in fields:
            for ancestry in ancestries:
                if (field == "Hom" and ancestry in ["POPMAX"]):
                    continue
                column = "{}_{}".format(field, ancestry)
                self.info_columns[column] = fields[field]

        columns = self.vcf_columns.copy()
        columns.update(self.aux_columns)
        columns.update(self.info_columns)
        self.columns = columns

        if (self.store_info):
            self.insert_columns = columns
        else:
            self.insert_columns = columns.copy()
            del self.insert_columns["INFO"]
        self.insert_sql = "INSERT INTO {} ({}) VALUES ({})".format(self.table, ", ".join(self.insert_columns),
                                ", ".join([self.parameter() for c in self.insert_columns]))

    def initialize(self):
        c = self.connection.cursor()
        columns = self.columns

        column_string = ", ".join(["{} {}".format(column, columns[column]) for column in columns])

        if (self.is_table_exist(self.table) > 0):
            sql = "DROP TABLE {}".format(self.table)
            print sql
            c.execute(sql)

        sql = "CREATE TABLE {} ({})".format(self.table, column_string)
        print sql
        c.execute(sql)

        self.create_indices()

    def create_indices(self):
        c = self.connection.cursor()
        c.execute("CREATE UNIQUE INDEX PosIdx On {} (CHROM, POS, SOURCE, REF, ALT)".format(self.table))
        c.execute("CREATE INDEX PosIdx2 On {} (POS, REF, ALT)".format(self.table))
        c.execute("CREATE INDEX RsIdIdx On {} (ID)".format(self.table))
        c.execute("CREATE INDEX SRCIdx On {} (SOURCE)".format(self.table))

    def ingest(self, vcf):
        BATCH_SIZE = 100
        with gzip.open(vcf, "rb") as input:
            print "Ingesting: {}".format(vcf)
            if ("exomes" in vcf):
                source = 'e'
            elif ("genomes" in vcf):
                source ='g'
            else:
                raise Exception("Genomes or Exomes not specified")
            vcf_reader = pyvcf.Reader(input)
            l = 0
            n = 0
            m = 0
            t0 = time.time()
            list_of_values = []
            while (True):
                record = vcf_reader.next()
                if (not record):
                    break
                # CHROM, POS, ID, REF, ALT
                l += 1

                alts = record.ALT
                for i in range(0, len(alts)):
                    try:
                        values = []
                        info = record.INFO
                        for column in self.insert_columns:
                            if (column in self.vcf_columns):
                                v = getattr(record,column)
                                if (type(v) is list):
                                    if (i < len(v)):
                                        v = v[i]
                                    else:
                                        v = None
                                if (column == 'ALT'):
                                    v = v.sequence
                                if (column == 'INFO'):
                                    v = json.dumps(v)
                                    if (len(v) > self.INFO_LEN):
                                        print "WARNING: INFO is too long: {}".format(len(v))
                                        v = v[:self.INFO_LEN]
                                values.append(v)
                            elif (column in self.aux_columns):
                                if (column == "SOURCE"):
                                    values.append(source)
                                elif (column == "POPMAX"):
                                    values.append(info["POPMAX"][i])
                                else:
                                    raise Exception("{} is {}".format(column, v))
                            elif (column in self.info_columns):
                                v = info.get(column)
                                if (v == None):
                                    #raise Exception("{} is {}".format(column, v))
                                    pass
                                if (type(v) is list):
                                    v = v[i]
                                values.append(v)
                            else:
                                raise Exception("{} is {}".format(column, v))

                        try:
                            #cursor.execute(self.insert_sql, tuple(values))
                            list_of_values.append(tuple(values))
                            n += 1
                        except:
                            raise
                    except:
                        raise

                if (l%BATCH_SIZE == 0):
                    m += self.execute_insert(self.insert_sql, list_of_values)
                    del list_of_values[:]
                    if (l % 1000 == 0):
                        t = time.time() - t0
                        print "{} ==> {} [{}]. Time: {}; Rate: {}".format(l, n, m, t, int(m/t))


    def execute_insert(self, sql, list_of_values):
        rowcount = 0
        if (not self.is_connected()):
            self.connect()
        cursor = self.connection.cursor()
        if (len(list_of_values) == 1):
            cursor.execute(sql, list_of_values[0])
            rowcount += cursor.rowcount
        else:
            try:
                cursor.executemany(sql, list_of_values)
                rowcount += cursor.rowcount
            except:
                n = len(list_of_values)
                print ("EXCEPTION ON LIST[{}]".format(n))
                m = n/2
                rowcount += self.execute_insert(sql, list_of_values[0:m])
                rowcount += self.execute_insert(sql, list_of_values[m:n])
        cursor.close()
        return rowcount



if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Import VCF files into gnomAD database")
    parser.add_argument("--files", "-f", "--input", "-i", help="Path to files to import",
                        default=["/opt/data/gnomad/vcf/exomes/gnomad.exomes.r2.0.2.sites.vcf.bgz"],
                        required=False, nargs='+')
    parser.add_argument("--dbms", help="DBMS type to import into", default="MySQL")
    parser.add_argument("--database", help="Database/Namespace", default="gnom1")
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

    connector = GnomAD(args.host, dbms=args.dbms, database=args.database, port=args.port, user=args.user, password=args.password)
    if (args.options):
        for key in args.options:
            option = key.split(':')
            connector.set_option(option[0], option[1])
    connector.connect()
    connector.initialize()
    for file in files:
        connector.ingest(file)

