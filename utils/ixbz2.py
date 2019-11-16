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

import bz2, threading
from time import time
from array import array
from bisect import bisect
from threading import Lock

#===============================================
class IndexBZ2:
    def __init__(self, fname):
        self.mFile = open(fname, 'r+b')
        self.mLock = Lock()
        assert b'IdxBZ2' == self._read(0, 6)
        tab_loc = array('L')
        tab_loc.fromstring(self._read(6, 16))
        pos, length = tab_loc
        self.mIdxTable = array('L')
        if length > 0:
            self.mIdxTable.fromstring(self._read(pos, length))
            last_start, last_count = self.mIdxTable[-4:-2]
            self.mTotalCount = int(last_start + last_count)
            self.mChunks = self.mIdxTable[::4]
        else:
            self.mTotalCount = 0
            self.mChunks = []

    def __enter__(self):
        return self

    def __exit__(self, tp, value, traceback):
        self.close()

    def close(self):
        self.mFile.close()
        self.mMMapFile = None

    def __len__(self):
        return self.mTotalCount

    def _read(self, pos, length):
        with self.mLock:
            self.mFile.seek(pos)
            return self.mFile.read(length)

    def __getitem__(self, idx):
        chunk_idx = 4 * (bisect(self.mChunks, idx) - 1)
        start, count, pos, length = self.mIdxTable[chunk_idx: chunk_idx + 4]
        chunk_lines = bz2.decompress(
            self._read(pos, length)).decode('utf-8').split('\n')
        return chunk_lines[idx - start]

#===============================================
class FormatterIndexBZ2:
    def __init__(self, fname, block_size = 2*19, report_output = None):
        self.mBlockSize = block_size
        self.mFile = open(fname, 'wb')
        self.mFile.write(b'IdxBZ2')
        self.mFile.write(b' ' * 16)
        self.mIdxTable = array('L')
        self.mDoneIdx = 0
        self.mCurLines = []
        self.mCurBlockSize = 0
        self.mTotalInpBytes = 0
        self.mTotalOutBytes = 0
        self.mBlockMinSize = 0
        self.mBlockMaxSize = 0
        self.mBlockMinComp = 0.
        self.mBlockMaxComp = 0.
        self.mBlockAccumComp = 0.
        self.mReportOutput = report_output

    def __enter__(self):
        return self

    def __exit__(self, tp, value, traceback):
        self.close()

    def _makeChunk(self, q_final = False):
        line_count = len(self.mCurLines)
        if q_final and line_count == 0:
            return
        comp_data = bz2.compress('\n'.join(self.mCurLines).encode('utf-8'))
        comp_size = len(comp_data)
        self.mIdxTable.extend([self.mDoneIdx, line_count,
            self.mFile.tell(), comp_size])
        self.mFile.write(comp_data)
        comp_coeff = comp_size / (self.mCurBlockSize + .01)
        self.mBlockAccumComp += comp_coeff
        if q_final:
            return
        if self.mDoneIdx == 0:
            self.mBlockMinSize = comp_size
            self.mBlockMinComp = comp_coeff
        else:
            self.mBlockMinSize = min(self.mBlockMinSize, comp_size)
            self.mBlockMinComp = min(self.mBlockMinComp, comp_coeff)
        self.mBlockMaxSize = max(self.mBlockMaxSize, comp_size)
        self.mBlockMaxComp = max(self.mBlockMaxComp, comp_coeff)

        self.mDoneIdx += line_count
        self.mTotalOutBytes += comp_size
        self.mCurLines = []
        self.mCurBlockSize = 0

    def getDoneLines(self):
        return self.mDoneIdx

    def getDoneBlocks(self):
        return len(self.mIdxTable) / 4

    def putLine(self, line):
        self.mCurLines.append(line)
        self.mTotalInpBytes += 1 + len(line)
        self.mCurBlockSize += 1 + len(line)
        if self.mCurBlockSize > self.mBlockSize:
            self._makeChunk()

    def close(self):
        self._makeChunk(q_final = True)
        tab_content = self.mIdxTable.tostring()
        tab_loc = array('L')
        tab_loc.extend([self.mFile.tell(), len(tab_content)])
        self.mFile.write(tab_content)
        self.mFile.seek(6)
        self.mFile.write(tab_loc.tostring())
        self.mFile.close()
        if self.mReportOutput is not None:
            self.mReportOutput.append((
                self.mTotalInpBytes, self.mTotalOutBytes,
                self.mDoneIdx, len(self.mIdxTable) / 4,
                self.mBlockMinSize, self.mBlockMaxSize,
                self.mBlockMinComp, self.mBlockMaxComp,
                self.mBlockAccumComp * 4 / len(self.mIdxTable)))

