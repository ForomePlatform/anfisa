import sys, json, re, logging
from datetime import datetime
from collections import defaultdict

from app.model.a_config import AnfisaConfig
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

    def feed(self, rec_data):
        if self.mFamilyData is None:
            self.mFamilyData = [None] * 3
            self.mMembers = set(rec_data["data"]["zygosity"].keys())
        seq = rec_data["_filters"].get("has_variant")
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
    def __init__(self, family_data, line_period):
        self.mKeyProband, self.mKeyFather, self.mKeyMother = family_data
        self.mGenesF = defaultdict(set)
        self.mGenesM = defaultdict(set)
        self.mCounts = [0, 0, 0]
        self.mLinePeriod = line_period
        self.mResTab = None
        self.mTimeStart = datetime.now()
        print >> sys.stderr, "Start CompHetsBatch at", self.mTimeStart

    def process(self, rec_no, rec_data):
        self.mCounts[0] += 1
        if self.mCounts[0] > 0 and self.mCounts[0] % self.mLinePeriod == 0:
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
        time_comp = datetime.now()
        print >> sys.stderr, "\nFinishing CompHetsBatch at", time_comp, \
            "for", (time_comp - self.mTimeStart)
        print >> sys.stderr, "Result: %d variants in %d genes\n" % (
            len(self.mResTab), gene_cnt)
        return True

    def report(self, output):
        print >> output, json.dumps(
            {"total": self.mCounts[0], "found": len(self.mResTab)})
        for rec_no in sorted(self.mResTab.keys()):
            print >> output, json.dumps([rec_no,
                [["comp-hets", sorted(self.mResTab[rec_no])]]])

    def recIsActive(self, rec_no):
        return rec_no in self.mResTab

    def transform(self, rec_no, rec_data):
        if rec_no not in self.mResTab:
            return False
        rec_data["_filters"]["compoundHet"] = True
        return True

#=====================================
class CompHetsMarkupBatch:
    def __init__(self, proband_rel):
        setup = AnfisaConfig.configOption("comp-hets.setup")
        self.mF_zFamily = [setup["zygosity"] + '_' + str(member_idx)
            for member_idx in proband_rel]
        self.mF_Genes = setup["Genes"]
        self.mF_Result = setup["Compound_heterozygous"]
        self.mView_Result = setup["ws_compound_heterosygotes"]

        self.mGenesF = defaultdict(set)
        self.mGenesM = defaultdict(set)
        self.mCounts = [0, 0, 0]
        self.mResTab = None

    def feed(self, rec_no, rec_fdata):
        self.mCounts[0] += 1
        z_p, z_f, z_m = [rec_fdata[key] for key in self.mF_zFamily]
        if  z_f > 0 and z_m < 1:
            self._regIt(self.mGenesF, rec_no, rec_fdata)
            self.mCounts[1] += 1
        elif z_f < 1 and z_m > 0:
            self._regIt(self.mGenesM, rec_no, rec_fdata)
            self.mCounts[2] += 1

    def _regIt(self, registry, rec_no, rec_fdata):
        genes = rec_fdata.get(self.mF_Genes)
        if not genes:
            return
        for gene in genes:
            registry[gene].add(rec_no)

    def finishUp(self, view_schema, flt_schema):
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
        logging.info(("CompHetsMarkupBatch result of total %d: "
            "%d variants in %d genes" ) % (
            self.mCounts[0], len(self.mResTab), gene_cnt))

        f_done = False
        for funit_info in flt_schema:
            if funit_info["name"] == self.mF_Result:
                funit_info["variants"] = [["True", len(self.mResTab)]]
                f_done = True
                break
        assert f_done
        v_done = False
        for vtab_info in view_schema:
            if vtab_info["name"] != "_main":
                continue
            for field_info in vtab_info["attrs"]:
                if field_info["name"] == self.mView_Result:
                    field_info["kind"] = "norm"
                    v_done = True
                    break
            if not v_done:
                vtab_info["attrs"].append({
                    "is_seq": False,
                    "kind": "norm",
                    "name": self.mView_Result,
                    "title": self.mView_Result})
                v_done = True
        assert v_done

    def transformFData(self, rec_no, rec_fdata):
        if rec_no in self.mResTab:
            rec_fdata[self.mF_Result] = ["True"]

    def transformRecData(self, rec_no, rec_data):
        if rec_no in self.mResTab:
            rec_data["data"][self.mView_Result] = ", ".join(
                sorted(self.mResTab[rec_no]))
