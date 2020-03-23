# Exclude common variants AF> 5%
if gnomAD_Total_AF >= 0.05:
    return False

#Exclude variants farther then 5pb from intronic/exonic border
if (GENCODE_Category not in {
                "exonic",
                "UTR3",
                "UTR5",
                "splicing"
            }):
    return False

#2.a.	Include if present in ClinVar as: Path, Likely Path, VUS
# (worst annotation, unless annotated benign by trusted submitter')
if (Clinvar in {"Likely pathogenic", "Pathogenic"}):
    return True

# 2.c.	Include all potential LOF variants
#       (stop-codon, frameshift, canonical splice site).
if (GENCODE_Exonic_Category in {
            "frameshift deletion",
            "frameshift insertion",
            "stopgain"
        }):
    return True

# 3.a. Leave only:
#   "Missense", "synonymous" and "splice region" variants
if (GENCODE_Exonic_Category not in {
                "nonframeshift deletion",
                "nonframeshift insertion",
                "nonsynonymous SNV",
                "stoploss",
                "synonymous SNV"
            }
            and
                GENCODE_Category not in {"splicing"}
        ):
    return False

#3.	Include: AF < 0.0007 (GnomAD Overall)
if gnomAD_Total_AF >= 0.0007:
    return False

if Polyphen_2_HVAR in {"D"} and  SIFTcat in {"deleterious"}:
    return True

return False