#===============================================
class InputReader(threading.Thread):
    def __init__(self, stream):
        threading.Thread.__init__(self)

        self.mLock = threading.Lock()
        self.mThrCondEmpty = threading.Condition()
        self.mThrCondOver = threading.Condition()
        self.mStream = stream
        self.mLines = []
        self.mFinish = False
        self.mCnt = 0
        self.mDelayEmpty = 0.
        self.mDelayOver = 0.
        self.mCntEmpty = 0
        self.mCntOver = 0
        self.start()

    def readline(self):
        while True:
            with self.mLock:
                self.mCnt += 1
                if len(self.mLines) > 0:
                    ret = self.mLines.pop(0)
                    with self.mThrCondOver:
                        self.mThrCondOver.notify()
                    return ret
                elif self.mFinish:
                    return None
            with self.mThrCondEmpty:
                tm0 = time()
                self.mThrCondEmpty.wait()
                self.mDelayEmpty += (time() - tm0)
                self.mCntEmpty += 1

    def run(self):
        for line in self.mStream:
            while True:
                with self.mLock:
                    if len(self.mLines) < 1000:
                        self.mLines.append(line)
                        with self.mThrCondEmpty:
                            self.mThrCondEmpty.notify()
                        break
                with self.mThrCondOver:
                    tm0 = time()
                    self.mThrCondOver.wait()
                    self.mDelayOver += (time() - tm0)
                    self.mCntOver += 1
        with self.mLock:
            self.mFinish = True
            with self.mThrCondEmpty:
                self.mThrCondEmpty.notify()

    def close(self):
        for _ in range(1000):
            with self.mLock:
                if not self.is_alive():
                    break
            time.sleep(.001)
        print("Delays: empty = %.01f/%d full = %.01f/%d" % (
            self.mDelayEmpty, self.mCntEmpty, self.mDelayOver, self.mCntOver),
            file = sys.stderr)


#===============================================
if __name__ == "__main__":
    import sys, codecs
    from argparse import ArgumentParser

    sys.stdin  = codecs.getreader('utf8')(sys.stdin.detach())
    sys.stderr = codecs.getwriter('utf8')(sys.stderr.detach())
    sys.stdout = codecs.getwriter('utf8')(sys.stdout.detach())

    parser = ArgumentParser()
    parser.add_argument("--block",  type = int, default = 2**19,
        help = "block size before compress")
    parser.add_argument("--calm",  action = "store_true",
        help = "calm mode")
    parser.add_argument("-o", "--output", default = "",
        help = "output file name")
    parser.add_argument("file", nargs = 1, help = "File name")
    run_args = parser.parse_args()

    if run_args.file[0].endswith('.ixbz2'):
        with IndexBZ2(run_args.file[0]) as index:
            for idx in range(len(index)):
                print(index[idx])
        sys.exit()

    out_fname = run_args.output
    if not out_fname:
        assert run_args.file[0] != "/dev/stdin"
        out_fname = run_args.file[0] + '.ixbz2'
    report = []
    done_blocks = None

    if run_args.file[0] == "/dev/stdin":
        inp = InputReader(sys.stdin)
    else:
        inp = open(run_args.file[0], 'r', encoding = 'utf-8')

    with FormatterIndexBZ2(out_fname, run_args.block, report) as form:
        while True:
            line = inp.readline()
            if not line:
                break
            form.putLine(line.rstrip())
            if form.getDoneBlocks() != done_blocks:
                done_blocks = form.getDoneBlocks()
                if not run_args.calm:
                    sys.stderr.write("...%d blocks - %d lines\r" % (
                        done_blocks, form.getDoneLines()))
    inp.close()

    print("", file = sys.stderr)
    total_inp, total_outp, n_lines, n_blocks = report[0][:4]
    min_chunk_size, max_chunk_size = report[0][4:6]
    min_comp, max_comp, avg_comp = report[0][6:]

    print("Prepared file:", out_fname, file = sys.stderr)
    print("Counts: lines=%d blocks=%d" % (
        n_lines, n_blocks), file = sys.stderr)
    print("Sizes: decomp=%d -> comp=%d (%.01f%s)" % (total_inp,
        total_outp, (100. * total_outp)/(total_inp + .001), '%'),
        file = sys.stderr)
    print("Compresssed block sizes: min=%d avg=%d max=%d" % (
        min_chunk_size,
        int((total_outp) / (n_blocks + .01)), max_chunk_size),
        file = sys.stderr)
    print("Compression: min=%.01f%s avg=%.01f%s max=%.01f%s" % (
        min_comp * 100, '%', avg_comp * 100, '%', max_comp * 100, '%'),
        file = sys.stderr)
