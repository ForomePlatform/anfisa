# -*- coding: UTF-8 -*-
from annotations import positions
from annotations.db_connect import Connection


class SpliceAI(Connection):
    

    TABLE = "spliceai.SPLICEAI"
    KEY_COLUMNS = [
            "CHROM",
            "POS",
            "REF",
            "ALT"
    ]
    
    TARGET_COLUMNS = [
            'SYMBOL',
            'STRAND',
            'TYPE',
            'DP_AG',
            'DP_AL',
            'DP_DG',
            'DP_DL',
            'DS_AG',
            'DS_AL',
            'DS_DG',
            'DS_DL',
            'ID',
            'MAX_DS'
                ]
            
    COLUMNS = KEY_COLUMNS + TARGET_COLUMNS
    def spliceai_data_version(self):
        vsql = "SELECT version FROM VERSION"
        v = self.connection.cursor()
        v.execute(vsql)
        version = v.fetchall()
        return version[0][0]
        
    def get_all(self, chrom, pos, ref, alt_list):
        assert len(alt_list) > 0
        table=self.TABLE 
        dict_sql = {}
        max_ds = None
        select_list = ', '.join(self.COLUMNS)
        alt_values = ', '.join(["\'" + alt + "\'" for alt in alt_list])
        sql = "SELECT {} FROM {} WHERE CHROM = \'{}\' AND POS = {} AND REF = \'{}\' AND ALT IN ({}) ".\
        format(select_list, table, chrom, pos, ref, alt_values)
        c = self.connection.cursor()
        c.execute(sql)
        rows = c.fetchall()
        
        if len(rows)==0:
            case  = 'None'
        else:
            max_ds = max([max_dsi[16] for max_dsi in rows])
            if max_ds < 0.2:
                case  = 'unlikely'
            elif max_ds < 0.5:
                case  = 'likely_pathogenic'
            elif max_ds < 0.8:
                case  = 'pathogenic'
            elif max_ds <= 1.0:
                case  = 'high_precision_pathogenic' 
            for row in rows:
                dict_sql["{}/{}/{}/{}".format(row[3],row[4],row[5],row[6])] = {self.COLUMNS[i] :  row[i] for i in range(7,15)}
            
        return dict_sql, case, max_ds 
        


    def __init__(self, host = "localhost",  #   имя боевого хоста "anfisa.forome.org:ip-172-31-24-96"
            database = "spliceai", port = None, user = "hgmd",
            password = "hgmd", dbms = "MySQL",
            ssh_user = None, driver = None,
            java_class_path = None, connect_now = True):
        Connection.__init__(self, host = host,
            database = database, port = port, user = user,
            password = password, dbms = dbms,
            ssh_user = ssh_user, driver = driver,
            java_class_path = java_class_path, connect_now = connect_now)


if __name__ == '__main__':
    with SpliceAI() as SpliceAI:
        a, b, c = SpliceAI.get_all(10, 92897, 'A', 'C')
        print a, b , c
        ver = SpliceAI.spliceai_data_version()
        print 'version spliceai = {}'.format(ver)
