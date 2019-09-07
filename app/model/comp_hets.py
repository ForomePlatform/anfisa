import logging, json
from collections import defaultdict

from app.config.a_config import AnfisaConfig
from app.filter.condition import ConditionMaker
from app.filter.unit import Unit

#=====================================
class CompHetsMarkupBatch:
    def __init__(self, proband_rel):
        setup_data = AnfisaConfig.configOption("comp-hets.setup")
        self.mF_zFamily = [setup_data["zygosity"] + '_' + str(member_idx)
            for member_idx in proband_rel]
        self.mF_Genes = setup_data["Genes"]
        self.mF_Result = setup_data["Compound_heterozygous"]
        self.mView_Result = setup_data["ws_compound_heterosygotes"]

        self.mGenesF = defaultdict(set)
        self.mGenesM = defaultdict(set)
        self.mCounts = [0, 0, 0]
        self.mResTab = None

    def feed(self, rec_no, rec_fdata):
        self.mCounts[0] += 1
        z_p, z_f, z_m = [rec_fdata[key] for key in self.mF_zFamily]
        if z_p == 1:
            if  z_f == 1 and z_m == 0:
                self._regIt(self.mGenesF, rec_no, rec_fdata)
                self.mCounts[1] += 1
            elif z_f == 0 and z_m == 1:
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

#=====================================
class CompHetsOperativeUnit(Unit):
    sSetupData = AnfisaConfig.configOption("comp-hets.setup")

    @classmethod
    def setupCondEnv(cls, cond_env, ds):
        var_names = cls.sSetupData["op-variables"][:]
        if not ds.getFamilyInfo() or len(ds.getFamilyInfo()) != 3:
            return False
        cond_env.addMode("trio")
        for nm in var_names:
            cond_env.addOperativeUnit(cls(ds, nm))
        return True

    def __init__(self, ds, name):
        Unit.__init__(self, {
            "name": name,
            "title": self.sSetupData.get("op-var-title", name),
            "kind": "enum",
            "vgroup": self.sSetupData["vgroup"],
            "research": False,
            "render": "operative",
            "no": -1})
        self.mDS = ds
        self.mIndex = ds.getIndex()

    def getDS(self):
        return self.mDS

    def _prepareZygConditions(self):
        dim0 = "%s_0" % self.sSetupData["zygosity"]
        dim1 = "%s_1" % self.sSetupData["zygosity"]
        dim2 = "%s_2" % self.sSetupData["zygosity"]
        return (
            ConditionMaker.condNum(dim0, [1, 1]),
            ["and", ConditionMaker.condNum(dim1, [1, 1]),
                ConditionMaker.condNum(dim2, [0, 0])],
            ["and", ConditionMaker.condNum(dim1, [0, 0]),
                ConditionMaker.condNum(dim2, [1, 1])])

    def compile(self, actual_cond_data = None, keep_actual = True):
        logging.info("Comp-hets: actual\n" +json.dumps(actual_cond_data))
        instr_and = ["and"]
        if not ConditionMaker.isAll(actual_cond_data):
            instr_and.append(actual_cond_data)
        c_proband, c_parent1, c_parent2 = self._prepareZygConditions()

        genes_unit = self.mIndex.getUnit(self.sSetupData["Genes"])
        genes1 = set()
        for gene, count in genes_unit.evalStat(
                self.mIndex.getCondEnv().parse(
                instr_and + [c_proband, c_parent1])):
            if count > 0:
                genes1.add(gene)
        logging.info("Eval genes1 for comp-hets: %d" % len(genes1))
        if len(genes1) == None:
            return ConditionMaker.condNone()
        genes2 = set()
        for gene, count in genes_unit.evalStat(
                self.mIndex.getCondEnv().parse(
                instr_and + [c_proband, c_parent2])):
            if count > 0:
                genes2.add(gene)
        logging.info("Eval genes2 for comp-hets: %d" % len(genes2))
        actual_genes = genes1 & genes2
        logging.info("Result genes for comp-hets: %d" % len(actual_genes))
        if len(actual_genes) == 0:
            return ConditionMaker.condNone()

        cond_genes_data = instr_and + [c_proband,
            ["or", c_parent1, c_parent2],
            ConditionMaker.condEnum(genes_unit.getName(),
            sorted(actual_genes))]
        cond_genes = self.mIndex.getCondEnv().parse(cond_genes_data)

        res_count = self.mIndex.evalTotalCount(cond_genes)
        logging.info("Eval count for comp-hets: %d" % res_count)

        if res_count == 0:
            return ConditionMaker.condNone()

        logging.info("Return gene-based cond")
        if not keep_actual and len(instr_and) > 1:
            del cond_genes_data[1]
        return ["genes", cond_genes_data]

    def makeCompStat(self, condition, calc_data, repr_context):
        ret = self.prepareStat()
        if len(calc_data) > 1:
            cond = self.mIndex.getCondEnv().parse(calc_data[1])
            if condition is not None:
                cond = condition.addAnd(cond)
            good_count = self.mIndex.evalTotalCount(cond)
        else:
            good_count = 0
        return ret + [[["True", good_count]]]

    def parseCondition(self, cond_data, comp_data):
        assert cond_data[1] == self.getName()
        if "True" in cond_data[3] and len(comp_data) > 1:
            cond = self.mIndex.getCondEnv().parse(comp_data[1])
        else:
            cond = self.mIndex.getCondEnv().getCondNone()
        if cond_data[2] == "not":
            return cond.negative()
        return cond

