if (Callers in {"BGM_BAYES_DE_NOVO"}):
    return True

import Compound_Het

# Inheritance Mode
if Inheritance_Mode() in {"Homozygous Recessive"}:
    return True

if Inheritance_Mode() in {"Autosomal Dominant"}:
    return True

if Compound_Het in {Proband}:
    return True

return False
