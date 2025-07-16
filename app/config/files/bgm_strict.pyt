#Red Button Rule: highly probable damaging variants
#0.     Check sequencing quality
"""
@knowledge_domain("Call Annotations")
@scale("Variant")
"""
if Proband_GQ < 20:
    return False
"""
@knowledge_domain("Call Annotations")
@scale("Variant")
"""
if Min_GQ < 40:
    return False
"""
@knowledge_domain("Call Annotations")
@scale("Variant")
"""
if (0 < QD and QD < 4):
    return False
"""
@knowledge_domain("Call Annotations")
@scale("Variant")
"""
if (QD < 0 and 0 < QUAL and QUAL < 40):
    return False
"""
@knowledge_domain("Call Annotations")
@scale("Variant")
"""
if FS >= 30:
    return False
"""
@knowledge_domain("Human Genetics")
@scale("Position")
"""
if Region_Worst in {"masked_repeats"}:
     return False
#Always include De-Novo variants
"""
@knowledge_domain("Call Annotations")
@scale("Variant")
"""
if (Callers in {"BGM_BAYES_DE_NOVO"}):
    return True
"""
@knowledge_domain("Call Annotations")
@scale("Variant")
"""
if (Callers in {"RUFUS"}):
    return True
"""
@knowledge_domain("Call Annotations")
@scale("Variant")
"""
if (Callers in {"CNV"}):
    return True
"""
@knowledge_domain("Functional Genetics")
@scale("Variant in Transcript")
@method("Bioinformatics Inference")
"""
if (Variant_Class in {"CNV: deletion"}):
    return True
#Exclude common variants
"""
@knowledge_domain("Population Genetics")
@scale("Variant")
@method("Experimental, Other")
"""
if gnomAD_AF_Genomes >= 0.01:
    return False
"""
@knowledge_domain("Population Genetics")
@scale("Variant")
@method("Experimental, Other")
"""
if gnomAD_AF_Exomes >= 0.01:
    return False
#Exclude known homozygous variants
"""
@knowledge_domain("Population Genetics")
@scale("Variant")
@method("Experimental, Other")
"""
if (gnomAD_Hom >= 1):
    return False
"""
@knowledge_domain("Population Genetics")
@scale("Variant")
@method("Experimental, Other")
"""
if (gnomAD_Hem >= 1):
    return False
#Exclude variants common for an ancestry group
"""
@knowledge_domain("Population Genetics")
@scale("Variant")
@method("Experimental, Other")
"""
if (gnomAD_PopMax_AN >= 2000 and gnomAD_PopMax_AF >= .05):
    return False
#Exclude non-coding
#   except those likely to alter splicing
"""
@knowledge_domain("Functional Genetics")
@knowledge_domain("Human Genetics")
@scale("Variant")
@method("Bioinformatics Inference")
"""
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
"""
@knowledge_domain("Human Genetics")
@scale("Variant")
@method("Clinical Evidence")
"""
if (Clinvar_Benign in {"Benign"} and Clinvar_stars in {"2", "3", "4"}):
    return False
"""
@knowledge_domain("Human Genetics")
@scale("Variant")
@method("Clinical Evidence")
"""
if (Clinvar_Trusted_Simplified in {"benign"} and Clinvar_stars in {"1"}):
    return False
label("Comp-1")
# Inheritance Mode
"""
@knowledge_domain("Phenotypic Data")
@scale("Variant")
"""
if (Inheritance_Mode() in {"Homozygous Recessive"}
        and Proband_Zygosity in {Homozygous}):
    return True
"""
@knowledge_domain("Phenotypic Data")
@scale("Variant")
"""
if Inheritance_Mode() in {"X-linked"}:
    return True
"""
@knowledge_domain("Phenotypic Data")
@scale("Gene")
"""
if Compound_Het(state="Comp-1") in {Proband}:
    return True
return False
