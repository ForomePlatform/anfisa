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

from forome_tools.path_works import AttrFuncPool
#===============================================
class AttrFuncHelper:
    @staticmethod
    def singleGetter(vpath):
        return _attrSingleGetter(vpath)

    @staticmethod
    def multiStrGetter(separator, path_seq):
        return _multiStrAtrGetter(separator, path_seq)

    @staticmethod
    def getter(vpath):
        if vpath.endswith('[]'):
            return AttrFuncPool.makeFunc(vpath)
        return _attrSingleGetter(vpath)

#===============================================
class _attrSingleGetter:
    def __init__(self, vpath):
        self.mFunc = AttrFuncPool.makeFunc(vpath)

    def __call__(self, rec_data):
        res = self.mFunc(rec_data)
        if res is not None and len(res) > 0:
            return res[0]
        return None

#===============================================
class _multiStrAtrGetter:
    def __init__(self, separator, path_seq):
        self.mSeparator = separator
        self.mFuncSeq = [AttrFuncPool.makeFunc(vpath)
            for vpath in path_seq]

    def __call__(self, rec_data):
        values = []
        for func in self.mFuncSeq:
            vvv = func(rec_data)
            assert len(vvv) > 0, "Not found data path: " + func.getPathRepr()
            values.append(vvv[0])
        return self.mSeparator.join(map(str, values))
