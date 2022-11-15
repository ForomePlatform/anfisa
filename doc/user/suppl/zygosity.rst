.. _zygosity_notes:

*****************
Notes on Zygosity
*****************

One of the most complicated task for doctors working with genome data is to catch rare
combinations of mutations which can lead to disease.
This section covers AnFiSA functions specially designed to deal with such complicated events.

Basic information regarding zygosity
====================================

Before we can proceed further, we nned to define some basic terms regarding zygosity.

Zygosity states
---------------
Most of chromosomes for human are pairwise, so a mutation/variant applying to a sample has one of the following states:

* Zygosity 0: variant is absent
* Zygosity 1: variant is heterozygous, it presents on one chromosome copy
* Zygosity 2: variant is homozygous, it presents on both copies of chromosome

Males have chromosomes X and Y in one copies, so a mutation/variant on these chromosomes for male sample
has one of the following states:

* Zygosity 0: variant is absent
* Zygosity 2: variant is hemozygous, it does present on single copy of chromosome

*Attention*: in hemozygous state a variant presents in one copy, however it is more convenient to define
zygosity number as 2, since it is essentially more similar to homozygous case than to heterozygous one.


Definitions: case, samples
--------------------------
Dataset in clinical disgnostics mostly represents a **case**
i.e genomics information on one or many persons - **samples** from the same family.

The typical case is **trio**: proband and two parents.
Note that some tasks in below are formulated only in context of this scope.

Compound heterozygous variants problem
======================================
The main idea of compound heterozygous variants is following.

The parents of the proband had different heterozygous recessive mutations in the same gene.
Each mutation in homozygous state breaks the gene function.
However for both parents these mutations are harmless:
both the patient's mother and father had other normal copies of the DNA of this gene, and everything was normal.
But in the patient, these two mutations converged,
and we catch a situation where one of the mutations breaks one copy of the gene, and the other breaks the other.

It is critically important for doctors to catch such pairs, but there are significant issues in their identification.
The list of mutations from which such pairs should be selected should,
on the one hand, be free of obviously non-problematic mutations, and,
on the other hand, should be large enough so that such rare events as compound pairs would be taken into account.

More formally: in the case of a trio, we need to find pairs of mutations that happened in the same gene,
and such that the first has the first property, and the second the second:

* First mutation: ``{"1": {patient, dad}, "0": {mother}}``
* Second mutation ``{"1": {patient, mom}, "0": {dad}}``


AnFiSA support of complex zygosity scenarios
============================================

Case IDs definition
-------------------
Each sample in case is identified by **id**.
Examples of id: ``"bgm9001a1"``, ``"bgm9001u1"``
Sample id starts with case id, then letter ``a`` (affected) or ``u`` (unaffected), and a number from 1 to upper.
The proband always ends up with ``"a1"`` (in medical cases proband is always "affected").

.. _zygosity_scenario:

Zygosity scenario notation
--------------------------
Zygosity scenario is join of zygosity conditions for samples in case. It is defined using following notation:

    | ``{`` *dictionary*
    |       <zygosity condition constant>: ``[`` *list of* samples id ``]``
    |       ...
    | ``}``

**Example**: ``{"1": {patient, dad}, "0": {mother}}``.
The variant is heterozygous in patient (proband) and its father. The patient's mother doesn't have a variation


.. _default_problem_group:

Zygosity conditions in AnFiSA
-----------------------------
We need to define meaningful conditions for zygosity number for variants. 
In the system the following 5 conditions are supported:

``“2”``,    ``“2-1”``,    ``“1”``,    ``“1-0”``,    ``“0”``

Formally speaking, we can define one more meaningful constant: ``"0-2"``,
but let us interpret this case as we do not define condition at all: all variant are passed.

.. _standard_zygosity_scenarios:

Standard zygosity scenarios
---------------------------
Let us consider split of samples in case on two groups: affected/unaffected.

The following scenarios are important in practice: 

* **Homozygous Recessive/X-linked**:  ``{“2”:`` *affected*, ``“1-0”:`` *unaffected* ``}``
* **Autosomal Dominant**:             ``{“2-1”:`` *affected*, ``“0”:`` *unaffected* ``}``
* **Compensational**:                 ``{“0”:`` *affected*, ``“2-1”:`` *unaffected* ``}``

