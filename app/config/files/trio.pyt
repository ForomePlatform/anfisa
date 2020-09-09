if (Callers in {"BGM_BAYES_DE_NOVO"}):
    return True

label("Comp-1")

# Inheritance Mode
if Inheritance_Mode() in {"Homozygous Recessive"}:
    return True

if Inheritance_Mode() in {"Autosomal Dominant"}:
    return True

if Compound_Het(state="Comp-1") in {Proband}:
    return True

return False
