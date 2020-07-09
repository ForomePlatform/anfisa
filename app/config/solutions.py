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

import os
from app.config.a_config import AnfisaConfig
from app.eval.condition import ConditionMaker
from app.model.sol_pack import SolutionPack
from app.model.tab_report import VariantsTabReportSchema
from .favor import FavorSchema
#===============================================
sCfgFilePath = os.path.dirname(os.path.abspath(__file__)) + "/files/"

def cfgPath(fname):
    global sCfgFilePath
    return sCfgFilePath + fname

def cfgPathSeq(fnames):
    return [cfgPath(fname) for fname in fnames]


#===============================================
sStdFMark = AnfisaConfig.configOption("filter.std.mark")
def stdNm(name):
    global sStdFMark
    return sStdFMark + name


#===============================================
sSolutionsAreSet = False

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
    return [
        ConditionMaker.condEnum("FT", ["PASS"]),
        ConditionMaker.condNum("Proband_GQ", min_val = 50),
        ConditionMaker.condNum("Min_GQ", min_val = 40),
        ConditionMaker.condNum("QD", min_val = 4),
        ConditionMaker.condNum("FS", max_val = 30)]

def impacting_splicing():
    return [ConditionMaker.condNum("splice_ai_dsmax", min_val = 0.2)]

#===============================================
def readySolutions():
    global sSolutionsAreSet
    if sSolutionsAreSet:
        return
    sSolutionsAreSet = True
    favor_pack = SolutionPack("FAVOR")
    setupSymbolPanels(favor_pack)
    FavorSchema.readySolutions(favor_pack)
    SolutionPack.regPack(favor_pack)

    base_pack = SolutionPack("CASE")
    setupSymbolPanels(base_pack)
    readySolutions_Case(base_pack)
    SolutionPack.regPack(base_pack)

