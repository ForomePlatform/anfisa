import sys
from annotations.db_connect import Connection


class RandomPos(Connection):
    TABLE = "random_pos"
    SQL = "insert into util.random_pos (chrom, Pos) Values ({chromosome}, (SELECT CAST(FLOOR(RAND()*({max}-{min}+1)+{min}) As UNSIGNED)))"

    def __init__(self, host = "anfisa.forome.org:ip-172-31-24-96", *args, **kvargs):
        if (not "database" in kvargs):
            kvargs["database"] = "util"
        if (not "user" in kvargs):
            kvargs["user"] = "hgmd"
        if (not "password" in kvargs):
            kvargs["password"] = "hgmd"
        Connection.__init__(self, host, connect_now=True, *args, **kvargs)
        self.table = "{}.{}".format(self.database, self.TABLE)

    def execute(self, n):
        cursor = self.connection.cursor()
        chromosome = 13
        start = 18445861
        end = 113671678
        sql = self.SQL.format(chromosome = chromosome, min = start, max = end)
        for i in range(0, n):
            cursor.execute(sql)
            if (i%20 == 0):
                print i


if __name__ == '__main__':
    if len(sys.argv) > 1:
        n = int(sys.argv[1])
    else:
        n = 100

    connector = RandomPos()

    connector.connect()
    connector.execute(n)
    connector.close()

    print "Done"