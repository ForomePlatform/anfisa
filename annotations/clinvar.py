from annotations.db_connect import Connection


class ClinVar(Connection):
    SUBMITTER_QUERY = "SELECT SubmitterName, ClinicalSignificance FROM `clinvar`.`CV_Submitters` NATURAL JOIN `clinvar`.`ClinVar2Sub_Sig` WHERE RCVaccession IN ({})"

    QUERY_BASE = "SELECT " \
                "`Start`," \
                "`Stop`," \
                "`AlternateAllele`," \
                "`Type`," \
                "ClinicalSignificance," \
                "PhenotypeIDS," \
                "PhenotypeList," \
                "OtherIDs, " \
                "RCVaccession " \
            "FROM clinvar.variant_summary AS v " \
            "WHERE " \
                "Assembly = 'GRCh37' AND " \
                "Chromosome={} AND " \
                "Start = {} "

    QUERY_0 = QUERY_BASE + " AND Stop = {} "
    QUERY = QUERY_0 + "AND (AlternateAllele = {} OR AlternateAllele = 'na')"
    QUERY_EXACT = QUERY_0 + " AND AlternateAllele = {}"
    QUERY_NA = QUERY_0 + " AND AlternateAllele = 'na'"

    def __init__(self, host = "anfisa.forome.org:ip-172-31-24-96"):
        Connection.__init__(self, host, database="clinvar", user="hgmd", password='hgmd', connect_now=True)
        n = len(self.QUERY.split("{}")) - 1
        p = self.parameter()
        args = [p for i in range(0, n)]
        self.query_exact = self.QUERY_EXACT.format(*args)
        ## print self.query_exact
        self.query_na = self.QUERY_NA.format(*args[:-1])
        self.query_0 = self.QUERY_0.format(*args[:-1])
        self.query_base = self.QUERY_BASE.format(*args[:-2])

    def get_submitters(self, row):
        rcv_accessions = row[-1].split(';')
        args = ','.join(["'{}'".format(arg) for arg in rcv_accessions])
        cursor = self.connection.cursor()
        cursor.execute(self.SUBMITTER_QUERY.format(args))
        submitters = {s[0]: s[1] for s in cursor.fetchall()}
        return tuple(list(row[0:-1]) + [submitters])

    def add_submitters_to_rows(self, rows):
        if (len(rows) < 1):
            return rows
        return [self.get_submitters(row) for row in rows]

    def exists(self, c, p1):
        rows = self.get_expanded_data(c, p1)
        return len(rows) > 0

    def get_expanded_data(self, c, p1):
        cursor = self.connection.cursor()
        cursor.execute(self.query_base, (c, p1))
        rows = cursor.fetchall()
        return self.add_submitters_to_rows(rows)

    def get_data(self, c, p1, p2, alt):
        cursor = self.connection.cursor()
        rows = []
        if (not isinstance(alt, list)):
            alt = str(alt).split(',')
        for a in alt:
            cursor.execute(self.query_exact, (c, p1, p2, a))
            rows += cursor.fetchall()
        if (len(rows) == 0):
            cursor.execute(self.query_na, (c, p1, p2))
            rows = cursor.fetchall()
        cursor.close()
        if (len(rows) > len(alt)):
            raise Exception("Ambiguous query: c={}, start = {}, end = {}, alt = {}".format(c, p1, p2, a))
        return self.add_submitters_to_rows(rows)


if __name__ == '__main__':
    with ClinVar() as clinvar_connector:  ##anfisa.forome.org
        data = clinvar_connector.get_data("15", 38614525, 38614525, "A")
        print data
        data = clinvar_connector.get_data("1", 156104292, 156104292, "A")
        print data
        data = clinvar_connector.get_data("5", 90151630, 90151630, "G")
        print data
        data = clinvar_connector.get_data("10", 92678741, 92678764, "AATATAT,A,AATATATATATATAT")
        print data

