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


def connect_mysql(port, user, password, database):
    connection = mysql.connector.connect(
        host="localhost",
        user=user,
        passwd=password,
        database=database,
        port = port
    )
    return connection


def connect_jdbc(driver, classpath, dbms, port, user, password, database):
    url = "jdbc:{dbms}://{host}:{port}/{database}".\
        format(dbms=dbms, host="localhost", port=port, database=database)
    connection = jaydebeapi.connect(driver, url, [user, password], classpath)
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
    def __init__(self, host = "localhost", database = None, port = None, user = None,
                 password = None, dbms = 'MySQL', ssh_user = None, driver = None, java_class_path = None):
        self.tunnel = None
        self.database = database
        self.host = resolve_host(host)
        self.user = user
        self.password = password
        self.dbms = dbms
        if (ssh_user):
            self.ssh_user = ssh_user
        else:
            self.ssh_user = getpass.getuser()
        if (port):
            self.port = port
        else:
            self.port = default_port(dbms)
        if (self.dbms == "MySQL"):
            self.connect_dbms = connect_mysql
        elif (self.dbms.startswith('jdbc')):
            self.connect_dbms = lambda port, user, password, database: \
                connect_jdbc(driver, java_class_path, self.port, self.user, self.password, self.database)
        self.connect()

    def connect(self):
        if (self.host == "localhost" or self.host == "127.0.0.1"):
            self.connection = self.connect_dbms(self.port, self.user, self.password, self.database)
        else:
            self.connection = self.connect_via_tunnel()
        self.connection.autocommit = True

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
                                       database = self.database)
        # print connection.is_connected()
        return connection

    def is_table_exist(self, schema, table):
        c = self.connection.cursor()

        p = self.parameter()
        if (self.dbms == 'MySQL'):
            sql = "SELECT table_name FROM information_schema.tables WHERE table_schema = {} AND table_name = {}"
        else:
            sql = "SELECT SqlTableName FROM %Dictionary.CompiledClass WHERE SqlSchemaName = {} AND SqlTableName = {}"

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

    def close(self):
        if (self.tunnel):
            self.tunnel.stop()
        if (self.is_connected()):
            self.connection.close()

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

    def __enter__(self):
        return self

