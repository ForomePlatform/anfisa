#Exclude  variants not in hearing loss panel
if Gene_Lists not in {"@ACMG59", "ACMG59"}:
    return False

#Include Present in HGMD as "DM"
if HGMD_Tags in {"DM"}:
    return True

#Include if present in ClinVar as: Path, Likely Path, VUS
# (worst annotation, unless annotated benign by trusted submitter')

if (ClinVar_Significance in {
            "Pathogenic",
            "Pathogenic, protective",
            "Pathogenic, risk factor",
            "Likely pathogenic",
            "Likely pathogenic, risk factor"
        }):
    return True

if (ClinVar_Significance in {
            "Uncertain significance"
        } and
        (Clinvar_Trusted_Simplified in {"uncertain", "pathogenic"} or
            Clinvar_Trusted_Simplified not in {"benign"})):
    return True

#Exclude variants farther then 25pb from intronic/exonic border
if (Region_Worst not in {"exon"}) and Dist_from_Exon_Worst > 25:
    return False
if Region_Worst in {"masked_repeats"}:
     return False

if (Clinvar_Benign in {"False"} and
        (Clinvar_Trusted_Simplified in {"uncertain", "pathogenic"} or
            Clinvar_Trusted_Simplified not in {"benign"})):
    return True

if (Most_Severe_Consequence in {
            'transcript_ablation',
            'splice_acceptor_variant',
            'splice_donor_variant',
            'stop_gained',
            'frameshift_variant',
            'stop_lost',
            'start_lost'
        }):
    return True

return False
