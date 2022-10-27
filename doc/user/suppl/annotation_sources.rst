.. _annotation_sources:

******************
Annotation Sources
******************

As a warehouse, AnFiSA stores annotations of single nucleotide variants (SNP),
insertions and deletions, copy number variantions (CNV) and structural variations (SV)
in the human genome that are used to prioritize candidate pathogenic variants in an affected proband.
Some of the annotations reflect technical information such as provenance and confidence information
about the specific call (call annotations).
Other annotations summarize genetic and biological evidence relevant to the potential effect
of mutations on molecular function and phenotype (biological annotations). These annotations
combine multiple inputs and consist of genomic, protein, and disease-specific information gathered
from different public and proprietary sources.

Brief description of annotation sources
=======================================

AnFiSA relies on dbNSFP gnomAD, ENSEMBLE Variant Effect Predictor (VEP)
and NCBI resources (e.g., ClinVar, MedGen and PubMed), OMIM, SpliceAI and HGMD as main annotation sources.
Collectively, these sources provide information on phenotypic effects of genes and individual variants,
allele frequencies, functional effect predictors (e.g., SIFT, PolyPhen),
conservation scores (e.g. PhastCons and GERP).
For ClinVar, in addition to the usual data for each variant including clinical significance,
stars, review status, conflicts, etc., the user has an option to select a set of trusted submitters,
in which case the clinical significance assigned by them will be provided as a separate category.
By default, AnFiSA includes Laboratory of Molecular Medicine (LMM),
GeneDx and Invitae as trusted sources by our team, though designation as trusted can be customized.



Here is the list of sources used in annotation process in Anfisa System

Assemblies
==========

GRCh37 (HG19)
-------------

* Project URL: `<https://www.ncbi.nlm.nih.gov/assembly/GCF_000001405.13/>`_

* File URL: `<http://ftp.ncbi.nlm.nih.gov/genomes/refseq/vertebrate_mammalian/Homo_sapiens/all_assembly_versions/GCF_000001405.25_GRCh37.p13/GCF_000001405.25_GRCh37.p13_genomic.fna.gz>`_

GRCh38
------

* Version: patch 13

* Project URL: `<https://www.ncbi.nlm.nih.gov/assembly/GCF_000001405.39>`_

* File URL: `<ftp://ftp.ncbi.nlm.nih.gov/genomes/refseq/vertebrate_mammalian/Homo_sapiens/all_assembly_versions/GCF_000001405.39_GRCh38.p13>`_

Gencode GTF
-----------

* Project URL: `<https://www.gencodegenes.org/pages/data_format.html>`_

* Downloads: `<https://useast.ensembl.org/info/data/ftp/index.html>`_

* Direct Download URL: `<ftp://ftp.ensembl.org/pub/release-99/gtf/homo_sapiens/Homo_sapiens.GRCh38.99.chr.gtf.gz>`_

Genome Aggregation Database (gnomAD)
====================================

* Version: 2.1.1

* URL: `<https://gnomad.broadinstitute.org/>`_

* Download URL: `<https://gnomad.broadinstitute.org/downloads>`_

ClinVar 
=======

* Project URL: `<https://www.ncbi.nlm.nih.gov/clinvar/>`_

* CSV File URL (contains data): `<https://ftp.ncbi.nlm.nih.gov/pub/clinvar/tab_delimited/variant_summary.txt.gz>`_
        
* XML File URL (contains data and metadata): `<https://ftp.ncbi.nlm.nih.gov/pub/clinvar/xml/>`_

SpliceAI
========
* GitHub URL:

    Download URL (requires free registration): `<https://basespace.illumina.com/analyses/194103939/files/236418325?projectId=66029966>`_

* Version: v1pre3

* Files:

    - spliceai_scores.masked.snv.hg38.vcf.gz

    - spliceai_scores.masked.indel.hg38.vcf.gz

* `<https://github.com/Illumina/SpliceAI>`_

dbNSFP
======

* Project URL: `<https://sites.google.com/site/jpopgen/dbNSFP>`_

* File URL: 

    - `<ftp://dbnsfp:dbnsfp@dbnsfp.softgenetics.com/dbNSFP4.0a.zip>`_ 
    - `<https://drive.google.com/file/d/1BNLEdIc4CjCeOa7V7Z8n8P8RHqUaF5GZ/view?usp=sharing>`_
    
dbSNP
=====

* Project URL: `<https://www.ncbi.nlm.nih.gov/snp>`_


GTEx
====

* Project URL: `<https://www.gtexportal.org/home/>`_

* Download URL: `<https://storage.googleapis.com/gtex_analysis_v8/rna_seq_data/GTEx_Analysis_2017-06-05_v8_RNASeQCv1.1.9_gene_median_tpm.gct.gz>`_

PharmGKB (Pharmacogenomics) 
===========================

* Project URL: `<https://www.pharmgkb.org/>`_

* Download URL: `<https://www.pharmgkb.org/downloads>`_

* File: Variant Annotations Help File (annotations.zip) 

GERP Scores
===========

* Project URL: `<http://mendel.stanford.edu/SidowLab/downloads/gerp/>`_

* Download URL: `<http://mendel.stanford.edu/SidowLab/downloads/gerp/hg19.GERP_scores.tar.gz>`_