Comments:

* **Autosomal Dominant** - probably bad: variant presents for all affected and is absent for all unaffected
* **Homozygous Recessive** - variant probably breaks gene, but has no effect while there is second good (gene) copy
* **X-linked** - variant probably bad, it affects all male samples and females in homozygous state
* **Compensational** - variant is probably good, it fixes (screens) up illness caused by other facts

These scenarios are most important for specialists and AnFiSA ave capable to identify it.

*Notes*: 

* we call group of affected samples as **problem group**
* for a dataset the **default problem group** is preset by different letters ``a`` and ``u`` in id of samples;
  however it is good if the user can define problem group directly

Gene approximations
-------------------
In the definition of compound heterozygotes given above,
we used the not fully formalized concept of “gene”.
AnFiSA supports three options to define, which is treated as *gene*:

#. *Transcript*: “gene” refers to a known transcript encoding a specific protein.
   This is the most accurate interpretation of the word “gene”.
   Unfortunately not all transcripts are identified
#. *Gene*: “gene” means a gene, but defined at the level of one of the transcripts
#. *Rough*: a gene is simply a known region/regions on a chromosome,
   regions sometimes overlapping (more precisely, one region may be inside another).
   This is the most inaccurate and crude way of interpreting the “gene” potentially leading to false positives.
   However it is the most "complete" method providing a certain level of guarantee that all real results
   will not be weeded out


Zygosity-related functions in AnFiSA
====================================

Inheritance_mode()
------------------
The function determines mutation type according to standard criteria for zygosity.

Custom_Inheritance()
--------------------
The extended version of *Inheritance_mode()* for any zygosity scenarios.


Compound_Heterozygous()
-----------------------
Identifies the compound heterozygous variations *inside a trio*.
The formal definition of compound heterozygous can be found here: :ref:`func_ref`


.. _compound_request:

Compound_Request()
------------------
The extension of *Compound_Heterozygous()* function to more complicated cases.




Zygosity events and compound requests
-------------------------------------

Let us fix some diapason or diapasons of positions on chromosome as "gene"
(see :ref:`below<gene_aproximations>` for details).
Then for some fixed zygosity scenario it is possible to count how many variants with this scenario
presents inside the "gene". Let us call these variants as "events".

    We are ready to define **compound request** in the following form:
    
    | ``[`` *list of* conditions for scenarios
    |       ``[`` *list*
    |           **[0]**: minimal count of events, **positive int**
    |           **[1]**: :ref:`zygosity_scenario`
    |       ``]``, ...
    | ``]``

The result of compound request is not empty only if for all scenarios in the list
there are not less than the defined count of events.

Strongly speaking, a compound request applies to "genes", and its result is either empty,
or *list of lists* of variants that cause events.
The current version of the system does not support so complex selection objects,
so we interpret result of compound request as a joined plain list of variants.

.. _compound-heterozygous:



