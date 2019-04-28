import datetime
import json
import os
import copy
import shutil
import sys

from annotations.annotator import get_md
from annotations.record import Variant
from app import storage
from utils import loadJSonConfig


annotation_server="anfisa.forome.org"
aws_user = "misha"


def annotate_all(config):
    for workspace in config["workspaces"]:
        annotate(workspace)


def import_all(config):
    app_config = loadJSonConfig("anfisa.json")
    for workspace in config["workspaces"]:
        load(app_config, workspace)


def annotate (workspace):
    f = workspace["file"]
    metadata = get_md(f)
    if (metadata):
        version = Variant.get_version()
        old_version = metadata["versions"]["annotations"]
        if (old_version == version):
            print "Case is already annotated with the same version"
            return
    case = workspace["mongo-name"]
    fname = os.path.basename(f)
    casedir = os.path.dirname(f)
    path = casedir.split('/')
    case_full_id = None
    for p in path:
        if (case in p):
            case_full_id = p
            break
    if (not case_full_id):
        case_full_id = "{}_wgs".format(case)
    if (not case in fname):
        print "Skipping non-standard case: {}".format(fname)
        return

    remote = "{aws_user}@{annotation_server}".format(annotation_server=annotation_server, aws_user=aws_user)
    remote_dir = "/data/bgm/cases/{}".format(case)
    cmd = "export PYTHONPATH=/data/bgm/anfisa ; cd {remote_dir} ; python -m annotations.annotator ".format(remote_dir=remote_dir)
    cmd = "{base} -i {case_id}_seq_a_boo_regions.vep.json ".format(base=cmd,case_id=case_full_id)
    print "Running {cmd} on ${annotation_server}".format(cmd=cmd, annotation_server=annotation_server)
    ssh = 'ssh -t {remote} "{cmd}"'.format(cmd=cmd, remote=remote)
    print ssh
    ret = os.system(ssh)
    if (ret):
        raise Exception("Returned {}".format(ret))
    result = "{}/{}_anfisa.json".format(remote_dir, case)
    scp = "scp {remote}:{result} {local}".format(remote=remote, local=f, result=result)
    print scp
    ret = os.system(scp)
    if (ret):
        raise Exception("Returned {}".format(ret))


def load(config, workspace):
    f = workspace["file"]
    case = workspace["mongo-name"]
    fname = os.path.basename(f)
    if (not case in fname):
        print "Skipping non-standard case: {}".format(fname)
        return
    print "Importing: {}".format(case)
    storage.dropDataSet(config, case, "ws", False)
    storage.createDataSet(config, case, "ws", case, f, 100)

def copy_data(config, dest):
    updated_config = copy.deepcopy(config)
    dirname = os.path.join(dest,"data")
    if (os.path.isdir(dirname)):
        now = str(datetime.datetime.now()).replace(' ', '_').replace(':','-')
        os.rename(dirname, "{}.{}".format(dirname, now))
    os.mkdir(dirname)

    for workspace in updated_config["workspaces"]:
        f = workspace["file"]
        shutil.copy(f, dirname)
        fname = os.path.basename(f)
        workspace["file"] = os.path.join("${DATA}", fname)

    updated_config["file-path-def"]["DATA"] = os.path.abspath(dirname)
    return updated_config


if __name__ == '__main__':
    if len(sys.argv) > 1:
        config_file = sys.argv[1]
    else:
        config_file = "anfisa.json"

    config = loadJSonConfig(config_file)
    updated_config = copy_data(config, os.path.dirname(config_file))
    with open(config_file + ".new", "w") as c:
        json.dump(updated_config, c, indent=2)

    annotate_all(config)
    import_all(config)
