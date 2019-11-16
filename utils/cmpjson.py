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

import sys, codecs, json
from random import Random
from argparse import ArgumentParser
from difflib import Differ

from .read_json import JsonLineReader
#=====================================
sys.stdin  = codecs.getreader('utf8')(sys.stdin.detach())
sys.stderr = codecs.getwriter('utf8')(sys.stderr.detach())
sys.stdout = codecs.getwriter('utf8')(sys.stdout.detach())

#=====================================
class SamplesRandomCollector:
    def __init__(self, size, seed):
        self.mRH = Random(seed)
        self.mSamples = []
        self.mSize = size
        self.mCount = 0

    def getRecNoSeq(self):
        return [smp[0] for smp in self.mSamples]

    def getCount(self):
        return self.mCount

    def addRecord(self, record):
        rec_no = self.mCount
        if rec_no < self.mSize:
            self.mSamples.append((rec_no, record))
        else:
            pos = self.mRH.randint(0, self.mCount)
            if pos < self.mSize:
                self.mSamples[pos] = ((rec_no, record))
        self.mCount += 1

    def getSize(self):
        return len(self.mSamples)

    def getRecIdx(self, pos):
        return self.mSamples[pos][0]

    def getRecord(self, pos):
        return self.mSamples[pos][1]

#=====================================
class SamplesDirectCollector:
    def __init__(self, rec_no_seq):
        self.mRecNoSeq = rec_no_seq
        self.mSamples = [None] * len(rec_no_seq)
        self.mPosMap = {rec_no: pos
            for pos, rec_no in enumerate(rec_no_seq)}
        self.mCount = 0

    def getCount(self):
        return self.mCount

    def getRecNoSeq(self):
        return self.mRecNoSeq

    def addRecord(self, record):
        rec_no = self.mCount
        if rec_no in self.mPosMap:
            self.mSamples[self.mPosMap[rec_no]] = (rec_no, record)
        self.mCount += 1

    def getSize(self):
        return len(self.mSamples)

    def getRecIdx(self, pos):
        return self.mSamples[pos][0]

    def getRecord(self, pos):
        return self.mSamples[pos][1]


#=====================================
if __name__ == "__main__":
    parser = ArgumentParser()
    parser.add_argument("--seed", type = int, default = 179,
        help = "Seed for random selection")
    parser.add_argument("-n", "--number", type = int, default = 5,
        help = "Number of samples")
    parser.add_argument("-s", "--seq",
        help = "Direct list of records, comma separated")
    parser.add_argument("-o", "--output",
        help =
        "Output filename preffix, use it to generate separated json files")
    parser.add_argument("source", nargs = 2, help = "Two js files to compare")
    run_args = parser.parse_args()

    if run_args.seq:
        collector1 = SamplesDirectCollector(map(int(run_args.seq.split(','))))
    else:
        collector1 = SamplesRandomCollector(run_args.number, run_args.seed)

    with JsonLineReader(run_args.source[0]) as inp:
        for record in inp:
            collector1.addRecord(record)

    collector2 = SamplesDirectCollector(collector1.getRecNoSeq())
    with JsonLineReader(run_args.source[1]) as inp:
        for record in inp:
            collector2.addRecord(record)

    if collector1.getCount() != collector2.getCount():
        print("Different counts: %d / %d" % (
            collector1.getCount(), collector2.getCount()), file = sys.stderr)
        sys.exit()

    if run_args.output:
        for idx in range(collector1.getSize()):
            rec_no = collector1.getRecIdx(idx)
            assert rec_no == collector2.getRecIdx(idx)
            fname1 = run_args.output + ("1_%d.json" % rec_no)
            fname2 = run_args.output + ("2_%d.json" % rec_no)
            print("Preparing %s / %s" % (fname1, fname2), file = sys.stderr)
            with open(fname1, "w", encoding = "utf8") as outp:
                print(json.dumps(collector1.getRecord(idx),
                    sort_keys=True, indent = 4), file = outp)
            with open(fname2, "w", encoding = "utf8") as outp:
                print(json.dumps(collector2.getRecord(idx),
                    sort_keys=True, indent = 4), file = outp)
    else:
        diff = Differ()
        for idx in range(collector1.getSize()):
            rec_no = collector1.getRecIdx(idx)
            assert rec_no == collector2.getRecIdx(idx)
            repr1 = json.dumps(collector1.getRecord(idx),
                sort_keys = True, indent = 4)
            repr2 = json.dumps(collector2.getRecord(idx),
                sort_keys = True, indent = 4)
            print("==========Cmp rec_no=%d===============" % rec_no)
            cur_diff = False
            prev_line_ok = None
            for line in diff.compare(repr1.splitlines(), repr2.splitlines()):
                if line.startswith(' '):
                    if not cur_diff:
                        prev_line_ok = line
                    else:
                        assert prev_line_ok is None
                        print(line)
                        cur_diff = False
                    continue
                if prev_line_ok is not None:
                    print(prev_line_ok)
                    prev_line_ok = None
                cur_diff = True
                print(line)
        print("=============Done=====================")
