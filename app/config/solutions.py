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

import os, logging
from glob import glob
from app.eval.condition import ConditionMaker
from app.model.sol_pack import SolutionPack
from app.model.sol_support import StdNameSupport
from app.model.tab_report import ReportTabSchema
from .favor import FavorSchema
from app.config.view_op_tune import prepareSeqColorTransform
#===============================================
sCfgFilePath = os.path.dirname(os.path.abspath(__file__)) + "/files/"

def cfgPath(fname):
    global sCfgFilePath
    return sCfgFilePath + fname

def cfgPathSeq(fnames):
    return [cfgPath(fname) for fname in fnames]

def stdNm(name):
    return StdNameSupport.stdNm(name)


#===============================================
sSolutionsAreReady = False

LoF_CSQ = [
    "CNV: deletion",
    "transcript_ablation",
    "splice_acceptor_variant",
    "splice_donor_variant",
    "stop_gained",
    "frameshift_variant"
]

NON_SYNONYMOUS_CSQ = LoF_CSQ + [
    "inframe_insertion",
    "inframe_deletion",
    "missense_variant",
    "protein_altering_variant",
    "incomplete_terminal_codon_variant"
]

MODERATE_IMPACT_CSQ = NON_SYNONYMOUS_CSQ + [
    "synonymous_variant",
    "splice_region_variant",
    "coding_sequence_variant"
]

LOW_IMPACT_CSQ = [
    "intron_variant",
    "intergenic_variant",
    "non_coding_transcript_exon_variant",
    "upstream_gene_variant",
    "downstream_gene_variant",
    "TF_binding_site_variant",
    "regulatory_region_variant"
]

def condition_consequence_xBrowse():
    return ConditionMaker.condEnum("Transcript_consequence",
        MODERATE_IMPACT_CSQ)

def condition_high_quality():
    return (condition_high_confidence()
        + condition_high_quality_all_samples())

def condition_high_confidence_QD():
    return condition_good_confidence() + [
        ConditionMaker.condNum("QD", min_val = 4)]

def condition_high_confidence():
    return condition_good_confidence() + [
        ConditionMaker.condNum("QUAL", min_val = 40)]

def condition_good_confidence():
    return [
        ConditionMaker.condEnum("FT", ["PASS"]),
        ConditionMaker.condNum("Max_GQ", min_val = 50),
        ConditionMaker.condNum("FS", max_val = 30)]

def condition_high_quality_all_samples():
    return [ConditionMaker.condNum("Min_GQ", min_val = 40)]

def condition_all_genotypes_called():
    return [ConditionMaker.condNum("Num_NO_CALL", max_val = 0)]

def impacting_splicing():
    return [ConditionMaker.condNum("splice_ai_dsmax", min_val = 0.2)]

def clinVar_not_benign():
    return [ConditionMaker.condEnum("Clinvar_Trusted_Simplified",
        ["benign"], "NOT")]

#===============================================
def checkSolutionUnits(sol_kind, sol_name, unit_names, requires):
    if "Rules" in unit_names:
        if not requires or "WS" not in requires:
            logging.error(
                'Solution %s/%s: "WS" must be set as requirement (uses Rules)'
                % (sol_kind, sol_name))
            return False
    if "Compound_Het" in unit_names:
        if (not requires
                or len({"trio", "trio_base", "trio_pure"} & requires) == 0):
            logging.error(
                ('Solution %s/%s: "trio"/"trio_base"/"trio_pure" must be set'
                ' as requirement (uses Compound_Het)')
                % (sol_kind, sol_name))
            return False
    return True

#===============================================
def solutionsAreReady():
    global sSolutionsAreReady
    return sSolutionsAreReady

def setupSolutions(app_config):
    global sSolutionsAreReady
    if sSolutionsAreReady:
        return
    sSolutionsAreReady = True
    favor_pack = SolutionPack("FAVOR", checkSolutionUnits)
    setupGenericPack(app_config, favor_pack)
    FavorSchema.setupSolutions(app_config, favor_pack)

    base_pack = SolutionPack("CASE", checkSolutionUnits)
    setupGenericPack(app_config, base_pack)
    setupSolutions_Case(app_config, base_pack)

