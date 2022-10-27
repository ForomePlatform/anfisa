.. _managing_data:

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

Uploading data to Anfisa described in Anfisa Setup and Administration Guide.

Notes regarding calling de novo variants
----------------------------------------
The specificity of calling de novo variants by standard GATK callers such as Haplotype caller
is unacceptably low to be useful in clinical practice.
In many cases, this is not a serious limitation, as de novo events are rare
and if the analysis is driven by phenotypic features and focused on established disease genes,
few de novo variants will pass initial filtering.

However, AnFiSA is designed to be used to evaluate patients with undiagnosed diseases,
where de novo mutation is often a viable hypothesis.
Analyzing such patients requires the use of specialized variant callers.
In our practice, we used `NovoCaller <https://academic.oup.com/bioinformatics/article/35/7/1174/5087716>`_
and `Rufus <https://github.com/jandrewrfarrell/RUFUS>`_.
Calling de novo variants is a part of the upstream analysis and hence beyond the topic of this guide.
Nevertheless, the curation algorithms we have developed rely on the annotations produced by these callers.

AnFiSA datasets
================
Uploading of processed data file (VCF/BAM) with the variants to the AnFiSA
creates primary XL dataset (XL, eXtra Large), which usually represents a whole exome (WES)
or a whole genome (WGS) sequencing data and can encompass up to 10 million variants.

The Anfisa users can generate secondary datasets by applying decision trees on primary XL datasets.
Secondary datasets are present as workspaces and contain smaller number of variants (up to 10000).
Workspace allows users to view, explore, tag, annotate and review the variants in it.

**Next**: :ref:`workspace`

:ref:`toc`




