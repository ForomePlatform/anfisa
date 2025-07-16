#Exclude  variants not detected in the family
"""
@knowledge_domain("Phenotypic Data")
@scale("Variant")
"""
if Num_Samples < 1:
    return False
#Exclude  variants not in hearing loss panel
"""
@scale("Variant in Transcript")
"""
if Transcript_Gene_Lists not in {All_Hearing_Loss}:
    return False
#Include Present in HGMD as "DM"
"""
@knowledge_domain("Human Genetics")
@scale("Variant")
@method("Clinical Evidence")
"""
if HGMD_Tags in {"DM"}:
    return True
# Exclude common variants AF> 5%
"""
@knowledge_domain("Population Genetics")
@scale("Variant")
@method("Experimental, Other")
"""
if gnomAD_AF >= 0.05:
    return False
#Exclude variants farther then 5pb from intronic/exonic border
"""
@scale("Variant in Transcript")
"""
if Transcript_source not in {"Ensembl"}:
     return False
"""
@knowledge_domain("Functional Genetics")
@scale("Variant in Transcript")
@scale("Window")
"""
if ((Transcript_region not in {"exon"})
    and (Transcript_dist_from_exon >= 6 or Transcript_dist_from_exon < 1)):
    return False
"""
@scale("Variant in Transcript")
"""
if Transcript_masked in {"True"}:
     return False
#2.a.    Include if present in ClinVar as: Path, Likely Path, VUS
# (worst annotation, unless annotated benign by trusted submitter')
"""
@knowledge_domain("Human Genetics")
@scale("Variant")
@method("Clinical Evidence")
"""
if (Clinvar_Benign in {"VUS or Pathogenic"} and
        (Clinvar_Trusted_Simplified in {"uncertain", "pathogenic"} or
            Clinvar_Trusted_Simplified not in {"benign"})):
    return True
# 2.b.    Include All de novo variants
"""
@knowledge_domain("Call Annotations")
@scale("Variant")
"""
if (Callers in {"BGM_BAYES_DE_NOVO"}):
    return True
"""
@knowledge_domain("Call Annotations")
@scale("Variant")
"""
if (Callers in {"RUFUS"}):
    return True
"""
@knowledge_domain("Call Annotations")
@scale("Variant")
"""
if (Callers in {"CNV"}):
    return True
# 2.c.    Include all potential LOF variants
#       (stop-codon, frameshift, canonical splice site).
"""
@knowledge_domain("Functional Genetics")
@scale("Variant in Transcript")
@method("Bioinformatics Inference")
"""
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
"""
@knowledge_domain("Functional Genetics")
@scale("Variant in Transcript")
@method("Bioinformatics Inference")
"""
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
"""
@knowledge_domain("Human Genetics")
@scale("Variant")
@method("Clinical Evidence")
"""
if (Clinvar_Benign in {"Benign"} and Clinvar_stars in {"2", "3", "4"}):
    return False
"""
@knowledge_domain("Human Genetics")
@scale("Variant")
@method("Clinical Evidence")
"""
if (Clinvar_Trusted_Simplified in {"benign"} and Clinvar_stars in {"1"}):
    return False
#3.    Include: AF < 0.0007 (GnomAD Overall)
#  And: PopMax < 0.01
#       (minimum 2000 alleles total in ancestral group)')
"""
@knowledge_domain("Population Genetics")
@scale("Variant")
@method("Experimental, Other")
"""
if (gnomAD_AF <= .0007 and
        (gnomAD_PopMax_AN <= 2000 or gnomAD_PopMax_AF <= .01)):
    return True
return False

