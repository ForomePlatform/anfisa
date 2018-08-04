CONFIG_AJson = {
    "_main_key": "label",
    "_view_tabs": ["view.general", "view.quality",
        "view.gnomAD", "view.Databases", "view.Predictions", "view.Genetics"],
    "_no_view_fields": ["view", "view.Inheritance"],

    "_aspect_title": {
        "view.general": "General",
        "view.quality": "Quality",
        "view.gnomAD": "gnamAD",
        "view.Databases": "Databases",
        "view.Predictions": "Predictions",
        "view.Genetics": "Genetics",
        "view.Inheritance": "Inheritance",
        "main": "VEP: Data",
        "cons": "VEP: Consequences",
        "colv": "Colocated Variants",
        "inp": "VCF"},
    "main": {
        "fields": ["label", "id", "assembly_name",
            "seq_region_name", "start", "end", "strand", "",
            "allele_string", "variant_class",
            "most_severe_consequence",
            "ClinVar", "HGMD"],
        "options": {
            "start":  {"class": "numeric"},
            "end":    {"class": "numeric"},
            "strand": {"class": "numeric"},
            "assembly_name": {"title": "Assembly"},
            "seq_region_name": {"title": "Sequence Region", "class": "flex"},
            "allele_string": {"title": "Allele String", "class": "flex"},
            "variant_class": {"title": "Variant Class", "class": "flex"},
            "most_severe_consequence": {
                "title": "Most Severe Consequence", "class": "flex"}
        }
    },
    "view.general":{
        "fields":["Genes", "header", "Ref", "Alt",
                  "Worst Annotation",
                  "cPos", "pPos",
                  "Ensembl Transcripts (Worst)",
                  "Variant Exon (Worst Annotation)",
                  "Variant Intron (Worst Annotation)",
                  "Ensembl Transcripts (Canonical)",
                  "Variant Exon (Canonical)",
                  "Variant Intron (Canonical)"],
        "options": {}
    },

    "view.quality":{
        "fields":["AD", "DP", "SB", "MQ", "QUAL"],
        "options": {}
    },
    "view.gnomAD":{
        "fields": ["AF", "URL"],
        "options": {"URL": {"class": "link"}}
    },
    "view.Databases":{
        "fields":["HGMD", "ClinVar"],
        "options": {"ClinVar": {"class": "link"}}
    },
    "view.Predictions":{
        "fields":["Polyphen",
                  "SIFT",
                  "REVEL",
                  "Mutation Taster",
                  "FATHMM",
                  "CADD",
                  "MutationAssessor"],
        "options": {}
    },
    "view.Genetics":{
        "fields":["Distance From Intron/Exon Boundary (Worst)", "Distance From Intron/Exon Boundary (Canonical)",
                  "Conservation",
                  "Species with variant", "Species with other variants", "MaxEntScan", "NNSplice", "Human Splicing Finder"],
        "options": {}
    },
    "view.Inheritance":{
        "fields":[],
        "options": {}
    },
    "colocated_variants": {
        "fields": ["id", "start", "end", "allele_string", "strand",
            "pubmed", "somatic", "phenotype_or_disease", "clin_sig",] +
            [[tp, [tp + "_allele", tp + "_maf"]] for tp in
                ("aa", "afr", "amr", "ea", "eas", "eur", "sas",
                "gnomad", "gnomad_afr", "gnomad_amr", "gnomad_asj",
                "gnomad_eas", "gnomad_fin", "gnomad_nfe",
                "gnomad_oth", "gnomad_sas")] +
            [["minor", ["minor_allele", "minor_allele_freq"]]],
        "options": {"allele_string":
            {"title": "Allele String", "class": "flex"}}
    },
    "consequences": {
        "groups": ["intergenic", "motif_f", "regulatory_f", "transcript"],
        "group-options": {
            "intergenic": {"field": "intergenic_consequences",
                "title": "Intergenic"},
            "motif_f": {"field": "motif_feature_consequences",
                "title": "Motif feature"},
            "regulatory_f": {"field": "regulatory_feature_consequences",
                "title": "Regulatory feature"},
            "transcript": {"field": "transcript_consequences",
                "title": "Transcript"}
        },
        "fields": ["amino_acids", "biotype", "cadd_phred", "cadd_raw",
            "canonical", "ccds", "cdna_end", "cdna_start", "cds_end",
            "cds_start", "clinvar_clnsig", "clinvar_rs", "codons",
            "consequence_terms", "conservation", "distance",
            "domains", "exacpli", "exon", "fathmm_pred",
            "fathmm_score", "flags", "gene_id",
            "gene_pheno", "gene_symbol", "gene_symbol_source",
            "gnomad_exomes_af", "gnomad_exomes_asj_af", "gnomad_genomes_af",
            "hgnc_id", "hgvs_offset", "hgvsc", "hgvsp",
            "high_inf_pos", "impact", "intron",
            "motif_feature_id", "motif_name", "motif_pos",
            "motif_score_change", "mutationassessor_pred",
            "mutationassessor_score", "mutationtaster_pred",
            "mutationtaster_score", "polyphen2_hdiv_pred",
            "polyphen2_hdiv_score", "polyphen2_hvar_pred",
            "polyphen2_hvar_score", "polyphen_prediction",
            "polyphen_score",
            "protein_end", "protein_id", "protein_start",
            "regulatory_feature_id", "revel_score",
            "sift_pred", "sift_prediction", "sift_score",
            "strand", "swissprot", "transcript_id", "trembl",
            "uniparc", "variant_allele"],
        "options": {}
    }
}
