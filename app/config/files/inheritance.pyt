if (Callers in {"BGM_BAYES_DE_NOVO"}):
    return True

# Inheritance Mode
if (not Inheritance_Mode() in
        {"Homozygous Recessive", "Autosomal Dominant"}):
    return False
