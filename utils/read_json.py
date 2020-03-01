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

import gzip, bz2, json
from glob import glob

#===============================================
class PlainFileReader:
    def __init__(self, fname):
        self.mInput = open(fname, 'r', encoding = 'utf-8')

    def nextLine(self):
        return self.mInput.readline()

    def close(self):
        self.mInput.close()

#===============================================
class GzipFileReader:
    def __init__(self, fname):
        self.mInput = gzip.open(fname, 'rt', encoding = "utf-8")

    def nextLine(self):
        return self.mInput.readline()

    def close(self):
        self.mInput.close()

#===============================================
class Bz2FileReader:
    def __init__(self, fname):
        self.mInput = bz2.BZ2File.open(fname, 'rt', encoding = "utf-8")

    def nextLine(self):
        return self.mInput.readline()

    def close(self):
        self.mInput.close()

#===============================================
class JsonLineReader:
    def __init__(self, source, parse_json = True,  transform_f = None):
        self.mSources = sorted(glob(source)) if "*" in source else [source]
        self.mCurReader = None
        self.mParseMode = parse_json
        self.mTransF = transform_f
        self.mCurLineNo = -1

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

    def __enter__(self):
        return self

    def __iter__(self):
        while True:
            line = self.nextLine()
            if line is None:
                break
            yield line

    def getCurLineNo(self):
        return self.mCurLineNo

    def close(self):
        self.mCurLineNo = -1
        if self.mCurReader is not None:
            self.mCurReader.close()

    def nextLine(self):
        return self.readOne()

    def readOne(self):
        while True:
            if self.mCurReader is not None:
                line = self.mCurReader.nextLine()
                self.mCurLineNo += 1
                if not line:
                    self.mCurReader.close()
                    self.mCurReader = None
                    continue
                if self.mParseMode:
                    rec = json.loads(line)
                    if self.mTransF:
                        rec = self.mTransF(rec)
                    return rec
                return line.rstrip()
            if len(self.mSources) == 0:
                return None
            src = self.mSources.pop(0)
            if src.endswith('.gz'):
                self.mCurReader = GzipFileReader(src)
            elif src.endswith('.bz2'):
                self.mCurReader = Bz2FileReader(src)
            else:
                self.mCurReader = PlainFileReader(src)

#===============================================
def readJSonRecords(src,  transform_f = None):
    if '*' in src:
        names = sorted(glob(src))
    else:
        names = [src]
    if transform_f is None:
        process_f = json.loads
    else:
        def process_f(line):
            return transform_f(json.loads(line))
    for nm in names:
        if nm.endswith('.gz'):
            with gzip.open(nm, 'rt', encoding = "utf-8") as inp:
                for line in inp:
                    yield process_f(line)
        elif nm.endswith('.bz2'):
            with bz2.BZ2File(nm, 'rt', encoding = "utf-8") as inp:
                for line in inp:
                    yield process_f(line)
        else:
            with open(nm, 'r', encoding = 'utf-8') as inp:
                for line in inp:
                    yield process_f(line)
