.. _managing_data:

*************
Managing data
*************

Preparing data for AnFiSA
=========================

AnFiSA works in tight connection with the Forome annotation pipeline,
which processes the initial set of variations through a series of annotation utilities.
AnFiSA works only with data pre-processed by this pipeline and can't digest "raw"
unprocessed VCF files.

The pipeline source code and documentation can be found here:
https://github.com/ForomePlatform/vcf-upload-cwl-pipeline.
However, at the moment, the installation and running of this pipeline can be tricky.
For a quick check of AnFiSA's capabilities, we recommend using a bild-in sample data set.

If you want to make a quick try of AnFiSA with your own dataset
you can contact **Forome** and ask for assistance with data processing.

Uploading data to AnFiSA is described in AnFiSA Setup and Administration Guide.

Notes regarding calling de novo variants
----------------------------------------
The specificity of calling de novo variants by standard GATK callers, such as, Haplotype caller
is unacceptably low to be useful for clinical practice.
In many cases, this is not a serious limitation, as de novo events are rare
and if the analysis is driven by phenotypic features and focused on established disease genes,
few de novo variants will pass initial filtering.

However, AnFiSA is designed to evaluate patients with undiagnosed diseases,
where de novo mutation is often a viable hypothesis.
Analyzing such patients requires the use of specialized variant callers.
In our practice, we used `NovoCaller <https://academic.oup.com/bioinformatics/article/35/7/1174/5087716>`_
and `Rufus <https://github.com/jandrewrfarrell/RUFUS>`_.
Calling de novo variants is a part of the upstream analysis and hence beyond the topic of this guide.
Nevertheless, the curation algorithms we have developed rely on the annotations produced by these callers.

AnFiSA datasets
================
Uploading of the processed data file (VCF/BAM) with the variants to the AnFiSA
creates a primary XL dataset (XL, eXtra Large), which usually represents a whole exome (WES)
or a whole genome (WGS) sequencing data and can encompass up to 10 million variants.

The AnFiSA users can generate secondary datasets by applying decision trees on primary XL datasets.
Secondary datasets are present as workspaces and contain fewer variants (up to 10000).
Workspace allows users to view, explore, tag, annotate, and review the variants in it.

**Next**: :ref:`workspace`

:ref:`toc`




