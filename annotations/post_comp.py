import sys, json, codecs, re, gzip
from datetime import datetime
from argparse import ArgumentParser
from collections import defaultdict

from app.prepare.read_json import JsonLineReader
#=====================================
sys.stdin  = codecs.getreader('utf8')(sys.stdin)
sys.stderr = codecs.getwriter('utf8')(sys.stderr)
sys.stdout = codecs.getwriter('utf8')(sys.stdout)

#=====================================
class FamilyDataMiner:
    def __init__(self):
        self.mFamilyData = None
        self.mMembers = None

    sReg_HasVariant = [
        re.compile("^proband\s+\[(\w+)\]$"),
        re.compile("^father\s+\[(\w+)\]$"),
        re.compile("^mother\s+\[(\w+)\]$")]

    def getFamilyData(self):
        if self.mFamilyData is not None and all(
                [mem_info is not None for mem_info in self.mFamilyData]):
            return self.mFamilyData
        return None

    def feed(self, rec):
        if self.mFamilyData is None:
            self.mFamilyData = [None] * 3
            self.mMembers = set(rec["data"]["zygosity"].keys())
        seq = rec["_filters"].get("has_variant")
        if not seq:
            return
        for h_var in seq:
            for idx, reg_ex in enumerate(self.sReg_HasVariant):
                if self.mFamilyData[idx] is None:
                    q = reg_ex.match(h_var)
                    if q:
                        assert q.group(1) in self.mMembers
                        self.mFamilyData[idx] = q.group(1)

#=====================================
class CompHetsBatch:
    def __init__(self, family_data):
        self.mKeyProband, self.mKeyFather, self.mKeyMother = family_data
        self.mGenesF = defaultdict(set)
        self.mGenesM = defaultdict(set)
        self.mCounts = [0, 0, 0]
        self.mResTab = None

    def process(self, rec_no, rec_data):
        self.mCounts[0] += 1
        if self.mCounts[0] > 0 and self.mCounts[0] % 100 == 0:
            self.reportStatus()
        if rec_data.get("record_type") == "metadata":
            return
        zygosity = rec_data["data"]["zygosity"]
        if zygosity[self.mKeyProband] < 1:
            return
        z_f, z_m = zygosity[self.mKeyFather], zygosity[self.mKeyMother]
        if  z_f > 0 and z_m < 1:
            self._regIt(self.mGenesF, rec_no, rec_data)
            self.mCounts[1] += 1
        elif z_f < 1 and z_m > 0:
            self._regIt(self.mGenesM, rec_no, rec_data)
            self.mCounts[2] += 1

    def _regIt(self, registry, rec_no, rec_data):
        genes = rec_data["view"]["general"].get("genes")
        if not genes:
            return
        for gene in genes:
            registry[gene].add(rec_no)

    def reportStatus(self):
        print >> sys.stderr, "\rLines: %d, found: %d/%d, genes: %d/%d" % (
            self.mCounts[0], self.mCounts[1], self.mCounts[2],
            len(self.mGenesF), len(self.mGenesM)),

    def finishUp(self):
        self.reportStatus()
        self.mResTab = defaultdict(list)
        gene_cnt = 0
        for gene, f_seq_rec_no in self.mGenesF.items():
            assert len(f_seq_rec_no) > 0
            m_seq_rec_no = self.mGenesM.get(gene)
            if m_seq_rec_no is None:
                continue
            gene_cnt += 1
            assert len(m_seq_rec_no) > 0
            for rec_no in (f_seq_rec_no | m_seq_rec_no):
                self.mResTab[rec_no].append(gene)
        print >> sys.stderr, "Final result: %d variants in %d genes" % (
            len(self.mResTab), gene_cnt)

    def report(self, output):
        print >> output, json.dumps(
            {"total": self.mCounts[0], "found": len(self.mResTab)})
        for rec_no in sorted(self.mResTab.keys()):
            print >> output, json.dumps([rec_no,
                [["comp-hets", sorted(self.mResTab[rec_no])]]])

    def recIsActive(self, rec_no):
        return rec_no in self.mResTab

    def transform(self, rec_no, rec_data):
        assert rec_no in self.mResTab
        rec_data["_filters"]["compoundHet"] = True

#=====================================
class PostAttonationProcess:
    def __init__(self, mine_lines):
        self.mMineLines = mine_lines
        self.mBufRecords = []
        self.mDataMiner = FamilyDataMiner()
        self.mBatch = None

    def process(self, rec_no, rec_data):
        if self.mDataMiner is not None:
            self.mDataMiner.feed(rec_data)
            family_data = self.mDataMiner.getFamilyData()
            if family_data is None:
                self.mBufRecords.append((rec_no, rec_data))
                assert len(self.mBufRecords) < self.mMineLines
                return
            self.mBatch = CompHetsBatch(family_data)
            for r_no, r_data in self.mBufRecords:
                self.mBatch.process(r_no, r_data)
            self.mBufRecords = None
            self.mDataMiner = None
        self.mBatch.process(rec_no, rec_data)

    def finishUp(self):
        self.mBatch.finishUp()

    def report(self, output):
        self.mBatch.report(output)

    def recIsActive(self, rec_no):
        return self.mBatch.recIsActive(rec_no)

    def transform(self, rec_no, rec_data):
        self.mBatch.transform(rec_no, rec_data)


#=====================================
time_start = datetime.now()
parser = ArgumentParser()
parser.add_argument("--minelines", type = int, default = 1000,
    help="Max count of lines to mine family info")
parser.add_argument("-o", "--output",
    help="Output name for modified annotated json, .gz expected")
parser.add_argument("source", nargs = 1, help = "Dataset name")
run_args = parser.parse_args()

proc = PostAttonationProcess(run_args.minelines)

print >> sys.stderr, "Started at:", time_start
with JsonLineReader(run_args.source[0]) as inp:
    for rec_no, rec_data in enumerate(inp):
        proc.process(rec_no, rec_data)

proc.finishUp()
time_calc = datetime.now()
print >> sys.stderr, "Calculated time:", time_calc - time_start

if run_args.output:
    print >> sys.stderr, "Save result to", run_args.output
    with gzip.open(run_args.output, "wb") as outp:
        with JsonLineReader(run_args.source[0], False) as inp:
            for rec_no, rec_line in enumerate(inp):
                if proc.recIsActive(rec_no):
                    rec_data = json.loads(rec_line)
                    proc.transform(rec_no, rec_data)
                    rec_line = json.dumps(rec_data, ensure_ascii = False)
                print >> outp, rec_line.encode("utf-8")
                if rec_no % 100 == 0:
                    print >> sys.stderr, "\r", rec_no, "lines...",

    time_done = datetime.now()
    print >> sys.stderr, "Done at", time_done, "for", time_done - time_calc
else:
    proc.report(sys.stdout)

