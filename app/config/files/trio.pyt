if (Callers in {"BGM_BAYES_DE_NOVO"}):
    return True

import Compound_heterozygous

# Inheritance Mode
if ((Inheritance_Mode() in
            {"Homozygous Recessive", "Autosomal Dominant"})
        or (Compound_heterozygous in {True})):
    return True

return False
