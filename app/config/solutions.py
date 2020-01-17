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
from app.eval.condition import ConditionMaker
from app.model.sol_pack import SolutionPack
#===============================================
sCfgFilePath = os.path.dirname(os.path.abspath(__file__)) + "/files/"

def cfgPath(fname):
    global sCfgFilePath
    return sCfgFilePath + fname

def cfgPathSeq(fnames):
    return [cfgPath(fname) for fname in fnames]


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
    return ConditionMaker.condEnum("Transctipt_consequence",
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

def readySolutions():
    global sSolutionsAreSet
    if sSolutionsAreSet:
        return
    sSolutionsAreSet = True
    base_pack = SolutionPack("BASE")
    SolutionPack.regDefaultPack(base_pack)
    SolutionPack.regPack(base_pack)

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
                ["Possibly_Damaging_Predictions"])],
        requires = {"WS"})

    base_pack.regFilter("InSilico_Damaging",
        condition_high_quality() + [
            ConditionMaker.condEnum("Rules", ["Damaging_Predictions"])],
        requires = {"WS"})

    # SEQaBOO Filters, should belong to "Hearing Loss Solution Pack"
    base_pack.regFilter("SEQaBOO_Hearing_Loss_v_01", [
        ConditionMaker.condEnum("Rules", ["SEQaBOO_Hearing_Loss_v_01"]),
        ConditionMaker.condEnum("Rules", ["ACMG59"], "NOT")],
        requires = {"WS"})
    base_pack.regFilter("SEQaBOO_Hearing_Loss_v_02", [
        ConditionMaker.condEnum("Rules", ["SEQaBOO_Hearing_Loss_v_02"]),
        ConditionMaker.condEnum("Rules", ["ACMG59"], "NOT")],
        requires = {"WS"})
    base_pack.regFilter("SEQaBOO_Hearing_Loss_v_03", [
        ConditionMaker.condEnum("Rules", ["SEQaBOO_Hearing_Loss_v_03"]),
        ConditionMaker.condEnum("Rules", ["ACMG59"], "NOT")],
        requires = {"WS"})
    base_pack.regFilter("SEQaBOO_Hearing_Loss_v_03_5", [
        ConditionMaker.condEnum("Rules", ["SEQaBOO_Hearing_Loss_v_03"]),
        ConditionMaker.condEnum("Panels", ["All_Hearing_Loss"])],
        requires = {"WS"})

    # SEQaBOO Filters, should belong to "Base Solution Pack"
    base_pack.regFilter("SEQaBOO_ACMG59", [
        ConditionMaker.condEnum("Rules", ["SEQaBOO_ACMG59"]),
        ConditionMaker.condEnum("Rules", ["ACMG59"], "AND")],
        requires = {"WS"})

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
    base_pack.regDTree("Trio Candidates",
        cfgPathSeq(["quality.pyt", "rare.pyt", "trio.pyt"]),
        requires = {"trio_base"})
    base_pack.regDTree("All Rare Variants",
        cfgPathSeq(["quality.pyt", "rare.pyt", "return_true.pyt"]))
    base_pack.regDTree("Hearing Loss, v.4",
        cfgPathSeq(["quality.pyt", "hearing_loss.pyt"]))
    base_pack.regDTree("Hearing Loss, v.5",
        cfgPathSeq(["quality.pyt", "hearing_loss_v5.pyt"]))
    base_pack.regDTree("ACMG59",
        cfgPathSeq(["quality.pyt", "acmg59.pyt"]))

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

    base_pack.regPanel("Symbol", "ACMG59",
        cfgPath("acmg59.lst"))
    base_pack.regPanel("Symbol", "All_Hearing_Loss",
        cfgPath("all_hearing_loss.lst"))
    base_pack.regPanel("Symbol", "Reportable_Hearing_Loss",
        cfgPath("rep_hearing_loss.lst"))
    base_pack.regPanel("Symbol", "Purpura_Fulminans",
        cfgPath("purpura_fulminans.lst"))
    base_pack.regPanel("Symbol", "PharmGKB_VIP",
        cfgPath("pharmgkb_vip.lst"))
    base_pack.regPanel("Symbol", "Coagulation_System",
        cfgPath("coagulation_system.lst"))
    base_pack.regPanel("Symbol", "Thrombotic_Thrombocytopenic_Purpura",
        cfgPath("ttp.lst"))
    base_pack.regPanel("Symbol", "Immune_Dysregulation",
        cfgPath("immune_dysregulation.lst"))
    base_pack.regPanel("Symbol", "Autism Spectrum",
        cfgPath("autism.lst"))
    # base_pack.regPanel("Symbol", "TTP1",
    #     cfgPath("ttp1.lst"))
    # base_pack.regPanel("Symbol", "TTP2",
    #     cfgPath("ttp2.lst"))
    # base_pack.regPanel("Symbol", "TTP3",
    #     cfgPath("ttp3.lst"))
    # base_pack.regPanel("Symbol", "TTP4",
    #     cfgPath("ttp4.lst"))

    base_pack.regZone("Gene", "Symbol")
    base_pack.regZone("Gene List", "Panels")
    base_pack.regZone("Sample", "Has_Variant")
    base_pack.regZone("Cohort", "Variant_in",  requires = {"cohorts"})
    base_pack.regZone("Tag", "_tags")


def completeDsModes(ds_h):
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
