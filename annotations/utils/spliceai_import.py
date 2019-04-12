# -*- coding: UTF-8 -*-
import argparse
import gzip
import json
import time
import sys

import vcf as pyvcf

from annotations.spliceai import SpliceAI

class SpliceAI_Import(SpliceAI):
    TABLE = "SPLICEAI"      #
    INFO_LEN = 1048576

    DS_list = ['DS_AG', 'DS_AL','DS_DG','DS_DL']

    def __init__(self, *args, **kvargs):
        SpliceAI.__init__(self, *args, **kvargs)
        self.table = "{}.{}".format(self.database, self.TABLE)

        self.columns = {}
        self.vcf_columns = {}
        self.insert_sql = None
        self.setup_columns()

    def setup_columns(self):

        self.vcf_columns = {
            "CHROM":    "varchar(4)",
            "POS":      "INT",
            "ID":       "varchar(20)",
            "REF":      "varchar(512)",
            "ALT":      "varchar(2048)"
        }
        
        self.info_columns = {
             'DP_AG':   "INT",
             'DP_AL':   "INT",
             'DP_DG':   "INT",
             'DP_DL':   "INT",
             'DS_AG':   "FLOAT",
             'DS_AL':   "FLOAT",
             'DS_DG':   "FLOAT",
             'DS_DL':   "FLOAT",
             'SYMBOL':  "varchar(20)",
             'TYPE' :   "varchar(1)",
             'STRAND':  "varchar(1)"
        }
        
        self.max_columns = {
             'MAX_DS':   "FLOAT"
        }        
        
        columns = self.vcf_columns.copy()
        columns.update(self.info_columns)
        columns.update(self.max_columns)
        self.columns = columns

        self.insert_sql = "INSERT INTO {} ({}) VALUES ({})".format(self.table, 
            ", ".join(self.columns),
            ", ".join([self.parameter() for c in self.columns]))

    def initialize(self):
        if not self.is_table_exist(self.table):
            self.create_table(self.table, self.columns)
            self.create_indices()

    def create_indices(self):
        self.create_index(self.table, "PosIdx", 
            columns=["CHROM", "POS", "REF", "ALT"])  #, unique=True)
        self.create_index(self.table, "PosIdx2", columns=["POS", "REF", "ALT"])
        self.create_index(self.table, "RsIdIdx", columns=["ID"])

    def _record_values(self,record):
        values = []
        info = record.INFO
        for column in self.columns:
            if (column in self.vcf_columns):
                v = getattr(record,column)    # тут вопрос с ALT, он остался списком
                if column == 'ALT':
                    if len(v)>1:
                        print >> sys.stderr, 'longALT:', repr(v)        
                    assert len(v)==1
                    v=str(v[0])
                    # print >> sys.stderr, 'v=', repr(v)
                    
                values.append(v)
            elif (column in self.info_columns):
                v = info[column]
                values.append(v)
            elif (column in self.max_columns):
                v = max(info[key] for key in self.DS_list)
                values.append(v)
            else:
                raise Exception("{} is {}".format(column, v))
        return values

    def ingest(self, vcf):
        BATCH_SIZE = 1000
       # with gzip.open(vcf, "rb") as input:
        print "Ingesting: {}".format(vcf)
        vcf_reader = pyvcf.Reader(filename = vcf,compressed = True)# '/home/trosman/work/whole_genome_filtered_spliceai_scores1000.vcf.gz' 
        #vcf_reader = pyvcf.Reader(input)
        t0 = time.time()
        list_of_values = []
        total, cnt = 0, 0
        for record in vcf_reader:
            # print >> sys.stderr,'len(list_of_values) = {}'.format(len(list_of_values))
            #record = vcf_reader.next()
            #if (not record):
              #  break 
            try:
                values = self._record_values(record)
                list_of_values.append(values)
            except:
                raise
            if len(list_of_values) >= BATCH_SIZE:
                total += self.execute_insert(self.insert_sql, list_of_values) 
                list_of_values = []
                cnt += 1
                if cnt >= 10:
                    cnt = 0
                    dt = time.time() - t0
                    print "Records: {} Time: {}; Rate: {:.2f}".format(total, dt, total / (dt + .0001))
        if len(list_of_values) > 0:
            total += self.execute_insert(self.insert_sql, list_of_values)
        dt = time.time() - t0
        print "Done: Records {} Time: {}; Rate: {:.2f}".format(total, dt, total / (dt + .0001))
        
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
    parser = argparse.ArgumentParser(description="Import VCF files into spliceai database")
    parser.add_argument("--files", "-f", "--input", "-i", help="Path to files to import",
                        default=["/opt/data/gnomad/vcf/exomes/gnomad.exomes.r2.0.2.sites.vcf.bgz"],
                        required=False, nargs='+')
    parser.add_argument("--database", help="Database/Namespace", default="spliceai")
    parser.add_argument("--host", help="DBMS host", default="localhost")
    parser.add_argument("--port", help="DBMS port, defualt depends on DBMS type",default = '3306')  #принудительная вписка default
    parser.add_argument("--user", "-u", help="DBMS user, defualt depends on DBMS type",default = 'hgmd')  #принудительная вписка default
    parser.add_argument("--password", "-p", help="DBMS password, defualt depends on DBMS type", default = 'hgmd') #принудительная вписка default
    parser.add_argument("--options", "-o", help="Options to pass to database driver", nargs='*')

    args = parser.parse_args()
    print args

    files = args.files

    if (not args.user):
        args.user = "hgmd"
    if (not args.password):
        args.password = "hgmd"

    connector = SpliceAI_Import(args.host, dbms="MySQL", database=args.database,       
        port=args.port, user=args.user, password=args.password)
    if (args.options):
        for key in args.options:
            option = key.split(':')
            connector.set_option(option[0], option[1])
    connector.connect()
    connector.initialize()
    for file in files:
        connector.ingest(file)

