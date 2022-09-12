*************
Managing data
*************

Preparing data for AnFiSA
=========================

Anfisa works in tight connection with Forome annotation pipeline,
which process initial set of variations through series of annotation utilities.
Anfisa works only with data pre-processed by this pipeline and can't digest "raw"
unprocessed VCF file.

The pipeline source code and documentation can be found here:
https://github.com/ForomePlatform/vcf-upload-cwl-pipeline
However, at the moment the installation and running of this pipeline can be tricky.
For quick check of AnFiSA capabilities we recooment using bild-in sample data set.

If you want to make a quick try of AnFisa with your own dataset
you can contact **Forome** and ask for assistance with data processing.

Uplodaing data to Anfisa described in Anfisa Setup and Administration Guide

AnFiSA datasets
================
Uploading of processed data file (VCF/BAM) with the variants to the AnFiSA
creates primary XL dataset (XL, eXtra Large), which usually represents a whole exome (WES)
or a whole genome (WGS) sequencing data and can encompass up to 10 million variants.

The Anfisa users can generate secondary datasets by applying decision trees on primary XL datasets.
Secondary datasets are present as workspaces and contain smaller number of variants (up to 10000).
Workspace allows users to view, explore, tag, annotate and review the variants in it.






