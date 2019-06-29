#Exclude  variants not in hearing loss panel
if Genes not in panel(ACMG59):
    return False

#Include Present in HGMD as "DM"
if HGMD_Tags in {"DM"}:
    return True

#Include if present in ClinVar as: Path, Likely Path, VUS
# (worst annotation, unless annotated benign by trusted submitter')
if (Clinvar_Benign in {"False"} and
        Clinvar_Trusted_Benign in {"False", "No data"}):
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
