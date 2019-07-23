import os
import mysql.connector
import paramiko
import sshtunnel

from annotations import host_name


def connect(port = 3306, user = "hgmd", password = "hgmd"):
    connection = mysql.connector.connect(
        host="localhost",
        user=user,
        passwd=password,
        database="hgmd_pro",
        port = port
    )
    return connection




class HGMD:
    SQL_ACC_NUM = "select acc_num from `hgmd_pro0`.`hg19_coords`  where chromosome = %s and coordSTART = %s and coordEND = %s"
    SQL_PMID = "SELECT distinct disease, PMID, Tag from hgmd_pro0.mutation where acc_num = %s"
    SQL_PHEN = "SELECT distinct phenotype " + \
               "FROM hgmd_phenbase0.hgmd_mutation as m join hgmd_phenbase0.hgmd_phenotype as p on p.phen_id = m.phen_id " + \
               "WHERE acc_num = %s"
    SQL_HG38 = "SELECT coordSTART, coordEND FROM `hgmd_pro0`.`hg38_coords` WHERE acc_num = %s"

    def __init__(self):
        self.tunnel = None
        hostname = host_name()
        if ("ip-172-31-24-96" in hostname):
            self.connection = connect()
        else:
            #self.connection = connect()
            self.connection = self.connect_via_tunnel()

    def connect_via_tunnel(self):
        host = "anfisa.forome.org"
        home = os.path.expanduser('~')
        mypkey = paramiko.RSAKey.from_private_key_file(os.path.join(home, ".ssh", "id_rsa"))
        self.tunnel = sshtunnel.SSHTunnelForwarder(
            (host, 22),
            ssh_username="misha",
            ssh_pkey=mypkey,
            remote_bind_address=("localhost", 3306)
        )
        self.tunnel.start()
        connection = connect(port=self.tunnel.local_bind_port)
        # print connection.is_connected()
        return connection

    def get_acc_num(self, chromosome, pos_start, pos_end):
        cursor = self.connection.cursor()
        cursor.execute(HGMD.SQL_ACC_NUM, (chromosome, pos_start, pos_end))
        rows = [row[0] for row in cursor]
        cursor.close()
        return rows

    def get_hg38(self, acc_numbers):
        cursor = self.connection.cursor()
        rows = []
        for acc_num in acc_numbers:
            cursor.execute(HGMD.SQL_HG38, [acc_num])
            rows += [row for row in cursor]
        cursor.close()
        return rows

    def get_data(self, chromosome, pos_start, pos_end):
        acc_numbers = self.get_acc_num(chromosome, pos_start, pos_end)
        return self.get_data_for_accession_numbers(acc_numbers)

    def get_data_for_accession_numbers(self, acc_numbers):
        cursor1 = self.connection.cursor()
        cursor2 = self.connection.cursor()

        phenotypes = []
        pmids = []
        for acc_num in acc_numbers:
            # print acc_num
            cursor1.execute(HGMD.SQL_PMID, [acc_num])
            pmids += [row for row in cursor1]
            cursor2.execute(HGMD.SQL_PHEN, [acc_num])
            phenotypes += [row for row in cursor2]

        cursor1.close()
        cursor2.close()
        return (phenotypes, pmids)

    def is_connected(self):
       return self.connection and self.connection.is_connected()

    def close(self):
        if (self.tunnel):
            self.tunnel.stop()
        if (self.is_connected()):
            self.connection.close()

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

    def __enter__(self):
        return self


if __name__ == '__main__':
    with HGMD() as hgmd_connector:
        data = hgmd_connector.get_data("1", 216062306, 216062306)

    print data