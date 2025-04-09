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

import sys, os, shutil, traceback
from glob import glob
from html import escape

from .html_report import startHtmlReport
#===============================================
def prepareDocDir(ds_doc_dir, ds_inventory, reset = False):
    files_reg = _FileRegistry(ds_doc_dir, reset)
    ret = []
    if ds_inventory is not None and ds_inventory.get("docs"):
        doc_env = _DocEnv(files_reg)
        for doc_info in ds_inventory["docs"]:
            _DocH.create(doc_info, doc_env).makeIt(ret)
    return ret

#===============================================
class _FileRegistry:
    @staticmethod
    def normDirPath(dir_path):
        if not dir_path or dir_path.endswith('/'):
            return dir_path
        return dir_path + '/'

    def __init__(self, ds_doc_dir, reset):
        self.mDestRoot = self.normDirPath(ds_doc_dir)
        self.mFiles = {"info.html"}
        if reset and os.path.exists(self.mDestRoot):
            shutil.rmtree(self.mDestRoot)
        if not os.path.exists(self.mDestRoot):
            os.mkdir(self.mDestRoot)

    def checkDestDir(self, dest_dir):
        if not os.path.exists(self.mDestRoot + dest_dir):
            os.mkdir(self.mDestRoot + dest_dir)

    def regPlace(self, dir_place):
        if dir_place in self.mFiles:
            print("Fatal: Destination file duplication: " + dir_place,
                file = sys.stderr)
            sys.exit()
        return self.mDestRoot + dir_place

#===============================================
class _DocEnv:
    def __init__(self, files_reg, src_path = None, dest_base = ""):
        self.mFilesReg = files_reg
        self.mSrcPath = _FileRegistry.normDirPath(src_path)
        self.mDestBase = _FileRegistry.normDirPath(dest_base)
        if self.mSrcPath is not None and not self.mSrcPath.endswith('/'):
            self.mSrcPath += '/'

    def getIdent(self):
        return self.mSrcPath

    def getSourcePath(self, doc_path):
        if self.mSrcPath is None or not doc_path.startswith('./'):
            return doc_path
        return self.mSrcPath + doc_path[2:]

    def regDestPlace(self, dest_place):
        return self.mFilesReg.regPlace(dest_place)

    def getDestBase(self):
        return self.mDestBase

    def getFilesReg(self):
        return self.mFilesReg

#===============================================
class _DocH:
    @staticmethod
    def create(doc_info, doc_env):
        doc_kind = doc_info["kind"]
        if doc_kind == "group":
            return _GroupH(doc_info, doc_env)
        if doc_kind == "support":
            return _SupportH(doc_info, doc_env)
        if doc_kind == "html":
            return _DocHtmlH(doc_info, doc_env)
        if doc_kind == "txt":
            return _DocTxtH(doc_info, doc_env)
        if doc_kind in ("png", "jpg"):
            return _DocImgH(doc_info, doc_env)
        if doc_kind == "*.txt":
            return _DocSeqTxtH(doc_info, doc_env)
        if doc_kind in ("*.png", "*.jpg"):
            return _DocSeqImgH(doc_info, doc_env)
        return None

    def __init__(self, doc_info, doc_env):
        self.mInfo = doc_info
        self.mDocEnv = doc_env

    def getDocEnv(self):
        return self.mDocEnv

    def get(self, key):
        return self.mInfo.get(key)

    def fatalMessage(self, message):
        print("Fatal:", message, "for DOC", self.mDocEnv.getIdent(),
            "title=", self.mInfo.get("title"), file = sys.stderr)

    def makeIt(self, ret):
        try:
            self._makeIt(ret)
        except Exception:
            self.fatalMessage("too bad data")
            traceback.print_exc(file = sys.stderr)
            sys.exit()

    def getSrcPathSeq(self, item_names = None):
        src_path = self.getDocEnv().getSourcePath(self.get("source"))
        if '*' in src_path:
            ret = sorted(glob(src_path))
            print("Pattern:", src_path, "Found:", len(ret), file = sys.stderr)
            if item_names is not None:
                prefix = src_path.partition('*')[0]
                postfix = src_path.rpartition('*')[2]
                i1, i2 = len(prefix), len(postfix)
                for fname in ret:
                    assert (fname.startswith(prefix)
                        and fname.endswith(postfix)), (
                        "Unexpected file name: "
                        + fname + " in path = " + src_path)
                    item_names.append(fname[i1:-i2])
            return ret
        if os.path.exists(src_path):
            return [src_path]
        return []

    def getDestPlace(self, src_path_seq):
        dest_place = self.get("dest")
        if not dest_place:
            if len(src_path_seq) < 1:
                self.fatalMessage("No destination names")
                sys.exit()
            if len(src_path_seq) > 1:
                self.fatalMessage("Many destination names")
                sys.exit()
            dest_place = os.path.basename(src_path_seq[0])
        return self.mDocEnv.getDestBase() + dest_place

    def makeFileDestPlace(self, src_path):
        return self.mDocEnv.getDestBase() + os.path.basename(src_path)

    def regDestPlace(self, dest_place):
        return self.mDocEnv.regDestPlace(dest_place)

