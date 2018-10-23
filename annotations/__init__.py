import os
import socket


def host_name():
    return socket.gethostname().lower()

def data_path():
    path_to_data = None
    hostname = host_name()
    if ("misha" in hostname):
        path_to_data = "/opt/data/"
    elif ("partners.org" in hostname):
        path_to_data = "/net/bgm/resources/"
    else:
        uname = os.uname()
        if ('aws' in uname[2].lower()):
            path_to_data = "/db/data/"
    return path_to_data


def gnomAD_path():
    path_to_gnomad_data = os.path.join(data_path(),"gnomad","db")
    return path_to_gnomad_data