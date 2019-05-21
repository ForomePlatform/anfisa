import logging
from collections import defaultdict

from app.config.a_config import AnfisaConfig
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
        if z_p == 1:
            if  z_f > 0 and z_m == 0:
                self._regIt(self.mGenesF, rec_no, rec_fdata)
                self.mCounts[1] += 1
            elif z_f == 0 and z_m > 0:
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
