.. _intro:

************
Introduction
************

Define the challenge
====================
Despite genomic sequencing rapidly transforming from being a bench-side tool to a routine procedure in a hospital,
there is a noticeable lack of genomic analysis software that supports both clinical and research workflows
as well as crowdsourcing.

There are number of approaches are used to architect upstream genomics analysis pipelines, prior to
variants identification.
Downstream genomic sequencing analysis (variations annotation and interpretation) is less standardized
and does not have a dominating set of tools and approaches.
Furthermore, most existing software packages are not forward-compatible in regards to
supporting ever-changing diagnostic rules adopted by the genetics community. Lastly, most of the software tools score
low on explainability amongst clinicians.

It would be fair to say, that the clinical community working with complex clinical cases
such as undiagnosed diseases with unknown genetic etiology does not have an optimal set of supporting tools.
If a healthcare organization wants to establish genetic services based on genomic sequencing,
there is no ready-made IT solution that this organization can acquire.
We believe that Forome project bridges a gap in the current ecosystem
of genetic analysis software. See more at https://forome.org/

AnFiSA key design and technology points
=======================================
Outside the fields of genetics and genomics, there is a thriving community
that continuously produces open-source software for data analysis, and cumulatively covers
virtually all aspects of data manipulation and exploration.
AnFiSA is focused on applying to variant analysis challenge best existing data analysis practises
instead of re-inventing the wheel.

Anfisa is based on three simple ideas: using Multidimensional database management system for genetic data,
using curated decision trees for clinical rules
and crowdsourcing of the most difficult cases.

These principles are translated into a variety of actionable design items:

* A platform that supports building and testing hypotheses in real-time without using programmable languages;
* Importance of real-time inspections of the results at each step of the data evaluation process;
* A platform that can be used as a computer aid for the clinicians;
* A highly responsive system which can deal with billions of genetic variants while providing a sub-minute response time;
* A two-tiered UI with a “red button” tier dedicated to application of existing guidelines and clinical protocols and a research tier supporting flexible research workflow and real-time processing of a patient’s whole genome;
* Visual tool that represents research hypotheses and workflow steps in a readable and editable way, while keeping track of any changes

Genome variations as a multi-dimensional data
---------------------------------------------
Genomic data are inherently multidimensional, i.e., every record is described by hundreds of
properties coming from a variety of interconnected sources, with each property often having multiple and even
inconsistent values often supported by contradicting evidence.
This is where OnLine Analytical Processing (OLAP) is valuable.
OLAP tools specifically focus on achieving the maximum performance for complex data querying,
data aggregation and information retrieval.

This approach is proven with other verticals like financial analysis, sales forecasting, etc.,
but to the best of our knowledge has never been applied to the big data in genetics. Currently,
AnFiSA relies on Apache Druid for backend OLAP support.

Pivoting data and pivot tables visualization
--------------------------------------------
The main foundation of our development strategy was the realization that genetic data are massive,
which makes it impossible to analyze individual records.
However, the data are static, which means that they do not change in real time and require analytical
rather than transactional processing. The volume of the data naturally leads to the idea
of visualization with Pivot Tables.
Pivot Tables show summary statistics and allow rearranging (or pivoting)
to spot patterns and build more advanced data models.

In AnFiSA, this idea is applied to the process of manual filtration of variants
to identify candidate causative mutations when a user builds a filter by adding conditions one-by-one.
As it is impossible to review individual records in a subset containing many thousands or millions of records,
we instead display a pivot table, a widget visualizing the distribution of the properties of the records.
AnFiSA does not make decisions for users - rather, it provides them with self-guided tools
to navigate in the labyrinth of heterogeneous information.

Curated decision trees
----------------------
Another key concept is representation of complex inclusion and exclusion criteria as a decision tree.

A decision tree is a sequence of a logical functions, applied to initial variation set.
At each branching point of a decision tree variants are split between three buckets:
those that are excluded from further review,
those that are unconditionally added to the resulting dataset
and those that are left for continuation of processing by subsequent branching points.
A result of application of a decision tree is a subset of candidate variants.
A very simple example of the decision tree can be
a shopping cart of an online shop.

Data scientists customarily use computational notebooks to represent their algorithms.
Decision trees fit naturally in the notebook interface, where a no-code visual representation
of an algorithm is combined with a readable and self-documented script.
AnFiSA follows the same approach to represent decision trees.

Specific sets of decision rules may vary depending on the phenotype in question,
whether the study is within a research or diagnostic setting, mode of inheritance or simply a
preference of the individual researcher/clinician.
At the same time, the process is highly repeatable
and same sets of rules may be invoked in many similar situations.

AnFiSA supports a number of pre-defined built-in decision trees.
They are included in the distribution and are available in the codebase on GitHub.

Crowdsourcing
-------------
Finally, there is the idea of crowdsourcing for solving the most challenging clinical cases
for patients with undiagnosed diseases. AnFiSA gives clinicians an option to create a secondary workspace,
which includes only very limited and fully de-identified information and thus can be shared
with outside researchers.

Testing data
============
For software development, validation and testing we used data from benchmark variants from the
whole genome of the openly-consented “Genome in a Bottle” Ashkenazi trio from the Personal Genome Project.
The high-confidence benchmark variants have been provided by NIST version 4.2.
The publicly available demo version of
AnFiSA includes datasets based on these resources.

**Next**: :ref:`filter_refiner`

:ref:`toc`
