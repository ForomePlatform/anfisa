*************
Forome AnFiSA
*************

Forome and AnFiSa overview
==========================
**Forome** (Forum for Omics: https://forome.org/) is an open community of renowned clinicians,
researchers and professional software developers
from different countries and backgrounds.
The Forome project purpose is to create the first community-built and fully
open-source genomics analysis software platform, following the crowdsourcing strategy.

Forome Genomics Analysis Platform consists of the following major modules:

* Upstream pipeline, that acquires data from a sequencing facility and creates the aligned BAM files;
* A set of standard and custom rare variant callers identifying extremely rare and unknown variants in a pedigree-aware way;
* The downstream annotation pipeline programmatically accessing a wide range of information related to functional analysis from relevant scientific and clinical databases (population genetics, clinical information, epigenetics)
* Interactive variants filtration, annotation and visualization tool.

Forome Genomics Platform supports both clinical and research workflows for all flavors of genetic data,
including Mendelian analysis on a case-by-case basis and on cohorts of patients.
It contains an integrated development environment for clinical rules, providing the ability to seamlessly
transform research workflows into novel clinical protocols.

**AnFiSA** (Annotation and Filtration for Sequencing Analysis) is a Variant Analysis and Curation tool
developed as a part of the Forome platform. It was designed to be
a specialized data warehouse for complex genomic data analysis,
such as whole genome sequencing for patients with rare diseases.

AnFiSA provides to user an organized web-based interface for variant filtration, curation and interpretation.
It incorporates a novel framework for intuitive and visual application of inclusion and exclusion criteria to
millions of records.
The AnFiSA platform is simple enough to be used by clinicians while at the same time capable of transforming
research workflows into more formal clinical protocols.
AnFiSA represents these protocols as human readable scripts in a notebook-like environment.

In addition AnFiSA keeps all data relevant to the annotation and curation processes
in the format straightforward for the review,
ensuring results reproducibility and traceability.
As a warehouse, AnFiSA stores annotations of all possible mutations in the human genome
that are used to prioritize candidate pathogenic variants in an affected proband.
It provides an easy and intuitive way
to perform reanalysis of some of the cases based on the new versions
of the knowledge sources or a new variant call file.

AnFiSA capabilities
===================

Anfisa tool allows the following:

* Supporting analysis of whole genomes, exomes as well as gene panels.
* Automated collection of genomics data from relevant sources, minimizing hands-on data collection time
* Automatically annotating genetic variants according to the current ACMG guideline
* Providing regular updates of genomics databases without posing challenges for reproducible and traceable automated genetic diagnostics tools
* Eliminating possible operator errors
* Presenting data in a well-organized, uniform way convenient for the review
* Tagging, followed by tag-based filtering
* Smoothing filtering with pre-defines and custom filters
* Curates decision trees adaptable to changing clinical rules
* Keeping curation notes
* A great data visualization

In contrast to most existing software packages, Anfisa is:

* Fully open-source variant curation tool
* Personalized medicine tool
* Supports both clinical and research workflows
* Forward-compatible in regards to supporting ever-changing diagnostic rules adopted by the genetics community
* Crowdsourcing-friendly interface to address difficult-to-diagnose cases
* Has been developed to invite and accept contributions from clinicians, researchers and professional software developers


Installation
============
AnFiSA can be used as a standalone application, or as a collaborative server.
For a quick introduction, look at a demo of AnFiSA at https://app.demo.forome.org/
The demo contains high confidence small variants callset v4.2 created by NIST by integrating results of sequencing,
alignment and variant calling from different sources; including both short and long read techniques.

To install local version of AnFiSA (including demo data) please follow the README in application repository:
https://github.com/ForomePlatform/anfisa/tree/v.0.7.x

User guide and tutorial
=======================

Anfisa user guide describes all available Anfisa tool options, operators and fields providing insight
into functional possibilities of the application.
This user guide also includes step-by-step instructions for geneticists and clinicians who are involved
in genetic variant’s analysis, annotations and curation.

This guide is current as of Anfisa version v.0.7.

To get familiar with AnFiSA capabilities, go through the following pages:


.. toctree::
   :maxdepth: 1

   intro

   managing_data

   workspace

   filter_refiner

   decision_tree.rst
   
   annotation_sources
   
   func_ref
   
   dtree_syntax
   
   zygosity

Acknowledgment
==============

Forome Anfisa is being actively used in three diverse and complementary projects:
SEQaBOO (SEQuencing a Baby for an Optimal Outcome),
Brigham Genomic Medicine (BGM)/Harvard Undiagnosed Disease Network Clinical Site
and research cohort analysis of purpura fulminans (PF) patients.

Indices and tables
==================

* :ref:`genindex`
* :ref:`search`
