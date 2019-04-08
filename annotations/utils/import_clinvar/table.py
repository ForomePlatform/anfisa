import logging, time
from annotations.db_connect import Connection

class Table( Connection ) :
    def __init__( self, host = None, database = None, port = None, user = None, 
            password = None, table = None, dbms = None, ssh_user = None, 
            driver = None, java_class_path = None, connect_now = True,
            columns = None, types = None, indexes = None,
             create = False, drop = False ) :
        Connection.__init__( self, host = host,
            database = database, port = port, user = user,
            password = password, dbms = dbms,
            ssh_user = ssh_user, driver = driver,
            java_class_path = java_class_path, connect_now = connect_now )
        self.table = table
        self.columns = columns
        self.types = types
        self.indexes = indexes
        self.drop = drop
        self.insert_sql = "INSERT INTO {} ({}) VALUES ({})".format( self.table, 
                ", ".join( [ self.quote( c ) for c in self.columns ] ), 
                ", ".join( [ self.parameter( ) for c in self.columns ] ) 
                )
        self.logger = logging.getLogger( 'clinvar.Connect' )
        if connect_now and create :
            self.create_table()
            self.create_index()

    def create_table( self ) :
        c = self.connection.cursor()
        column_string = ", ".join( ["{} {}".format( self.quote( column ), type_ )
                                    for column, type_ in zip( self.columns, self.types ) ] 
                                )
        if ( self.is_table_exist( self.table ) > 0 ) :
            if self.drop :
                sql = "DROP TABLE {}".format( self.table )
            else :
                table_old = self.table + '_OLD'
                if ( self.is_table_exist( table_old ) > 0 ) :
                    sql = "DROP TABLE {}".format( table_old )
                    self.logger.debug( sql )
                    c.execute( sql )
                sql = "RENAME TABLE {} TO {}".format( self.table, table_old )
            self.logger.debug(sql)
            c.execute( sql )
        sql = "CREATE TABLE {} ({})".format( self.table, column_string )
        self.logger.debug( sql )
        c.execute( sql )

    def create_index( self ) :
        for i in self.indexes :
            c = self.connection.cursor( )
            qualifier       = "UNIQUE" if i[2] else ""
            btree           = "USING BTREE" if i[3] else ""
            column_string   = ",".join( [ self.quote( cl ) for cl in i[1] ] )
            sql             = "CREATE {q} INDEX {name} ON {table} ({cols}) {ubt}".format(
                                q = qualifier, name = self.quote( i[0] ), table = self.table,
                                cols = column_string, ubt = btree )
            self.logger.debug( sql )
            c.execute( sql )

    def insert ( self, batch ) :
        rowcount = 0
        if ( not self.is_connected( ) ) :
            self.connect( )
        cursor = self.connection.cursor( )
        if ( len( batch ) == 1 ):
            cursor.execute( self.insert_sql, batch[0] )
            rowcount += cursor.rowcount
        else:
            cursor.executemany( self.insert_sql, batch  )
            rowcount += cursor.rowcount
        cursor.close()
        return rowcount

        
