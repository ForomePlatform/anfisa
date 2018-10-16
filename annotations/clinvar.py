from annotations.db_connect import Connection


class ClinVar(Connection):
    QUERY_BASE = "SELECT " \
                "`Start`," \
                "`Stop`," \
                "`AlternateAllele`," \
                "`Type`," \
                "ClinicalSignificance," \
                "PhenotypeIDS," \
                "PhenotypeList," \
                "OtherIDs " \
            "FROM clinvar.variant_summary " \
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
        self.query_na = self.QUERY_NA.format(*args[:-1])
        self.query_0 = self.QUERY_0.format(*args[:-1])
        self.query_base = self.QUERY_BASE.format(*args[:-2])

    def exists(self, c, p1):
        rows = self.get_expanded_data(c, p1)
        return len(rows) > 0

    def get_expanded_data(self, c, p1):
        cursor = self.connection.cursor()
        cursor.execute(self.query_base, (c, p1))
        rows = cursor.fetchall()
        return rows

    def get_data(self, c, p1, p2, alt):
        cursor = self.connection.cursor()
        rows = []
        if (not isinstance(alt, list)):
            alt = str(alt).split(',')
        for a in alt:
            cursor.execute(self.query_exact, (c, p1, p2, a))
            rows += cursor.fetchall()
        cursor.execute(self.query_na, (c, p1, p2))
        rows += cursor.fetchall()
        cursor.close()
        if (len(rows) > len(alt)):
            raise Exception("Ambiguous query: c={}, start = {}, end = {}, alt = {}".format(c, p1, p2, a))
        return rows


if __name__ == '__main__':
    with ClinVar("localhost") as clinvar_connector:  ##anfisa.forome.org
        data = clinvar_connector.get_data("15", 38614525, 38614525, "A")
        print data
        data = clinvar_connector.get_data("1", 156104292, 156104292, "A")
        print data
        data = clinvar_connector.get_data("5", 90151630, 90151630, "G")
        print data
        data = clinvar_connector.get_data("10", 92678741, 92678764, "AATATAT,A,AATATATATATATAT")
        print data

