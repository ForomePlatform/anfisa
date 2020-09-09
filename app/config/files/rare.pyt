#Always include De-Novo variants
if (Callers in {"BGM_BAYES_DE_NOVO"}):
    return True

#Exclude common variants
if gnomAD_AF >= 0.01:
    return False

#Exclude variants common for an ancestry group
if (gnomAD_PopMax_AN >= 2000 and gnomAD_PopMax_AF >= .05):
    return False

#Exclude very low impact variants
#   except those likely to alter splicing
if ((Most_Severe_Consequence in
            {"intron_variant", "intergenic_variant"})
        and (splice_ai_dsmax <= 0.2)):
    return False

