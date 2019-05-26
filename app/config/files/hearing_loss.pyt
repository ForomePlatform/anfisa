#Exclude  variants not in hearing loss panel
if Genes not in panel(All_Hearing_Loss):
    return False

#Include Present in HGMD as "DM"
if HGMD_Tags in {"DM"}:
    return True

# Exclude common variants AF> 5%
if gnomAD_AF >= 0.05:
    return False

#Exclude variants farther then 5pb from intronic/exonic border
if (not Region in {"exon"}) and Dist_from_Exon >= 6:
    return False

#2.a.	Include if present in ClinVar as: Path, Likely Path, VUS
# (worst annotation, unless annotated benign by trusted submitter')
if (Clinvar_Benign in {"False"} and
        Clinvar_Trusted_Benign in {"False", "No data"}):
    return True

# 2.b.	Include All de novo variants
if (Callers in {"BGM_BAYES_DE_NOVO"}):
    return True

# 2.c.	Include all potential LOF variants
#       (stop-codon, frameshift, canonical splice site).
if (Severity >= 3):
    return True

# 3.a. Leave only:
#   "Missense", "synonymous" and "splice region" variants
if (Severity <= 0):
    return False

#3.	Include: AF < 0.0007 (GnomAD Overall)
#  And: PopMax < 0.01
#       (minimum 2000 alleles total in ancestral group)')
if (gnomAD_AF <= .0007 and 
        (gnomAD_PopMax_AN <= 2000 or gnomAD_PopMax_AF <= .01)):
    return True

return False
