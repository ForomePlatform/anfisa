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

import os, re, logging
from glob import glob

#===============================================
class MirrorUiDirectory:
    sFileTab = None

    @classmethod
    def transform(cls, name):
        if cls.sFileTab is not None:
            return cls.sFileTab.get(name, name)
        return name

    sRegExpSrcFName = re.compile("^[\w_]+\.\w+$")
    sRegExpDestFName = re.compile("(^[\w_]+)\-(\d\d\d)(\.\w+)$")

    @classmethod
    def setup(cls, config_data):
        if config_data is None:
            return
        dir_src, dir_dest = config_data
        if not os.path.isdir(dir_dest):
            logging.warning("No destination directory for mirror-ui found.\n"
                "Attempt to create: " + dir_dest)
            os.mkdir(dir_dest)
        fnames_sheet = dict()
        for fpath in glob(dir_src + "/*.*"):
            fname = fpath.rpartition('/')[2]
            if cls.sRegExpSrcFName.match(fname) is not None:
                fnames_sheet[fname] = []
        cls.sFileTab = dict()
        extra_files = []
        count_keep, count_update = 0, 0
        for fpath in glob(dir_dest + "/*.*"):
            fname = fpath.rpartition('/')[2]
            f_m = cls.sRegExpDestFName.match(fname)
            if f_m is not None:
                src_name = f_m.group(1) + f_m.group(3)
                if src_name in fnames_sheet:
                    fnames_sheet[src_name].append(int(f_m.group(2)))
                    continue
            extra_files.append(fname)
        for fname, versions in fnames_sheet.items():
            ver = None
            with open(dir_src + "/" + fname, "rb") as inp:
                src_content = inp.read()
            if len(versions) > 1:
                ver = max(versions)
                for v in versions:
                    if v != ver:
                        extra_files.append(cls.getVerName(fname, v))
            elif len(versions) == 1:
                ver = versions[0]
            if ver is not None:
                dest_fname = cls.getVerName(fname, ver)
                with open(dir_dest + "/" + dest_fname, "rb") as inp:
                    dest_content = inp.read()
                if src_content == dest_content:
                    count_keep += 1
                    cls.sFileTab[fname] = dest_fname
                    continue
                extra_files.append(dest_fname)
                ver += 1
                if ver >= 1000:
                    ver = 0
            else:
                ver = 0
            dest_fname = cls.getVerName(fname, ver)
            with open(dir_dest + "/" + dest_fname, "wb") as outp:
                outp.write(src_content)
            cls.sFileTab[fname] = dest_fname
            count_update += 1
        for fname in extra_files:
            full_name = dir_dest + '/' + fname
            logging.warning("Mirror dir EXTRA FILE!: " + full_name)
            os.remove(full_name)
        logging.info("Mirror dir started (kept %d, updated %d): %s -> %s" %
            (count_keep, count_update, dir_src, dir_dest))

    @staticmethod
    def getVerName(fname, ver):
        nm, q, ext = fname.partition('.')
        return "%s-%03d.%s" % (nm, ver, ext)
