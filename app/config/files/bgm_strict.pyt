#0.     Check sequencing quality
if Proband_GQ <= 19:
    return False
if Min_GQ <= 39:
    return False
if QD <= 4:
    return False
if FS >= 30:
    return False

#Always include De-Novo variants
if (Callers in {"BGM_BAYES_DE_NOVO"}):
    return True
if (Callers in {"RUFUS"}):
    return True
if (Callers in {"CNV"}):
    return True
if (Variant_Class in {"CNV: deletion"}):
    return True

#Exclude common variants
if gnomAD_AF_Genomes >= 0.01:
    return False
if gnomAD_AF_Exomes >= 0.01:
    return False
#Exclude known homozygous variants
if (gnomAD_Hom >= 1):
    return False
if (gnomAD_Hem >= 1):
    return False

#Exclude variants common for an ancestry group
if (gnomAD_PopMax_AN >= 2000 and gnomAD_PopMax_AF >= .05):
    return False

#Exclude non-coding
#   except those likely to alter splicing
if ((Most_Severe_Consequence in
            {
                "intergenic_variant",
                "intron_variant",
                "non_coding_transcript_exon_variant",
                "upstream_gene_variant",
                "downstream_gene_variant",
                "TF_binding_site_variant",
                "regulatory_region_variant",
                "5_prime_UTR_variant",
                "3_prime_UTR_variant",
                "splice_region_variant",
                "TFBS_ablation",
                "mature_miRNA_variant",
                "synonymous_variant"
            })
        and (splice_ai_dsmax <= 0.2)):
    return False

import Compound_Het

# Inheritance Mode
if Inheritance_Mode() in {"Homozygous Recessive"}:
    return True

if Inheritance_Mode() in {"X-linked"}:
    return True

if Compound_Het in {Proband}:
    return True

return False