#===============================================
class _GroupH(_DocH):
    def __init__(self, doc_info, doc_env):
        _DocH.__init__(self, doc_info, doc_env)

    def _makeIt(self, ret):
        src_path_seq = self.getSrcPathSeq()
        if len(src_path_seq) > 1:
            self.fatalMessage("not a single file")
            sys.exit()
        if len(src_path_seq) != 1:
            return
        dest_place = self.getDestPlace([])
        self.getDocEnv().getFilesReg().checkDestDir(dest_place)
        sub_ret = []
        doc_env = _DocEnv(self.getDocEnv().getFilesReg(),
            src_path_seq[0], dest_place)
        for doc_info in self.get("docs"):
            _DocH.create(doc_info, doc_env).makeIt(sub_ret)
        print("Doc directory created", dest_place, file = sys.stderr)
        ret.append([self.get("title"), sub_ret])

#===============================================
class _SupportH(_DocH):
    def __init__(self, doc_info, doc_env):
        _DocH.__init__(self, doc_info, doc_env)

    def _makeIt(self, ret):
        src_path_seq = self.getSrcPathSeq()
        if len(src_path_seq) > 1:
            self.fatalMessage("not a single file")
            sys.exit()
        if len(src_path_seq) != 1:
            return
        dest_place = self.getDestPlace(src_path_seq)
        self.getDocEnv().getFilesReg().checkDestDir(dest_place)
        for fname in glob(src_path_seq[0] + "/*.*"):
            dest_path = dest_place + "/" + os.path.basename(fname)
            shutil.copyfile(fname,
                self.getDocEnv().getFilesReg().regPlace(dest_path))
        print("Support directory created", dest_place, file = sys.stderr)

#===============================================
class _DocHtmlH(_DocH):
    def __init__(self, doc_info, doc_env):
        _DocH.__init__(self, doc_info, doc_env)

    def _makeIt(self, ret):
        src_path_seq = self.getSrcPathSeq()
        if len(src_path_seq) > 1:
            self.fatalMessage("not a single file")
            sys.exit()
        if len(src_path_seq) != 1:
            return
        dest_place = self.getDestPlace(src_path_seq)
        shutil.copyfile(src_path_seq[0], self.regDestPlace(dest_place))
        print("Doc html-file copied", dest_place, file = sys.stderr)
        ret.append([self.get("title"), dest_place])

#===============================================
class _DocTxtH(_DocH):
    def __init__(self, doc_info, doc_env):
        _DocH.__init__(self, doc_info, doc_env)

    def _makeIt(self, ret):
        src_path_seq = self.getSrcPathSeq()
        if len(src_path_seq) != 1:
            return
        dest_place = self.getDestPlace([])
        with open(self.regDestPlace(dest_place), "w",
                encoding = "utf-8") as output:
            startHtmlReport(output, self.get("title"))
            print(' <body><pre>', file = output)
            with open(src_path_seq[0], "r", encoding = "utf-8") as inp:
                print(inp.read(), file = output)
            print(' </pre></body>', file = output)
            print('</html>', file = output)
        print("Doc txt-based file created", dest_place, file = sys.stderr)
        ret.append([self.get("title"), dest_place])

