import sys, json, codecs, re
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
        self.mRecNo = -1

    def process(self, rec):
        self.mRecNo += 1
        zygosity = rec["data"]["zygosity"]
        if zygosity[self.mKeyProband] < 1:
            return
        z_f, z_m = zygosity[self.mKeyFather], zygosity[self.mKeyMother]
        if  z_f > 0 and z_m < 1:
            self._regIt(self.mGenesF, rec)
        elif z_f < 1 and z_m > 0:
            self._regIt(self.mGenesM, rec)

    def _regIt(self, registry, rec):
        genes = rec["view"]["general"].get("genes")
        if not genes:
            return
        for gene in genes:
            registry[gene].add(self.mRecNo)

    def result(self, output):
        res_tab = defaultdict(list)
        for gene, f_seq_rec_no in self.mGenesF.items():
            assert len(f_seq_rec_no) > 0
            m_seq_rec_no = self.mGenesM.get(gene)
            if m_seq_rec_no is None:
                continue
            assert len(m_seq_rec_no) > 0
            for rec_no in (f_seq_rec_no | m_seq_rec_no):
                res_tab[rec_no].append(gene)
        print >> output, json.dumps({"total": self.mRecNo})
        for rec_no in sorted(res_tab.keys()):
            print >> output, json.dumps([rec_no,
                [["comp-hets", sorted(res_tab[rec_no])]]])

#=====================================
class PostAttonationProcess:
    def __init__(self, mine_lines):
        self.mMineLines = mine_lines
        self.mBufRecords = []
        self.mDataMiner = FamilyDataMiner()
        self.mBatch = None

    def process(self, rec):
        if self.mDataMiner is not None:
            self.mDataMiner.feed(rec)
            family_data = self.mDataMiner.getFamilyData()
            if family_data is not None:
                self.mBatch = CompHetsBatch(family_data)
                for rec in self.mBufRecords:
                    self.mBatch.process(rec)
                self.mBufRecords = None
                self.mDataMiner = None
                return
            self.mBufRecords.append(rec)
            assert len(self.mBufRecords) < self.mMineLines
            return
        self.mBatch.process(rec)

    def report(self, output):
        self.mBatch.result(output)

#=====================================
parser = ArgumentParser()
parser.add_argument("--minelines", type = int, default = 1000,
    help="Max count of lines to mine family info")
parser.add_argument("source", nargs = 1, help = "Dataset name")
run_args = parser.parse_args()

proc = PostAttonationProcess(run_args.minelines)

with JsonLineReader(run_args.source[0]) as inp:
    for rec in inp:
        proc.process(rec)

proc.report(sys.stdout)

