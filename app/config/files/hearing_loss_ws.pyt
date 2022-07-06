#Exclude  variants not detected in the family
if Num_Samples < 1:
    return False

#Exclude  variants not in hearing loss panel
if Transcript_Gene_Lists not in {All_Hearing_Loss}:
    return False

#Include Present in HGMD as "DM"
if HGMD_Tags in {"DM"}:
    return True

# Exclude common variants AF> 5%
if gnomAD_AF >= 0.05:
    return False

#Exclude variants farther then 5pb from intronic/exonic border
if Transcript_source not in {"Ensembl"}:
     return False
if ((Transcript_region not in {"exon"})
    and (Transcript_dist_from_exon >= 6 or Transcript_dist_from_exon < 1)):
    return False
if Transcript_masked in {"True"}:
     return False

#2.a.	Include if present in ClinVar as: Path, Likely Path, VUS
# (worst annotation, unless annotated benign by trusted submitter')
if (Clinvar_Benign in {"VUS or Pathogenic"} and
        (Clinvar_Trusted_Simplified in {"uncertain", "pathogenic"} or
            Clinvar_Trusted_Simplified not in {"benign"})):
    return True

# 2.b.	Include All de novo variants
if (Callers in {"BGM_BAYES_DE_NOVO"}):
    return True
if (Callers in {"RUFUS"}):
    return True
if (Callers in {"CNV"}):
    return True

# 2.c.	Include all potential LOF variants
#       (stop-codon, frameshift, canonical splice site).
if (Transcript_consequence in {
            'transcript_ablation',
            'splice_acceptor_variant',
            'splice_donor_variant',
            'stop_gained',
            'frameshift_variant',
            'stop_lost',
            'start_lost'
        }):
    return True

# 3.a. Leave only:
#   "Missense", "synonymous" and "splice region" variants
if (Transcript_consequence not in {
        "inframe_insertion",
        "inframe_deletion",
        "missense_variant",
        "protein_altering_variant",
        "splice_region_variant",
        "synonymous_variant",
        "stop_retained_variant",
        "coding_sequence_variant"
        }):
    return False

if (Clinvar_Benign in {"Benign"} and Clinvar_stars in {"2", "3", "4"}):
    return False

if (Clinvar_Trusted_Simplified in {"benign"} and Clinvar_stars in {"1"}):
    return False

#3.	Include: AF < 0.0007 (GnomAD Overall)
#  And: PopMax < 0.01
#       (minimum 2000 alleles total in ancestral group)')
if (gnomAD_AF <= .0007 and
        (gnomAD_PopMax_AN <= 2000 or gnomAD_PopMax_AF <= .01)):
    return True

return False
