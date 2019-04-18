import sys, json, codecs, gzip
from datetime import datetime
from argparse import ArgumentParser

from utils.read_json import JsonLineReader
from .comp_hets import FamilyDataMiner, CompHetsBatch
#=====================================
class PostAttonationProcess:
    def __init__(self, mine_lines = 1000, line_period = 1000):
        self.mMineLines = mine_lines
        self.mLinePeriod = line_period
        self.mBufRecords = []
        self.mDataMiner = FamilyDataMiner()
        self.mBatch = None

    def isOK(self):
        return (self.mBatch is not None or
            self.mDataMiner is not None)

    def _shutDown(self):
        self.mDataMiner = None
        self.mBufRecords = None
        print >> sys.stderr, \
            "Family is not complete for compound het evaluation"

    def process(self, rec_no, rec_data):
        if self.mDataMiner is not None:
            self.mDataMiner.feed(rec_data)
            family_data = self.mDataMiner.getFamilyData()
            if family_data is None:
                self.mBufRecords.append((rec_no, rec_data))
                if len(self.mBufRecords) >= self.mMineLines:
                    self._shutDown()
                return
            self.mBatch = CompHetsBatch(family_data, self.mLinePeriod)
            for r_no, r_data in self.mBufRecords:
                self.mBatch.process(r_no, r_data)
            self.mBufRecords = None
            self.mDataMiner = None
        if self.mBatch is not None:
            self.mBatch.process(rec_no, rec_data)

    def finishUp(self):
        if self.mBufRecords is not None:
            self._shutDown();
            return False
        if self.mBatch is not None:
            return self.mBatch.finishUp()
        return False

    def report(self, output):
        if self.mBatch is not None:
            self.mBatch.report(output)

    def recIsActive(self, rec_no):
        if self.mBatch is not None:
            return self.mBatch.recIsActive(rec_no)
        return False

    def transform(self, rec_no, rec_data):
        if self.mBatch is not None:
            return self.mBatch.transform(rec_no, rec_data)
        return False

#=====================================
if __name__ == '__main__':
    sys.stdin  = codecs.getreader('utf8')(sys.stdin)
    sys.stderr = codecs.getwriter('utf8')(sys.stderr)
    sys.stdout = codecs.getwriter('utf8')(sys.stdout)

    parser = ArgumentParser()
    parser.add_argument("--minelines", type = int, default = 1000,
        help="Max count of lines to mine family info")
    parser.add_argument("--replines", type = int, default = 1000,
        help="Report lines period")
    parser.add_argument("-o", "--output",
        help="Output name for modified annotated json, .gz expected")
    parser.add_argument("source", nargs = 1, help = "Dataset name")
    run_args = parser.parse_args()

    proc = PostAttonationProcess(run_args.minelines, run_args.replines)

    with JsonLineReader(run_args.source[0]) as inp:
        for rec_no, rec_data in enumerate(inp):
            proc.process(rec_no, rec_data)
    proc.finishUp()

    if not proc.isOK():
        print >> sys.stderr, "Terminated"
        sys.exit()

    if not run_args.output:
        proc.report(sys.stdout)
        sys.exit()

    time_start_save = datetime.now()
    print >> sys.stderr, "Save result to", run_args.output, \
        "at", time_start_save
    with gzip.open(run_args.output, "wb") as outp:
        with JsonLineReader(run_args.source[0], False) as inp:
            for rec_no, rec_line in enumerate(inp):
                if proc.recIsActive(rec_no):
                    rec_data = json.loads(rec_line)
                    proc.transform(rec_no, rec_data)
                    rec_line = json.dumps(rec_data, ensure_ascii = False)
                print >> outp, rec_line.encode("utf-8")
                if rec_no % run_args.replines == 0:
                    print >> sys.stderr, "\r", rec_no, "lines...",

    time_done_save = datetime.now()
    print >> sys.stderr, "Done at", time_done_save, \
        "for", time_done_save - time_start_save