#===============================================
def setupSolutions_Case(app_config, base_pack):
    # BGM Filters, should belong to "Undiagnosed Patients Solution Pack"
    base_pack.regFilter("BGM_De_Novo", [
        condition_consequence_xBrowse(),
        ConditionMaker.condEnum("Callers", ["BGM_BAYES_DE_NOVO", "RUFUS"])],
        requires = {"trio_base", "WS"}, rubric = "Test-A")

    base_pack.regFilter("BGM_Homozygous_Rec", [
        condition_consequence_xBrowse(),
        ConditionMaker.condEnum("Transcript_biotype", ["protein_coding"]),
        ConditionMaker.condEnum("Callers", ["BGM_HOM_REC"]),
        ConditionMaker.condEnum("Transcript_source", ["Ensembl"]),
        ConditionMaker.condFunc("Inheritance_Mode", dict(),
            ["Homozygous Recessive"])],
        requires = {"trio_base", "WS"}, rubric = "Test-A")

    base_pack.regFilter("BGM_Compound_Het", [
        condition_consequence_xBrowse(),
        ConditionMaker.condEnum("Transcript_biotype", ["protein_coding"]),
        ConditionMaker.condEnum("Callers", ["BGM_CMPD_HET"]),
        ConditionMaker.condEnum("Transcript_source", ["Ensembl"]),
        ConditionMaker.condFunc("Compound_Het",
            {"approx": "transcript"}, ["Proband"])],
        requires = {"trio_base", "WS"}, rubric = "Test-A")

    base_pack.regFilter("BGM_Autosomal_Dominant", [
        condition_consequence_xBrowse(),
        ConditionMaker.condEnum("Transcript_biotype", ["protein_coding"]),
        ConditionMaker.condEnum("Callers", ["BGM_DE_NOVO"]),
        ConditionMaker.condEnum("Transcript_source", ["Ensembl"])],
        requires = {"trio_base", "WS"}, rubric = "Test-A")

    # Standard mendelian Filters, should belong to
    # "Undiagnosed Patients Solution Pack"
    base_pack.regFilter("X_Linked", condition_high_quality() + [
        condition_consequence_xBrowse(),
        ConditionMaker.condEnum("Transcript_biotype", ["protein_coding"]),
        ConditionMaker.condEnum("Transcript_source", ["Ensembl"]),
        ConditionMaker.condFunc("Inheritance_Mode", dict(), ["X-linked"])],
        requires = {"trio_base", "WS"}, rubric = "Test-B")

    base_pack.regFilter("Mendelian_Homozygous_Rec",
        condition_high_quality() + condition_all_genotypes_called()
        + clinVar_not_benign() + [
            condition_consequence_xBrowse(),
            ConditionMaker.condEnum("Transcript_biotype", ["protein_coding"]),
            ConditionMaker.condEnum("Transcript_source", ["Ensembl"]),
            ConditionMaker.condFunc("Inheritance_Mode", dict(),
                ["Homozygous Recessive"]),
            ConditionMaker.condEnum("Proband_Zygosity", ["Homozygous"])
        ],
        requires = {"trio_base", "WS"}, rubric = "Test-B")

    base_pack.regFilter("Mendelian_Compound_Het",
        condition_high_quality() + clinVar_not_benign() + [
            condition_consequence_xBrowse(),
            ConditionMaker.condEnum("Transcript_biotype", ["protein_coding"]),
            ConditionMaker.condEnum("Transcript_source", ["Ensembl"]),
            ConditionMaker.condFunc("Compound_Het",
                {"approx": "transcript"}, ["Proband"])],
        requires = {"trio_base", "WS"}, rubric = "Test-B")

    base_pack.regFilter("Mendelian_Auto_Dom",
        condition_high_quality() + clinVar_not_benign() + [
            condition_consequence_xBrowse(),
            ConditionMaker.condEnum("Transcript_biotype", ["protein_coding"]),
            ConditionMaker.condEnum("Transcript_source", ["Ensembl"]),
            ConditionMaker.condFunc("Inheritance_Mode", dict(),
                ["Autosomal Dominant"]),
            ConditionMaker.condEnum("Proband_Zygosity", ["Heterozygous"])
        ],
        requires = {"trio_base", "WS"}, rubric = "Test-B")

    base_pack.regFilter("InSilico_Possibly_Damaging",
        condition_high_confidence() + [ConditionMaker.condEnum(
            "Rules", [stdNm("Possibly_Damaging_Predictions")])],
        requires = {"WS"}, rubric = "Test-C")

    base_pack.regFilter("InSilico_Damaging", condition_high_confidence()
        + [ConditionMaker.condEnum("Rules",
            [stdNm("Damaging_Predictions")])],
        requires = {"WS"}, rubric = "Test-C")

    # SEQaBOO Filters, should belong to "Hearing Loss Solution Pack"
    # base_pack.regFilter("SEQaBOO_Hearing_Loss_v_01", [
    #     ConditionMaker.condEnum("Rules",
    #        [stdNm("SEQaBOO_Hearing_Loss_v_01")]),
    #     ConditionMaker.condEnum("Rules", [stdNm("ACMG59")], "NOT")],
    #     requires = {"WS"})
    # base_pack.regFilter("SEQaBOO_Hearing_Loss_v_02", [
    #     ConditionMaker.condEnum("Rules",
    #        [stdNm("SEQaBOO_Hearing_Loss_v_02")]),
    #     ConditionMaker.condEnum("Rules", [stdNm("ACMG59")], "NOT")],
    #     requires = {"WS"})
    # base_pack.regFilter("SEQaBOO_Hearing_Loss_v_03", [
    #     ConditionMaker.condEnum("Rules",
    #        [stdNm("SEQaBOO_Hearing_Loss_v_03")]),
    #     ConditionMaker.condEnum("Rules", [stdNm("ACMG59")], "NOT")],
    #     requires = {"WS"})
    # base_pack.regFilter("SEQaBOO_Hearing_Loss_v_03_5", [
    #     ConditionMaker.condEnum("Rules",
    #        [stdNm("SEQaBOO_Hearing_Loss_v_03")]),
    #     ConditionMaker.condEnum("Panels", ["All_Hearing_Loss"])],
    #     requires = {"WS"})
    # base_pack.regFilter("SEQaBOO_Hearing_Loss_v_4", [
    #     ConditionMaker.condEnum("Rules", [stdNm("Hearing Loss, v.4")])],
    #     requires = {"WS"})
    base_pack.regFilter("SEQaBOO_Hearing_Loss_v_5", [
        ConditionMaker.condEnum("Rules", [stdNm("Hearing Loss, v.5")])],
        requires = {"WS"}, rubric = "Test-C")
    base_pack.regFilter("SEQaBOO_Hearing_Quick", [
        ConditionMaker.condEnum("Rules", [stdNm("Hearing Loss Quick")])],
        requires = {"WS"}, rubric = "Test-C")

    # SEQaBOO Filters, should belong to "Base Solution Pack"
    base_pack.regFilter("SEQaBOO_ACMG59", [
        ConditionMaker.condEnum("Rules", [stdNm("ACMG59")])],
        requires = {"WS"}, rubric = "Test-C")
    # base_pack.regFilter("SEQaBOO_ACMG59", [
    #     ConditionMaker.condEnum("Rules", [stdNm("SEQaBOO_ACMG59")]),
    #     ConditionMaker.condEnum("Rules", [stdNm("ACMG59")], "AND")],
    #     requires = {"WS"})

    base_pack.regFilter("Loss_Of_Function", condition_high_quality() + [
        ConditionMaker.condEnum("Most_Severe_Consequence", LoF_CSQ)])

    base_pack.regFilter("Non_Synonymous", condition_high_quality() + [
        ConditionMaker.condEnum("Most_Severe_Consequence",
            NON_SYNONYMOUS_CSQ)])

    base_pack.regFilter("UTR_and_Worse", condition_high_quality() + [
        ConditionMaker.condEnum("Most_Severe_Consequence",
            LOW_IMPACT_CSQ, join_mode = "NOT")])

    base_pack.regFilter("Impact_Splicing",
        condition_high_confidence() + impacting_splicing())

    base_pack.regFilter("ClinVar_VUS_or_Worse",
        condition_high_confidence() + [
            ConditionMaker.condEnum("Clinvar_stars",  ["1", "2", "3", "4"]),
            ConditionMaker.condEnum("Clinvar_conflicts", ["True"],
                                    join_mode = "NOT"),
            ConditionMaker.condEnum("Clinvar_Benign", ["VUS or Pathogenic"])
        ], requires={"XL"})

    base_pack.regFilter("In_Silico_Damaging",
        condition_high_confidence() + [
            ConditionMaker.condEnum("Polyphen_2_HVAR",  ["D"]),
            ConditionMaker.condEnum("SIFT", ["deleterious"])
        ], requires={"XL"})

    # base_pack.regFilter("Impact_Splicing",
    #     condition_high_quality() + impacting_splicing())

    # Production Decision Trees
    base_pack.regDTree("BGM Research",
        cfgPathSeq(["bgm_xbrowse.pyt"]),
        requires = {"trio_base"}, rubric = "Test-A")
    base_pack.regDTree("BGM Red Button",
        cfgPathSeq(["bgm_strict.pyt"]),
        requires = {"trio_base"}, rubric = "Test-A")
    base_pack.regDTree("Trio Candidates",
        cfgPathSeq(["quality.pyt", "rare.pyt", "trio.pyt"]),
        requires = {"trio_base"}, rubric = "Test-A")
    base_pack.regDTree("All Rare Variants",
        cfgPathSeq(["quality.pyt", "rare.pyt", "return_true.pyt"]))
    # base_pack.regDTree("Hearing Loss, v.4",
    #    cfgPathSeq(["quality.pyt", "hearing_loss.pyt"]))
    base_pack.regDTree("Hearing Loss, v.5",
        cfgPathSeq(["quality.pyt", "hearing_loss_v5.pyt"]),
        rubric = "Test-B")
    base_pack.regDTree("Hearing Loss Quick",
        cfgPathSeq(["quality.pyt", "hearing_loss_ws.pyt"]),
        requires = {"WS"}, rubric = "Test-B")
    base_pack.regDTree("ACMG59 Variants",
        cfgPathSeq(["quality.pyt", "acmg59.pyt"]),
        rubric = "Test-B")
    base_pack.regDTree("Damaging_Predictions",
        cfgPathSeq(["damaging.pyt"]), rubric = "Test-C")
    base_pack.regDTree("Possibly_Damaging_Predictions",
        cfgPathSeq(["possibly_damaging.pyt"]), rubric = "Test-C")

    # Test trees
    # base_pack.regDTree("Q Test",
    #     cfgPathSeq(["quality.pyt", "return_true.pyt"]))
    # base_pack.regDTree("R Test",
    #     cfgPathSeq(["rare.pyt", "return_true.pyt"]))
    # base_pack.regDTree("T Test",
    #     [cfgPath("trio.pyt")],
    #     requires = {"trio_base"})
    # base_pack.regDTree("H Test",
    #     [cfgPath("hearing_loss.pyt")])

    base_pack.regZone("Gene", "Symbol")
    base_pack.regZone("Gene List", "Gene_Lists")
    base_pack.regZone("Sample", "Has_Variant")
    base_pack.regZone("Cohort", "Variant_in",  requires = {"cohorts"})
    base_pack.regZone("Tag", "_tags")

    demo_tab_schema = ReportTabSchema("demo", use_tags = True)
    demo_tab_schema.addField("gene(s)", "/_view/general/genes[]")
    demo_tab_schema.addField("variant", "/__data/label")
    demo_tab_schema.addField("gnomAD_AF", "/_filters/gnomad_af_fam")
    base_pack.regTabSchema(demo_tab_schema)

