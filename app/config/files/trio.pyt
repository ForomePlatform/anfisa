if (Callers in {"BGM_BAYES_DE_NOVO"}):
    return True

# Inheritance Mode
if Inheritance_Mode() in {"Homozygous Recessive"}:
    return True

if Inheritance_Mode() in {"Autosomal Dominant"}:
    return True

if Compound_Het in {True}:
    return True

return False
