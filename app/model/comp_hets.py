import logging

from app.config.a_config import AnfisaConfig
from app.filter.unit import Unit, ComplexEnumSupport

#=====================================
class CompHetsOperativeUnit(Unit, ComplexEnumSupport):
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

        for var_info in cls.sSetupData["op-variables." + cond_env.getKind()]:
            name, gene_unit = var_info[:2]
            title = var_info[2] if len(var_info) > 2 else name
            cond_env.addOperativeUnit(
                CompHetsOperativeUnit(ds, name, gene_unit, title))
        return True

    def __init__(self, ds, name, gene_unit, title):
        Unit.__init__(self, {
            "name": name,
            "title": title,
            "kind": "enum",
            "vgroup": self.sSetupData["vgroup"],
            "research": False,
            "render": "operative",
            "no": -1})
        self.mDS = ds
        self.mIndex = ds.getIndex()
        self.mCondEnv = self.mIndex.getCondEnv()
        self.mZygUnit = self.mIndex.getUnit(self.sSetupData["zygosity.unit"])
        self.mGeneUnit = self.mIndex.getUnit(gene_unit)

    def getDS(self):
        return self.mDS

    def _prepareZygConditions(self, trio_info):
        zyg_base, zyg_father, zyg_mother = [
            self.mZygUnit.getFamUnit(idx) for idx in trio_info[1:]]
        return [self.mCondEnv.makeNumericCond(zyg_base, [1, 1]),
            self.mCondEnv.joinAnd([
                self.mCondEnv.makeNumericCond(zyg_father, [1, 1]),
                self.mCondEnv.makeNumericCond(zyg_mother, [0, 0])]),
            self.mCondEnv.joinAnd([
                self.mCondEnv.makeNumericCond(zyg_mother, [1, 1]),
                self.mCondEnv.makeNumericCond(zyg_father, [0, 0])])]

    def prepareImport(self, actual_condition):
        ret = dict()
        for trio_info in self.mDS.getFamilyInfo().getTrioSeq():
            self._prepareTrio(trio_info, actual_condition, ret)
        return ret

    def _prepareTrio(self, trio_info, actual_condition, ret):
        logging.info("Comp-hets eval for %s" % trio_info[0])
        c_proband, c_father, c_mother = self._prepareZygConditions(trio_info)

        genes1 = set()
        for gene, count in self.mGeneUnit.evalStat(self.mCondEnv.joinAnd(
                [actual_condition, c_proband, c_father])):
            if count > 0:
                genes1.add(gene)
        logging.info("Eval genes1 for %s comp-hets: %d" %
            (trio_info[0], len(genes1)))
        if len(genes1) == None:
            return
        genes2 = set()
        for gene, count in self.mGeneUnit.evalStat(self.mCondEnv.joinAnd(
                [actual_condition, c_proband, c_mother])):
            if count > 0:
                genes2.add(gene)
        logging.info("Eval genes2 for %s comp-hets: %d" %
            (trio_info[0], len(genes2)))
        actual_genes = genes1 & genes2
        logging.info("Result genes for comp-hets: %d" % len(actual_genes))
        if len(actual_genes) == 0:
            return
        ret[trio_info[0]] = sorted(actual_genes)

    def iterComplexCriteria(self, context, variants = None):
        for trio_info in self.mDS.getFamilyInfo().getTrioSeq():
            if variants is not None and trio_info[0] not in variants:
                continue
            gene_seq = context.get(trio_info[0])
            if not gene_seq:
                continue
            c_proband, c_father, c_mother = self._prepareZygConditions(
                trio_info)
            yield trio_info[0], self.mCondEnv.joinAnd([
                c_proband, c_father.addOr(c_mother),
                self.mCondEnv.makeEnumCond(self.mGeneUnit, "", gene_seq)])

    def makeCompStat(self, condition, calc_data, repr_context):
        ret = self.prepareStat()
        if self.mGeneUnit.isDetailed():
            ret[1]["detailed"] = True
        ret.append(self.collectComplexStat(self.mIndex, condition,
            calc_data, detailed = self.mGeneUnit.isDetailed()))
        return ret

    def parseCondition(self, cond_data, calc_data):
        return self.makeComplexCondition(
            cond_data[2], cond_data[3], calc_data)

