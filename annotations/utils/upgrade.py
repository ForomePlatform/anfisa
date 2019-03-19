import codecs
import datetime
import json
import os
import shutil
import sys


annotation_server="anfisa.forome.org"
aws_user = "misha"


def annotate_all(config):
    for workspace in config["workspaces"]:
        annotate(workspace)


def annotate (workspace):
    f = workspace["file"]
    case = workspace["mongo-name"]
    remote = "{aws_user}@{annotation_server}".format(annotation_server=annotation_server, aws_user=aws_user)
    remote_dir = "/data/bgm/cases/{}".format(case)
    cmd = "export PYTHONPATH=/data/bgm/anfisa ; cd {remote_dir} ; python -m annotations.annotator ".format(remote_dir=remote_dir)
    cmd = "{base} -i {case_id}_seq_a_boo_regions.vep.json ".format(base=cmd,case_id=case)
    print "Running {cmd} on ${annotation_server}".format(cmd=cmd, annotation_server=annotation_server)
    ssh = "ssh -t {remote} {cmd}".format(cmd=cmd, remote=remote)
    print ssh
    os.system(ssh)
    scp = "scp {remote} {local}".format(remote=remote, local=f)
    print scp
    os.system(scp)


def load():
    pass


def loadJSonConfig(config_file):
    with codecs.open(config_file, "r", encoding = "utf-8") as inp:
        content = inp.read()
    dir_name = os.path.abspath(__file__)
    for idx in range(2):
        dir_name = os.path.dirname(dir_name)
    content = content.replace('${HOME}', dir_name)
    pre_config = json.loads(content)

    file_path_def = pre_config.get("file-path-def")
    if file_path_def:
        for key, value in file_path_def.items():
            assert key != "HOME"
            content = content.replace('${%s}' % key, value)
    return json.loads(content)



def copy_data(config):
    updated_config = config.copy()
    dirname = "data"
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
    updated_config = copy_data(config)
    with open(config_file + ".new", "w") as c:
        json.dump(updated_config, c)

    annotate_all(config)