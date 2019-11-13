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

def evalRec(env, rec):
    """hearing_loss_genes"""
    return (len(set(rec.Symbol) &
        {
            'ABCD1',
            'ABHD12',
            'ABHD5',
            'ACOT13',
            'ACTB',
            'ACTG1',
            'ADCY1',
            'ADGRV1',
            'ADK',
            'AIFM1',
            'AK2',
            'ALMS1',
            'AMMECR1',
            'ANKH',
            'ARSB',
            'ATP13A4',
            'ATP2B2',
            'ATP2C2',
            'ATP6V1B1',
            'ATP6V1B2',
            'BCAP31',
            'BCS1L',
            'BDNF',
            'BDP1',
            'BSND',
            'BTD',
            'CABP2',
            'CACNA1C',
            'CACNA1D',
            'CATSPER2',
            'CCDC50',
            'CD151',
            'CD164',
            'CDC14A',
            'CDC42',
            'CDH23',
            'CDKN1C',
            'CEACAM16',
            'CEP78',
            'CEP152',
            'CFTR',
            'CHD7',
            'CHSY1',
            'CIB2',
            'CISD2',
            'CLCNKA',
            'CLCNKB',
            'CLDN14',
            'CLIC5',
            'CLPP',
            'CLRN1',
            'CMIP',
            'CNTNAP2',
            'COCH',
            'COL11A1',
            'COL11A2',
            'COL2A1',
            'COL4A3',
            'COL4A4',
            'COL4A5',
            'COL4A6',
            'COL9A1',
            'COL9A2',
            'COL9A3',
            'CRYL1',
            'CRYM',
            'CYP19A1',
            'DCAF17',
            'DCDC2',
            'DCDC2',
            'DIABLO',
            'DIAPH1',
            'DIAPH3',
            'DLX5',
            'DMXL2',
            'DNMT1',
            'DOCK4',
            'DRD2',
            'DSPP',
            'DYX1C1',
            'EDN3',
            'EDNRB',
            'ELMOD3',
            'EPS8',
            'EPS8L2',
            'ERCC2',
            'ERCC3',
            'ESPN',
            'ESRP1',
            'ESRRB',
            'EYA1',
            'EYA4',
            'FAM189A2',
            'FDXR',
            'FGF3',
            'FGFR1',
            'FGFR2',
            'FGFR3',
            'FKBP14',
            'FOXC1',
            'FOXF2',
            'FOXI1',
            'FOXP1',
            'FOXP2',
            'FOXRED1',
            'FRMPD4',
            'GAA',
            'GATA3',
            'GCFC2',
            'GIPC3',
            'GJA1',
            'GJB1',
            'GJB2',
            'GJB3',
            'GJB6',
            'GNPTAB',
            'GNPTG',
            'GPLD1',
            'GPSM2',
            'GRAP',
            'GREB1L',
            'GRHL2',
            'GRXCR1',
            'GRXCR2',
            'GSDME',
            'GSTP1',
            'GTPBP3',
            'HAAO',
            'HARS',
            'HARS2',
            'HGF',
            'HOMER1',
            'HOMER2',
            'HOXA2',
            'HOXB1',
            'HSD17B4',
            'HTRA2',
            'IARS2',
            'IDS',
            'IGF1',
            'ILDR1',
            'JAG1',
            'KARS',
            'KCNE1',
            'KCNJ10',
            'KCNQ1',
            'KCNQ4',
            'KIAA0319',
            'KIT',
            'KITLG',
            'LARS2',
            'LHFPL5',
            'LHX3',
            'LMX1A',
            'LOXHD1',
            'LOXL3',
            'LRP2',
            'LRTOMT',
            'MANBA',
            'MARVELD2',
            'MASP1',
            'MCM2',
            'MET',
            'MFN2',
            'MIR182',
            'MIR183',
            'MIR96',
            'MITF',
            'MPZL2',
            'MRPL19',
            'MSRB3',
            'MTAP',
            'MTO1',
            'MTRNR1',
            'MTTK',
            'MTTL1',
            'MTTS1',
            'MYH14',
            'MYH9',
            'MYO15A',
            'MYO1A',
            'MYO1C',
            'MYO1F',
            'MYO3A',
            'MYO6',
            'MYO7A',
            'NAGPA',
            'NARS2',
            'NDP',
            'NDUFA1',
            'NDUFA11',
            'NDUFAF1',
            'NDUFAF2',
            'NDUFAF3',
            'NDUFAF4',
            'NDUFAF5',
            'NDUFB11',
            'NDUFB3',
            'NDUFB9',
            'NDUFS1',
            'NDUFS2',
            'NDUFS3',
            'NDUFS4',
            'NDUFS6',
            'NDUFV1',
            'NDUFV2',
            'NF2',
            'NLRP3',
            'NOTCH2',
            'NRSN1',
            'NUBPL',
            'OPA1',
            'ORC1',
            'OSBPL2',
            'OTOA',
            'OTOF',
            'OTOG',
            'OTOGL',
            'P2RX2',
            'PAX2',
            'PAX3',
            'PCDH15',
            'PDE1C',
            'PDZD7',
            'PEX1',
            'PEX6',
            'PITX2',
            'PJVK',
            'PMP22',
            'PNPT1',
            'POLG',
            'POLR1C',
            'POLR1D',
            'POU3F4',
            'POU4F3',
            'PRPS1',
            'PTPRQ',
            'RDX',
            'RIPOR2',
            'RMND1',
            'ROBO1',
            'ROR1',
            'RPS6KA3',
            'S1PR2',
            'SALL1',
            'SALL4',
            'SEMA3E',
            'SERAC1',
            'SERPINB6',
            'SETBP1',
            'SGPL1',
            'SF3B4',
            'SIX1',
            'SIX5',
            'SLC12A1',
            'SLC17A8',
            'SLC19A2',
            'SLC22A4',
            'SLC26A4',
            'SLC26A5',
            'SLC29A3',
            'SLC33A1',
            'SLC4A11',
            'SLC52A2',
            'SLC52A3',
            'SLC9A1',
            'SLITRK6',
            'SMAD4',
            'SMPX',
            'SNAI2',
            'SOX10',
            'SOX2',
            'SPATC1L',
            'SPINK5',
            'SRPX2',
            'STRC',
            'STXBP2',
            'STXBP3',
            'SUCLA2',
            'SUCLG1',
            'SYNE4',
            'TACO1',
            'TBC1D24',
            'TBL1X',
            'TBX1',
            'TCF21',
            'TCOF1',
            'TDP2',
            'TECTA',
            'TECTB',
            'TFAP2A',
            'TFB1M',
            'TIMM8A',
            'TIMMDC1',
            'TJP2',
            'TMC1',
            'TMC2',
            'TMEM126B',
            'TMEM132E',
            'TMIE',
            'TMPRSS3',
            'TMPRSS5',
            'TNC',
            'TPRN',
            'TRIOBP',
            'TRMU',
            'TSPEAR',
            'TUBB4B',
            'TWNK',
            'TYR',
            'USH1C',
            'USH1G',
            'USH2A',
            'VCAN',
            'WBP2',
            'WFS1',
            'WHRN',
        }
    ) > 0)