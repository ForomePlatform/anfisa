if (Callers in {"BGM_BAYES_DE_NOVO"}):
    return True

if Custom() in {"Homozygous Recessive", "Autosomal Dominant"}:
    return True

return False