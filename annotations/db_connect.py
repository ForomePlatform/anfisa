import getpass

import mysql.connector
import paramiko
import sshtunnel
import socket
import jaydebeapi
import os

IRIS = [
    "com.intersystems.jdbc.IRISDriver",
    "/Users/misha/intersys/perforce/iris/latest/built/common/java/1.8/intersystems-jdbc/intersystems-jdbc-3.0.0.jar"
]


def host_name():
    return socket.gethostname().lower()


def connect_mysql(port, user, password, database, driver_options):
    connection = mysql.connector.connect(
        host="localhost",
        user=user,
        passwd=password,
        database=database,
        port = port, **driver_options
    )
    return connection


def connect_jdbc(driver, classpath, dbms, port, user, password, database, driver_options):
    url = "jdbc:{dbms}://{host}:{port}/{database}".\
        format(dbms=dbms, host="localhost", port=port, database=database)
    options = {
        "user": user,
        "password": password
    }
    if (driver_options):
        options.update(driver_options)
    connection = jaydebeapi.connect(driver, url, options, classpath)
    return connection


def default_port(dbms):
    if (dbms == "MySQL"):
        return 3306
    if (dbms == "IRIS"):
        return 51773
    return None


def resolve_host(host):
    hosts = host.lower().split(':')
    if (len(hosts) < 2):
        return host
    hostname = host_name().lower()
    if (hostname in hosts[1:]):
        return "localhost"
    return hosts[0]


class Connection:
    def __init__(self, host = "localhost",
            database = None, port = None, user = None,
            password = None, dbms = 'MySQL',
            ssh_user = None, driver = None,
            java_class_path = None, connect_now = False):
        self.tunnel = None
        self.database = database
        self.host = resolve_host(host)
        self.user = user
        self.password = password
        self.dbms = dbms
        self.options = dict()
        if (ssh_user):
            self.ssh_user = ssh_user
        else:
            self.ssh_user = getpass.getuser()
        if (port):
            self.port = port
        else:
            self.port = default_port(dbms)
        if (self.dbms.startswith('jdbc')):
            wrapper = "jdbc"
        else:
            wrapper = None
        if (self.dbms == "IRIS"):
            wrapper = "jdbc"
            if (not driver):
                driver = IRIS[0]
            if (not java_class_path):
                java_class_path = IRIS[1]

        if (self.dbms == "MySQL"):
            self.connect_dbms = connect_mysql
        elif (wrapper == "jdbc"):
            self.connect_dbms = lambda po, u, pswd, db, opt: \
                connect_jdbc(driver, java_class_path, dbms, po, u, pswd, db, opt)
        else:
            raise Exception("Unsupported DBMS: {}".format(self.dbms))
        if (connect_now):
            self.connect()

    def set_option(self, key, value):
        self.options[key] = value

    def connect(self):
        if (self.host == "localhost" or self.host == "127.0.0.1"):
            self.connection = self.connect_dbms(self.port, self.user, self.password, self.database, self.options)
        else:
            self.connection = self.connect_via_tunnel()
        self.connection.autocommit = True

    def get_connection(self):
        if (self.host == "localhost" or self.host == "127.0.0.1"):
            connection = self.connect_dbms(self.port, self.user, self.password, self.database, self.options)
        else:
            connection = self.connect_via_tunnel()
        connection.autocommit = True
        return connection

    def connect_via_tunnel(self):
        host = self.host
        home = os.path.expanduser('~')
        mypkey = paramiko.RSAKey.from_private_key_file(os.path.join(home, ".ssh", "id_rsa"))
        self.tunnel = sshtunnel.SSHTunnelForwarder(
            (host, 22),
            ssh_username=self.ssh_user,
            ssh_pkey=mypkey,
            remote_bind_address=("localhost", self.port)
        )
        self.tunnel.start()
        connection = self.connect_dbms(port=self.tunnel.local_bind_port,
                                       user = self.user,
                                       password = self.password,
                                       database = self.database,
                                       driver_options=self.options)
        # print connection.is_connected()
        return connection

    def is_table_exist(self, table):
        c = self.connection.cursor()

        p = self.parameter()
        t = table.split('.')
        if (len(t) > 1):
            table = t[1]
            schema = t[0]
        else:
            schema = None
        if (self.dbms == 'MySQL'):
            sql = "SELECT table_name FROM information_schema.tables WHERE table_schema = {} AND table_name = {}"
            if (not schema):
                schema = self.database
        elif (self.dbms == "IRIS"):
            sql = "SELECT SqlTableName FROM %Dictionary.CompiledClass WHERE SqlSchemaName = {} AND SqlTableName = {}"
            if (schema == None):
                schema = "SQLUser"

        sql = sql.format(p, p)
        c.execute(sql, (schema, table))
        rows =  c.fetchall()
        exists = len(rows) > 0
        c.close()
        return exists

    def is_connected(self):
        if (self.dbms == 'MySQL'):
            return self.connection and self.connection.is_connected()
        else:
            return self.connection and not self.connection._closed

    def parameter(self):
        if (self.dbms == 'MySQL'):
            return '%s'
        else:
            return '?'

    def quote(self, str):
        if (self.dbms == 'MySQL'):
            return "`{}`".format(str)
        else:
            return '"{}"'.format(str)

    def create_table(self, table, columns):
        c = self.connection.cursor()

        column_string = ", ".join(["{} {}".format(column, columns[column]) for column in columns])

        if (self.is_table_exist(table) > 0):
            sql = "DROP TABLE {}".format(table)
            print sql
            c.execute(sql)

        sql = "CREATE TABLE {} ({})".format(table, column_string)
        print sql
        c.execute(sql)

    def create_index(self, table, name, columns, unique = False):
        c = self.connection.cursor()
        qualifier = "UNIQUE" if unique else ""
        column_string = ",".join(columns)
        sql = "CREATE {q} INDEX {name} ON {table} ({cols})".\
            format(q=qualifier, name = name, table = table, cols = column_string)
        c.execute(sql)

    def close(self):
        if (self.tunnel):
            self.tunnel.stop()
        if (self.is_connected()):
            self.connection.close()

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

    def __enter__(self):
        return self

