#Exclude common variants
if gnomAD_AF <= 0.001:
    return False

#Exclude low impact variants
if Severity <= 0:
    return False

#2.a.	Include if present in ClinVar Path, Likely Path, 
#   VUS (worst annotation), unless annotated benign by trusted submitter')
if Clinvar_Benign in {True} and Clinvar_Trusted_Benign in {"False", "No data"}:
    return True

#3.	Include: AF < 0.0007 (GnomAD Overall) AND +/- 5 bases
#And: PopMax < 0.01 (minimum 2000 alleles total in ancestral group)')
if (gnomAD_AF <= .0007 and 
        (gnomAD_PopMax_AN <= 2000 or gnomAD_PopMax_AF >= .01)):
    return False

return True
