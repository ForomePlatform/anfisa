if (Callers in {"BGM_BAYES_DE_NOVO"}):
    return True

import Compound_heterozygous

# Inheritance Mode
if Inheritance_Mode() in {"Homozygous Recessive"}:
    return True

if Inheritance_Mode() in {"Autosomal Dominant"}:
    return True

if Compound_heterozygous in {True}:
    return True

return False
