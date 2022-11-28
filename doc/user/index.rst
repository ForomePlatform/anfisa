*************
Forome AnFiSA
*************

Forome and AnFiSA overview
==========================
**Forome** (Forum for Omics: https://forome.org/) is an open community of renowned clinicians,
researchers and professional software developers
from different countries and backgrounds.
The Forome project aims to create the first community-built and fully
open-source genomics analysis software platform, following the crowdsourcing strategy.

Forome Genomics Analysis Platform consists of the following major modules:

* Upstream pipeline, which acquires data from a sequencing facility and creates the aligned BAM files;
* A set of standard and custom variant callers identifying extremely rare and unknown variants in a pedigree-aware way;
* The downstream annotation pipeline programmatically accessing a wide range of information
  related to the functional analysis from the relevant scientific and clinical databases
  (population genetics, clinical information, and epigenetics);
* Interactive variants filtration, annotation, and visualization tool.

Forome Genomics Platform supports clinical and research workflows for all flavors of genetic data,
including Mendelian analysis on a case-by-case basis and cohorts of patients.
It contains an integrated development environment for clinical rules, providing the ability to seamlessly
transform research workflows into novel clinical protocols.

**AnFiSA** (Annotation and Filtration for Sequencing Analysis) is a Variant Analysis and Curation tool
developed as a part of the Forome platform. It was designed to be
a specialized data warehouse for complex genomic data analysis,
such as whole genome sequencing for patients with rare diseases.

AnFiSA provides the user with an organized web-based interface for variant filtration, curation, and interpretation.
It incorporates a novel framework for the intuitive and visual application of inclusion and exclusion criteria to
millions of records.
The AnFiSA platform is simple enough to be used by clinicians while at the same time capable of transforming
research workflows into more formal clinical protocols.
AnFiSA represents these protocols as human-readable scripts in a notebook-like environment.

In addition, AnFiSA keeps all data relevant to the annotation and curation processes
in a format that’s simple for review, ensuring results' reproducibility and traceability.
As a warehouse, AnFiSA stores annotations of all possible mutations in the human genome
that are used to prioritize candidate pathogenic variants in an affected proband.
It provides an easy and intuitive way to perform a reanalysis of some cases based on the new versions
of the knowledge sources or a new variant call file.

A detailed description of the AnFiSA and Forome platform from a scientific point of view can be found in the paper:
`AnFiSA: An open-source computational platform for the analysis
of sequencing data for rare genetic disease <https://www.sciencedirect.com/science/article/abs/pii/S153204642200185X>`_


AnFiSA capabilities
===================

AnFiSA tool allows the following:

* Supporting the analysis of the whole genomes, exomes, and gene panels;
* Automated collection of genomics data from relevant sources, minimizing hands-on data collection time;
* Automatically annotating genetic variants according to the current ACMG guideline;
* Providing regular updates of genomics databases without posing a challenge to reproducible and traceable automated genetic diagnostics tools;
* Eliminating possible operator errors;
* Presenting data in a well-organized, uniform way that's convenient for the review;
* Tagging, followed by tag-based filtering;
* Smoothing filtering with pre-defined and custom filters;
* Curates decision trees adaptable to changing clinical rules;
* Keeping curation notes;
* A great data visualization;

In contrast to most existing software packages, AnFiSA:

* Is a fully open-source variant curation tool;
* Is a personalized medicine tool;
* Supports both clinical and research workflows;
* Is forward-compatible in supporting ever-changing diagnostic rules adopted by the genetics community;
* Is a crowdsourcing-friendly interface for addressing difficult-to-diagnose cases;
* Was developed to invite and accept contributions from clinicians, researchers, and professional software developers;


Installation
============
AnFiSA can be used as a standalone application or as a collaborative server.
For a quick introduction, look at a demo of AnFiSA at https://app.demo.forome.org/
The demo contains high confidence small variants callset v4.2, created by NIST by integrating the results of sequencing,
alignment, and variant calling from different sources, including both short and long-read techniques.

To install a local version of AnFiSA (including demo data), please follow the README in the application repository:
https://github.com/ForomePlatform/anfisa/tree/v.0.7.x

User guide and tutorial
=======================

AnFiSA user guide describes all available AnFiSA tool options, operators, and fields providing insight
into the functional possibilities of the application.
This user guide also includes step-by-step instructions for geneticists and clinicians involved
in genetic variant analysis, annotations, and curation.

This guide is current as of AnFiSA version v.0.7.

For a very quick dive into AnFiSA, review :ref:`analysis_nutshell`

To get familiar with AnFiSA capabilities, start from the :ref:`intro`.
Or select a page from the table of contents.

.. _toc:

Table of contents
-----------------

..  toctree::
    :maxdepth: 1

    variant_analysis_nutshell

    intro

    managing_data

    workspace

    filter_refiner

    decision_tree

    filter_dashboard

    derived_dataset

    analysis_examples
   
.. _suppl:

Supplementary materials
=======================

..  toctree::
    :maxdepth: 1

    suppl/variants_classification

    suppl/predefined_filters

    suppl/discriminative_power

    suppl/annotation_sources

    suppl/func_ref

    suppl/dtree_syntax

    suppl/zygosity

Acknowledgment
==============

Forome AnFiSA is actively used in three diverse and complementary projects:
SEQaBOO (SEQuencing a Baby for an Optimal Outcome),
Brigham Genomic Medicine (BGM)/Harvard Undiagnosed Disease Network Clinical Site
and research cohort analysis of purpura fulminans (PF) patients.

Indices and tables
==================

* :ref:`genindex`
* :ref:`search`
