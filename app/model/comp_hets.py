import logging, json

from app.config.a_config import AnfisaConfig
from app.filter.condition import ConditionMaker
from app.filter.unit import Unit

#=====================================
class CompHetsOperativeUnit(Unit):
    sSetupData = AnfisaConfig.configOption("comp-hets.setup")

    @classmethod
    def setupCondEnv(cls, cond_env, ds):
        trio_seq = ds.getFamilyInfo().getTrioSeq()
        if not trio_seq:
            return False
        if trio_seq[0][0] == "Proband":
            cond_env.addMode("trio_base")
            if len(ds.getFamilyInfo()) == 3:
                cond_env.addMode("trio_pure")
        cond_env.addMode("trio")
        for nm in cls.sSetupData["op-variables"]:
            cond_env.addOperativeUnit(CompHetsOperativeUnit(ds, nm))
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

