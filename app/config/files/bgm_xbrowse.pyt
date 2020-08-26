# BGM Research Rule: creates a workspace for BGM exploration
#0.     Check sequencing quality
if Proband_GQ < 20:
    return False
if Region_Worst in {"masked_repeats"}:
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

#Exclude variants common for an ancestry group
if (gnomAD_PopMax_AN >= 2000 and gnomAD_PopMax_AF >= .05):
    return False

#Exclude very low impact variants
#   except those likely to alter splicing
if ((Most_Severe_Consequence in
            {
                "intron_variant",
                "intergenic_variant",
                "non_coding_transcript_exon_variant",
                "upstream_gene_variant",
                "downstream_gene_variant",
                "TF_binding_site_variant",
                "regulatory_region_variant"
            })
        and (splice_ai_dsmax <= 0.2)):
    return False

label("Comp-1")

# Inheritance Mode
if (Inheritance_Mode() in {"Homozygous Recessive"}
        and Proband_Zygosity in {Homozygous}):
    return True

if Inheritance_Mode() in {"X-linked"}:
    return True

if Inheritance_Mode() in {"Autosomal Dominant"}:
    return True

if Compound_Het(state="Comp-1") in {Proband}:
    return True

return False