#===============================================
def readySolutions_Case(base_pack):
    # BGM Filters, should belong to "Undiagnosed Patients Solution Pack"
    base_pack.regFilter("BGM_De_Novo", [
        condition_consequence_xBrowse(),
        ConditionMaker.condEnum("Callers", ["BGM_BAYES_DE_NOVO", "RUFUS"])],
        requires = {"trio_base", "WS"})

    base_pack.regFilter("BGM_Homozygous_Rec", [
        condition_consequence_xBrowse(),
        ConditionMaker.condEnum("Transcript_biotype", ["protein_coding"]),
        ConditionMaker.condEnum("Callers", ["BGM_HOM_REC"]),
        ConditionMaker.condEnum("Transcript_source", ["Ensembl"]),
        ConditionMaker.condFunc("Inheritance_Mode", dict(),
            ["Homozygous Recessive"])],
        requires = {"trio_base", "WS"})

    base_pack.regFilter("BGM_Compound_Het", [
        condition_consequence_xBrowse(),
        ConditionMaker.condEnum("Transcript_biotype", ["protein_coding"]),
        ConditionMaker.condEnum("Callers", ["BGM_CMPD_HET"]),
        ConditionMaker.condEnum("Transcript_source", ["Ensembl"]),
        ConditionMaker.condFunc("Compound_Het",
            {"approx": "transcript"}, ["Proband"])],
        requires = {"trio_base", "WS"})

    base_pack.regFilter("BGM_Autosomal_Dominant", [
        condition_consequence_xBrowse(),
        ConditionMaker.condEnum("Transcript_biotype", ["protein_coding"]),
        ConditionMaker.condEnum("Callers", ["BGM_DE_NOVO"]),
        ConditionMaker.condEnum("Transcript_source", ["Ensembl"])],
        requires = {"trio_base", "WS"})

    # Standard mendelian Filters, should belong to
    # "Undiagnosed Patients Solution Pack"
    base_pack.regFilter("X_Linked", condition_high_quality() + [
        condition_consequence_xBrowse(),
        ConditionMaker.condEnum("Transcript_biotype", ["protein_coding"]),
        ConditionMaker.condEnum("Transcript_source", ["Ensembl"]),
        ConditionMaker.condFunc("Inheritance_Mode", dict(), ["X-linked"])],
        requires = {"trio_base", "WS"})

    base_pack.regFilter("Mendelian_Homozygous_Rec",
        condition_high_quality() + [
            condition_consequence_xBrowse(),
            ConditionMaker.condEnum("Transcript_biotype", ["protein_coding"]),
            ConditionMaker.condEnum("Transcript_source", ["Ensembl"]),
            ConditionMaker.condFunc("Inheritance_Mode", dict(),
                ["Homozygous Recessive"])],
        requires = {"trio_base", "WS"})

    base_pack.regFilter("Mendelian_Compound_Het",
        condition_high_quality() + [
            condition_consequence_xBrowse(),
            ConditionMaker.condEnum("Transcript_biotype", ["protein_coding"]),
            ConditionMaker.condEnum("Transcript_source", ["Ensembl"]),
            ConditionMaker.condFunc("Compound_Het",
                {"approx": "transcript"}, ["Proband"])],
        requires = {"trio_base", "WS"})

    base_pack.regFilter("Mendelian_Auto_Dom",
        condition_high_quality() + [
            condition_consequence_xBrowse(),
            ConditionMaker.condEnum("Transcript_biotype", ["protein_coding"]),
            ConditionMaker.condEnum("Transcript_source", ["Ensembl"]),
            ConditionMaker.condFunc("Inheritance_Mode", dict(),
                ["Autosomal Dominant"])],
        requires = {"trio_base", "WS"})

    base_pack.regFilter("Impact_Splicing",
        condition_high_quality() + impacting_splicing())

    base_pack.regFilter("InSilico_Possibly_Damaging",
        condition_high_quality() + [
            ConditionMaker.condEnum("Rules",
                [stdNm("Possibly_Damaging_Predictions")])])

    base_pack.regFilter("InSilico_Damaging",
        condition_high_quality() + [
            ConditionMaker.condEnum("Rules",
                [stdNm("Damaging_Predictions")])])

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
    base_pack.regFilter("SEQaBOO_Hearing_Loss_v_4", [
        ConditionMaker.condEnum("Rules", [stdNm("Hearing Loss, v.4")])])
    base_pack.regFilter("SEQaBOO_Hearing_Loss_v_5", [
        ConditionMaker.condEnum("Rules", [stdNm("Hearing Loss, v.5")])])

    # SEQaBOO Filters, should belong to "Base Solution Pack"
    base_pack.regFilter("SEQaBOO_ACMG59", [
        ConditionMaker.condEnum("Rules", [stdNm("ACMG59")])])
    # base_pack.regFilter("SEQaBOO_ACMG59", [
    #     ConditionMaker.condEnum("Rules", [stdNm("SEQaBOO_ACMG59")]),
    #     ConditionMaker.condEnum("Rules", [stdNm("ACMG59")], "AND")],
    #     requires = {"WS"})

    base_pack.regFilter("Non_Synonymous", condition_high_quality() + [
        ConditionMaker.condEnum("Most_Severe_Consequence",
            NON_SYNONYMOUS_CSQ)])

    base_pack.regFilter("UTR_and_Worse", condition_high_quality() + [
        ConditionMaker.condEnum("Most_Severe_Consequence",
            LOW_IMPACT_CSQ, join_mode = "NOT")])

    base_pack.regFilter("Impacting_Splicing",
        condition_high_quality() + impacting_splicing())

    # Production Decision Trees
    base_pack.regDTree("BGM xBrowse Alt",
        cfgPathSeq(["bgm_xbrowse.pyt"]),
        requires = {"trio_base"})
    base_pack.regDTree("BGM_Strict",
        cfgPathSeq(["bgm_strict.pyt"]),
        requires = {"trio_base"})
    base_pack.regDTree("Trio Candidates",
        cfgPathSeq(["quality.pyt", "rare.pyt", "trio.pyt"]),
        requires = {"trio_base"})
    base_pack.regDTree("All Rare Variants",
        cfgPathSeq(["quality.pyt", "rare.pyt", "return_true.pyt"]))
    base_pack.regDTree("Hearing Loss, v.4",
        cfgPathSeq(["quality.pyt", "hearing_loss.pyt"]))
    base_pack.regDTree("Hearing Loss, v.5",
        cfgPathSeq(["quality.pyt", "hearing_loss_v5.pyt"]))
    base_pack.regDTree("ACMG59 Variants",
        cfgPathSeq(["quality.pyt", "acmg59.pyt"]))
    base_pack.regDTree("Damaging_Predictions",
        cfgPathSeq(["quality.pyt", "damaging.pyt"]))

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
    base_pack.regZone("Gene List", "Panels")
    base_pack.regZone("Sample", "Has_Variant")
    base_pack.regZone("Cohort", "Variant_in",  requires = {"cohorts"})
    base_pack.regZone("Tag", "_tags")

    demo_tab_schema = VariantsTabReportSchema("demo", use_tags = True)
    demo_tab_schema.addField("symbol", "/_view/general/genes[]")
    demo_tab_schema.addField("gnomAD_AF", "/_filters/gnomad_af_fam")
    base_pack.regTabSchema(demo_tab_schema)

#===============================================
def setupSymbolPanels(base_pack):
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
    # base_pack.regPanel("TTP1", "Symbol",
    #     cfgPath("ttp1.lst"))
    # base_pack.regPanel("TTP2", "Symbol",
    #     cfgPath("ttp2.lst"))
    # base_pack.regPanel("TTP3", "Symbol",
    #     cfgPath("ttp3.lst"))
    # base_pack.regPanel("TTP4", "Symbol",
    #     cfgPath("ttp4.lst"))

def completeDsModes(ds_h):
    if ds_h.getDataSchema() == "CASE":
        family_info = ds_h.getFamilyInfo()
        trio_seq = family_info.getTrioSeq()
        if trio_seq:
            ds_h.addModes({"trio"})
            if trio_seq[0][0] == "Proband":
                ds_h.addModes({"trio_base"})
                if len(family_info) == 3:
                    ds_h.addModes({"trio_pure"})
        if ds_h.getDataInfo()["meta"].get("cohorts"):
            ds_h.addModes({"cohorts"})
    elif ds_h.getDataSchema() == "FAVOR":
        FavorSchema.completeDsModes(ds_h)