#===============================================
class _DocImgH(_DocH):
    def __init__(self, doc_info, doc_env):
        _DocH.__init__(self, doc_info, doc_env)

    def _makeIt(self, ret):
        if not self.get("dest"):
            self.fatalMessage("dest html-file not set")
            sys.exit()
        src_path_seq = self.getSrcPathSeq()
        if len(src_path_seq) > 1:
            self.fatalMessage("not a single file")
            sys.exit()
        if len(src_path_seq) != 1:
            return
        img_dest_place = self.makeFileDestPlace(src_path_seq[0])
        shutil.copyfile(src_path_seq[0], self.regDestPlace(img_dest_place))

        desc = {"image": img_dest_place, "type": "img"}

        dest_place = self.getDestPlace([])
        with open(self.regDestPlace(dest_place), "w",
                encoding = "utf-8") as output:
            startHtmlReport(output, self.get("title"))
            print(' <body>', file = output)
            img_params = ['src="%s"' % os.path.basename(img_dest_place)]
            tooltip = self.get("tooltip")
            if tooltip:
                img_params.append('title="%s"' % escape(tooltip))
                desc["tooltip"] = tooltip
            print('  <img %s>' % " ".join(img_params), file = output)
            print(' </body>', file = output)
            print('</html>', file = output)
        print("Doc image-based file created", dest_place, file = sys.stderr)
        ret.append([self.get("title"), dest_place, desc])

#===============================================
class _DocSeqTxtH(_DocH):
    def __init__(self, doc_info, doc_env):
        _DocH.__init__(self, doc_info, doc_env)

    def _makeIt(self, ret):
        item_names = []
        src_path_seq = self.getSrcPathSeq(item_names)
        if len(src_path_seq) < 1:
            return
        dest_place = self.getDestPlace(src_path_seq)
        with open(self.regDestPlace(dest_place), "w",
                encoding = "utf-8") as output:
            startHtmlReport(output, self.get("title"))
            print(' <body>', file = output)
            if item_names:
                print('   <ul>', file = output)
                for name in item_names:
                    print('    <li><a href="#%s">%s</a>' % (name, name),
                        file = output)
                print('   </ul>', file = output)
            for idx, src_path in enumerate(src_path_seq):
                if idx < len(item_names):
                    print('<h2 id="%s">%s</h2>' %
                        (item_names[idx], item_names[idx]), file = output)

                print(' <pre>', file = output)
                with open(src_path, "r", encoding = "utf-8") as inp:
                    print(inp.read(), file = output)
                print(' </pre>', file = output)
            print('  </body>', file = output)
            print('</html>', file = output)
        print("Doc txt-seq-based file created", dest_place, file = sys.stderr)
        ret.append([self.get("title"), dest_place])

#===============================================
class _DocSeqImgH(_DocH):
    def __init__(self, doc_info, doc_env):
        _DocH.__init__(self, doc_info, doc_env)

    def _makeIt(self, ret):
        item_names = []
        src_path_seq = self.getSrcPathSeq(item_names)
        if len(src_path_seq) < 1:
            return

        desc = {"images": [], "type": "seq_img"}
        if item_names:
            desc["names"] = item_names

        dest_img_seq = []
        for img_src in src_path_seq:
            img_dest_place = self.makeFileDestPlace(img_src)
            desc["images"].append(img_dest_place)
            shutil.copyfile(img_src, self.regDestPlace(img_dest_place))
            dest_img_seq.append(os.path.basename(img_dest_place))

        dest_place = self.getDestPlace(src_path_seq)
        with open(self.regDestPlace(dest_place), "w",
                encoding = "utf-8") as output:
            startHtmlReport(output, self.get("title"))
            print(' <body>', file = output)
            if item_names:
                print('   <ul>', file = output)
                for name in item_names:
                    print('    <li><a href="#%s">%s</a>' % (name, name),
                        file = output)
                print('   </ul>', file = output)
            for idx, img_name in enumerate(dest_img_seq):
                if idx < len(item_names):
                    print('<h2 id="%s">%s</h2>' %
                        (item_names[idx], item_names[idx]), file = output)
                print('  <img src="%s">' % img_name, file = output)
            print('  </body>', file = output)
            print('</html>', file = output)
        print("Doc image-seq-based file created", dest_place,
            file = sys.stderr)
        ret.append([self.get("title"), dest_place, desc])