The following compound request is important in practice. It applies to trio:

    | ``[``
    |       ``[1, {“1”: {`` *proband*, *proband's mother* ``}, “0”: {`` *proband`s father* ``}},``
    |       ``[1, {“1”: {`` *proband*, *proband's father* ``}, “0”: {`` *proband`s mother* ``}}``
    | ``]``
    
Comments.

* The main idea of request: let us consider case when only proband is affected.
  It might happen that on some "gene" each parent has (different) dangerous variant in heterozygous state.
  These variants have no effect because second copy of gene are not broken.
  But proband has both copies of "gene" broken: one copy is broken by one of dangerous variants, ans second copy -
  by another one.
* From informational point of view, the detection of compound events is a clear tasks.
  In practice however there are serious difficulties to prepare proper setup for this detection.
  Results of the procedure might be good only if most part of benign variants are filtered out before the detection process.
  It is a matter of experiments, so the system provides extended functionality for this special kind of experimental activity.
    
.. _gene_aproximations:    
    
Approximations to gene locations
--------------------------------

The system supports 3 variants of gene approximation:

* ``"transcript"``: shared transcript
* ``"gene"``: shared gene
* ``"rough"``: non-intersecting transcripts
    
The first two variants use transcript variants as a base filtering item, so they are applicable only in WS-datasets. 

In practice the first variant is most good for precision purposes. But it might be not so good in recall:
not all transcripts are well studied and registered up to now. For recall purposes use ``"rough"`` approximation:
it causes many false positive effects however it filters out variants that can not be found with first two
approximation variants.

Conclusion
==========
Detection for variants of standard scenarios and compound heterozygous variants are standard tasks in genomics,
so it is important to support it in the most easy way.

On another hand, the functionality based on direct definition of scenarios and/or compound requests is rather
heavy for support and usage. But it is important, especially in complex cases, with many samples in case.

Notes on complexity
-------------------
If we deal with cases containing larger number of samples,
it becomes quite obvious that all the variety described above is not enough.
Indeed, the cases discussed above are model examples “from textbooks”.
It is customary for medical doctors to work with them, but they are not enough.

Anfisa provides ways to work in these complex cases,
but it is not surprising that they are really difficult at all stages:
both for support in the interface and for the user to work with these features.

But all this is extremely important, and therefore covered.

Appendix
========

Formal Definition of Compound Heterozygous
------------------------------------------
We distinguish two variants of compound heterozygous variants (compound hets to be short):

* Compound on a gene
* Compound on a transcript
* Possibly, in the future we might look for variants compound on exons

Further I am using the word “base” to denote either gene or transcript, depending on what kind of base is used.

We divide all possible conditions on variants into two categories:
*base* dependent (or parameterized on base)
and base independent (i.e. dependent only on a position, ref and alt).
This is mostly applicable when transcript is used as a base.

A majority of base dependent conditions are aggregates on base, such as maximum or minimum of base-dependent data.

Examples of the transcript independent conditions:

* Allele frequency in gnomAD
* Clinical Significance in ClinVar

Examples of the transcript dependent conditions:

* Calculated Consequences (e.g. frameshift, missense, synonymous, 5_prime_UTR), this is usually the most severe consequences over all genes and transcripts that include the variant. When we calculate compound hets on transcript (parametrizing by transcript), we cannot aggregate over all transcripts, rather we are looking for variants that are both annotated as missense on the same transcript.
* Distance from exon/intron boundary. This is usually a minimum between the distances to exon over all transcripts.

There is a special case, when instead of genomic coordinate we use exon number as a position.
This is special because exon number is dependent on a transcript.

A set of a priori conditions we will call an apriori filter.

A pair of variants constitute a compound heterozygosity on a base if:

#. Exists a base (gene or transcript), such that it contains both variants
#. Variants are in trans, i.e. one of the pair is inherited from the mother and another is from the father
#. They both satisfy the apriori filter
#. If any of the conditions in the apriori filter is base-dependent, then they both pass the filter in the same base.

**Examples for #4**:

Suppose that an apriori filter includes a condition
that variants must be missense or synonymous and suppose we have two variants v1 and v2.

*A*:

There are two genes, g1 and g2, such that g2 is located inside an intron of g1.
Variant v1 is located in an exon of g1 (and therefore not in g2) and variant v2 is located in an exon of g2
(and therefore in the intron of g1).

Both variants are annotated for the most severe consequences as missense.
However, they do not constitute a compound het pair because for one of the variants,
the missense annotation is related to g1 (and its transcript t1) and for the other
it is related to g2 (and its transcript - t2).
V2 should have intronic annotation for g1 and v1 is either not in g2 or might be up/downstream of it.
These are not compound heterozygous regardless of whether gene or transcript is used as a base.

*B*:

Both variants are in the same gene, g1.
There are two transcripts of g1: t1 and t2 that overlay the region of both v1 and v2.
In t1, v1 is within an exon and thus satisfy the condition that it are missense or synonymous,
but v2 is in an intron of t1.
In another transcript, t2, v2 is in exon and v1 is in 3_prime_UTR.

In this case, if we select gene as the base, then this pair constitute a compound het.
However, if we select transcript as a base, it does not.
This is because, there exists a gene that both variants have most severe consequences
being missense or synonymous in the same gene, but there is no single transcript for which that would be true.



