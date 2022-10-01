#  Copyright (c) 2019. Partners HealthCare and other members of
#  Forome Association
#
#  Developed by Sergey Trifonov based on contributions by Joel Krier,
#  Michael Bouzinier, Shamil Sunyaev and other members of Division of
#  Genetics, Brigham and Women's Hospital
#
#  Licensed under the Apache License, Version 2.0 (the "License");
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
#
#        http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.
#
import tarfile, io, os, logging, json, shutil
from copy import deepcopy

from forome_tools.log_err import logException
#===============================================
def jsDataToTar(tar, name, data):
    f_info = tarfile.TarInfo(name = name)
    dump = json.dumps(data, ensure_ascii = False, sort_keys = True,
        indent = 4).encode("utf-8")
    f_info.size = len(dump)
    tar.addfile(f_info, io.BytesIO(dump))

#===============================================
def exportWS(ds_h, with_support, with_root_doc):
    assert ds_h.getDSKind() == "ws", "Wrong dataset kind"
    logging.info(f"exportWS: {ds_h.getName()}")
    export_dir = ds_h.getApp().prepareExportDir()
    ds_dir = ds_h.getDirPath() + "/"
    ds_info = ds_h.getDataInfo()
    support_data = None
    root_doc_dir = None

    if with_root_doc:
        root_name = ds_h.getRootDSName()
        root_ds_h = ds_h.getDataVault().getDS(root_name)
        if root_ds_h is not None:
            if "doc" not in root_ds_h.getDataInfo():
                logging.warning(
                    f"No doc root dataset {root_name}, root documents ignored")
            else:
                ds_info = deepcopy(ds_info)
                ds_info["doc"] = root_ds_h.getDataInfo()["doc"]
                root_doc_dir = root_ds_h.getDirPath() + "/doc/"
        else:
            logging.warning(
                f"No root dataset {root_name}, root documents ignored")

    if with_support:
        support_data = {
            "mongo": ds_h.getSolEnv().dumpAll(),
            "note": ds_h.getMongoAgent().getNote()[0]}

    out_name = ds_h.getName() + ".tgz"

    with tarfile.open(export_dir + "/" + out_name, "w:gz") as tar:
        for fname in ("fdata.json.gz", "pdata.json.gz",
                "vdata.ixbz2", "doc/info.html"):
            tar.add(ds_dir + fname, arcname = fname)
        for fname in ("stat.json"):
            if os.path.exists(ds_dir + fname):
                tar.add(ds_dir + fname, arcname = fname)

        if os.path.exists(ds_dir + "stat.json"):
            tar.add(ds_dir + "stat.json", arcname = "stat.json")
        jsDataToTar(tar, "dsinfo.json", ds_info)
        if support_data is not None:
            jsDataToTar(tar, "support.json", support_data)
        if root_doc_dir is not None:
            for fname in os.listdir(root_doc_dir):
                if fname == "info.html":
                    continue
                tar.add(root_doc_dir + fname, arcname = "doc/" + fname)

    return {"kind": "tar.gz", "url": "excel/" + out_name}

#===============================================
def importWS(vault_h, ds_name, tar_content):
    ds_dir = vault_h.getDir() + "/" + ds_name
    if os.path.exists(ds_dir):
        return {"error": f"Directory {ds_dir} already exists"}

    with tarfile.open(fileobj = io.BytesIO(tar_content), mode = "r:gz") as tar:
        member_names = set(tar.getnames())

        for fname in ("fdata.json.gz", "pdata.json.gz", "dsinfo.json",
                "vdata.ixbz2", "doc/info.html"):
            if fname not in member_names:
                return {
                    "error": f"Bad dataset archive: file {fname} is required"}
        os.mkdir(ds_dir)
        
        import os
        
        def is_within_directory(directory, target):
            
            abs_directory = os.path.abspath(directory)
            abs_target = os.path.abspath(target)
        
            prefix = os.path.commonprefix([abs_directory, abs_target])
            
            return prefix == abs_directory
        
        def safe_extract(tar, path=".", members=None, *, numeric_owner=False):
        
            for member in tar.getmembers():
                member_path = os.path.join(path, member.name)
                if not is_within_directory(path, member_path):
                    raise Exception("Attempted Path Traversal in Tar File")
        
            tar.extractall(path, members, numeric_owner) 
            
        
        safe_extract(tar, path=ds_dir)

    try:
        with open(ds_dir + "/dsinfo.json", "r", encoding = "utf-8") as inp:
            ds_info = json.loads(inp.read())
    except Exception:
        logException("Upload archive: bad dsinfo.json")
        shutil.rmtree(ds_dir)
        return {"error": "Incorrect dataset info"}

    ds_info["name"] = ds_name
    ds_info["root"] = ds_name
    ds_info["mongo"] = ds_name
    if "base" in ds_info:
        del ds_info["base"]
    with open(ds_dir + "/dsinfo.json", "w", encoding = "utf-8") as outp:
        outp.write(json.dumps(ds_info, ensure_ascii = False, sort_keys = True,
            indent = 4))

    support_path = ds_dir + "/support.json"
    if os.path.exists(support_path):
        with open(support_path, "r", encoding = "utf-8") as inp:
            support_data = json.loads(inp.read())
    mongo_agent = vault_h.getApp().getMongoConnector().getPlainAgent(ds_name)
    mongo_agent.delete_many({})
    mongo_agent.insert_many(support_data["mongo"])
    vault_h.getApp().getMongoConnector().getDSAgent(ds_name, "ws").setNote(
        support_data["note"])
    with open(ds_dir + "/active", "w", encoding = "utf-8") as outp:
        print("", file = outp)

    return {"created": ds_name}