#===============================================
def setupGenericPack(app_config, base_pack):
    setupInstanceSolutions(app_config, base_pack)

    base_pack.regItemDict("Clinvar_Trusted_Submitters", {
        "Laboratory for Molecular Medicine, "
        + "Partners HealthCare Personalized Medicine": "LMM",
        "GeneDx":   "GeneDx",
        "Invitae":  "Invitae"})

    base_pack.regPanel("ACMG59", "Symbol",
        cfgPath("acmg59.lst"))
    base_pack.regPanel("All_Hearing_Loss", "Symbol",
        cfgPath("all_hearing_loss.lst"))
    base_pack.regPanel("Reportable_Hearing_Loss", "Symbol",
        cfgPath("rep_hearing_loss.lst"))
    base_pack.regPanel("Complement_System", "Symbol",
        cfgPath("complement_system.lst"))
    base_pack.regPanel("PharmGKB_VIP", "Symbol",
        cfgPath("pharmgkb_vip.lst"))
    base_pack.regPanel("Coagulation_System", "Symbol",
        cfgPath("coagulation_system.lst"))
    base_pack.regPanel("Thrombotic_Thrombocytopenic_Purpura", "Symbol",
        cfgPath("ttp.lst"))
    base_pack.regPanel("Immune_Dysregulation", "Symbol",
        cfgPath("immune_dysregulation.lst"))
    base_pack.regPanel("Autism_Spectrum", "Symbol",
        cfgPath("autism.lst"))
    base_pack.regPanel("Holoprosencephaly", "Symbol",
        cfgPath("hpe.lst"))
    base_pack.regPanel("Tubulinopathies", "Symbol",
        cfgPath("tubulinopathies.lst"))
    base_pack.regPanel("Notch_Signaling_Pathway", "Symbol",
        cfgPath("notch.lst"))
    base_pack.regPanel("SSH1_Interactors", "Symbol",
        cfgPath("ssh.lst"))
    base_pack.regPanel("Wnt1_Interactors", "Symbol",
        cfgPath("wnt.lst"))

    base_pack.regPanel("Check-Tags", "_tags", items = [
        "Previously categorized",
        "Previously Triaged",
        "Not categorized",
        "Benign/Likely benign",
        "False positives"]
    )

    csv_tab_schema = ReportTabSchema("csv", use_tags = False)
    csv_tab_schema.addField("chromosome", "/_filters/chromosome")
    csv_tab_schema.addMustiStrField("variant", "|", [
        "/_filters/chromosome",
        "/_filters/start",
        "/_filters/ref",
        "/_filters/alt"])
    base_pack.regTabSchema(csv_tab_schema)

    xbr_tab_schema = ReportTabSchema("xbr", use_tags = True)
    xbr_tab_schema.addField("ClinVar", "/__data/clinvar_significance")
    xbr_tab_schema.addField("HGMD", "/_view/databases/hgmd_tags")
    # xbr_tab_schema.addField("Gene", "/_view/general/genes")
    xbr_tab_schema.addMustiStrField("Coordinate", ":", [
        "/_filters/chromosome",
        "/_filters/start"])
    xbr_tab_schema.addMustiStrField("Change", ">", [
        "/_filters/ref",
        "/_filters/alt"])

    xbr_tab_schema.addField("MSQ", "/_view/general/canonical_annotation")
    xbr_tab_schema.addField("Protein Change", "/_view/general/ppos_canonical")
    xbr_tab_schema.addField("Polyphen2_HVAR",
        "/_view/predictions/polyphen2_hvar",
        prepareSeqColorTransform("Polyphen"))
    xbr_tab_schema.addField("Polyphen2_HDIV",
        "/_view/predictions/polyphen2_hdiv",
        prepareSeqColorTransform("Polyphen"))
    xbr_tab_schema.addField("SIFT",
        "/_view/predictions/sift",
        prepareSeqColorTransform("SIFT"))
    xbr_tab_schema.addField("MUT TASTER",
        "/_view/predictions/mutation_taster",
        prepareSeqColorTransform("MutationTaster"))
    xbr_tab_schema.addField("FATHMM", "/_view/predictions/fathmm",
        prepareSeqColorTransform("FATHMM"))

    xbr_tab_schema.addField("gnomAD_Overall_AF", "/_filters/gnomad_af_fam")
    xbr_tab_schema.addField("gnomAD_Overall_AF_Popmax",
        "/_filters/gnomad_popmax_af")
    xbr_tab_schema.addField("gnomAD_Genomes_AF",
        "/_filters/gnomad_db_genomes_af")
    xbr_tab_schema.addField("gnomAD_Exomes_AF",
        "/_filters/gnomad_db_exomes_af")
    xbr_tab_schema.addField("gnomAD_Overall_Hom", "/_filters/gnomad_hom")
    xbr_tab_schema.addField("gnomAD_Overall_Hem", "/_filters/gnomad_hem")

    xbr_tab_schema.addField("QD", "/_filters/qd")
    xbr_tab_schema.addField("FT", "/_filters/filters")

    xbr_tab_schema.addNamedAttr("ColorCode")
    xbr_tab_schema.addNamedAttr("GTEx")
    xbr_tab_schema.addNamedAttr("IGV")
    xbr_tab_schema.addNamedAttr("gnomAD")
    xbr_tab_schema.addNamedAttr("Samples")
    xbr_tab_schema.addNamedAttr("GeneColored")

    base_pack.regTabSchema(xbr_tab_schema)

#===============================================
def setupInstanceSolutions(app_config, base_pack):
    solutions_info = app_config.get("solutions")
    if solutions_info is None:
        return
    panels_info = solutions_info.get("panels")
    if panels_info is None:
        return
    for panel_type, panel_info in panels_info.items():
        dir_pass = panel_info["dir"]
        if not os.path.exists(dir_pass):
            logging.error("Panel directory %s for type %s does not exists"
                % (dir_pass, panel_type))
            continue
        for file_name in glob(dir_pass + "/*.lst"):
            panel_name = file_name.rpartition('/')[2].rpartition('.')[0]
            base_pack.regPanel(panel_name, panel_type, file_name)


#===============================================
def startTune(ds_h):
    if ds_h.getDataSchema() == "FAVOR":
        FavorSchema.startTune(ds_h)
