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

#import sys
import re, logging

#===============================================
def _checkNotNone(obj):
    return obj is not None

def _checkNotEmpty(obj):
    return not obj

#===============================================
class _AttrFunc:
    def __init__(self, path, parent, is_seq = None):
        self.mParent = parent
        self.mPath = path
        self.mIsSeq = is_seq
        if self.mIsSeq is None:
            if self.mParent is not None:
                self.mIsSeq = self.mParent.isSeq()
            else:
                self.mIsSeq = False

    def getParent(self):
        return self.mParent

    def getPath(self):
        return self.mPath

    def isSeq(self):
        return self.mIsSeq

#===============================================
class RootF(_AttrFunc):
    def __init__(self):
        _AttrFunc.__init__(self, "", None)

    def __call__(self, obj):
        return [obj]

#===============================================
class KeyF(_AttrFunc):
    def __init__(self, path, parent):
        _AttrFunc.__init__(self, path, parent)
        assert path[-1].startswith('/')
        self.mName = path[-1][1:]

    def __call__(self, obj):
        ret = []
        for v_dict in self.getParent()(obj):
            if v_dict is not None:
                val = v_dict.get(self.mName)
                if val is not None:
                    ret.append(val)
        return ret

#===============================================
class SeqF(_AttrFunc):
    def __init__(self, path, parent):
        _AttrFunc.__init__(self, path, parent, True)
        assert path[-1] == "[]"

    def __call__(self, obj):
        ret = []
        for v_seq in self.getParent()(obj):
            if v_seq is not None:
                for val_obj in v_seq:
                    if val_obj is not None:
                        ret.append(val_obj)
        return ret

#===============================================
class AttrFuncPool:
    sPoolF = {"": RootF()}

    @classmethod
    def _makeF(cls, path):
        path_str = ''.join(path)
        if path_str in cls.sPoolF:
            return cls.sPoolF[path_str]
        path_parent = ''.join(path[:-1])
        parent_f = cls.sPoolF[path_parent]
        if path[-1] == "[]":
            ret_f = SeqF(path, parent_f)
        elif path[-1].startswith('/'):
            ret_f = KeyF(path, parent_f)
        else:
            assert False
        cls.sPoolF[path_str] = ret_f
        return ret_f

    sPatt = re.compile(r'[\[\/]')

    @classmethod
    def makeFunc(cls, path_str):
        ret_func = cls.sPoolF[""]
        idx = 0
        path = []
        try:
            while idx is not None:
                q = cls.sPatt.search(path_str, idx + 1)
                if q is not None:
                    path.append(path_str[idx:q.start()])
                    idx = q.start()
                else:
                    path.append(path_str[idx:])
                    idx = None
                ret_func = cls._makeF(path)
                if path_str[idx:].startswith("[]"):
                    path
        except Exception:
            logging.fatal("Failed to parse attrbute path: %s" % path_str)
        return ret_func

#===============================================
