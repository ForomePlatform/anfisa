Notes on Zygosity 
=================

The purpose of this text is to explain (or interpret) some portion of genomics in terms of informatics. We take care of correct informational formulations for data structures (in JSON format) and tasks to be supported.

Definitions: case, samples 
--------------------------

:term:`Dataset` represents **case** i.e genomics information on one or many persons - **samples** - from the same family. Each sample in case is identified by **id**.

Examples of id: ``"bgm9001a1"``, ``"bgm9001u1"``

Sample id starts with case id, then letter ``a`` (affected) or ``u`` (unaffected), and a number from 1 to upper. Id of proband always ends up with ``"a1"`` (in medical cases we proband is always "affected") . 

The typical case is **trio**: samples are proband and two parents. Note that some tasks in below are formulated only in context of this scope. 

Zygosity states
---------------

Most of chromosomes for human are pairwise, so a mutation/variant applying to a sample has one of the following states:

* Zygosity 0: variant is absent

* Zygosity 1: variant is heterozygous, it presents on one chromosome copy

* Zygosity 2: variant is homozygous, it presents on both copies of chromosome
    
Males have chromosomes X and Y in one copies, so a mutation/variant on these chromosomes for male sample has one of the following states:

* Zygosity 0: variant is absent

* Zygosity 2: variant is hemozygous, it does present on single copy of chromosome
    
*Attention*: in hemozygous state a variant presents in one copy, however it is more convenient to define zygosity number as 2, since it is essentially more similar to homozygous case than to heterozygous one.

Zygosity conditions
-------------------
We need to define meaningful conditions for zygosity number for variants. 
So let us define the following 5 *string* (not *int*!) constants:

``“2”``,    ``“2-1”``,    ``“1”``,    ``“1-0”``,    ``“0”``

Formally speaking, we can define one more meaningful constant: ``"0-2"``, but let us interpret this case as we do not define condition at all: all variant are passed.

.. _zygosity-scenario:

Zygosity scenario
-----------------
Zygosity scenario is join of zygosity conditions for samples in case. In JSON format it has form:

    | ``{`` *dictionary*
    |       <zygosity condition constant>: ``[`` *list of* samples id ``]``
    |       ...
    | ``}``

.. _standard-zygosity-scenarios:

Standard zygosity scenarios
---------------------------
    
Let us consider split of samples in case on two groups: affected/unaffected. 

The following scenarios are important in practice: 

* **Homozygous Recessive/X-linked**:  ``{“2”:`` *affected*, ``“1-0”:`` *unaffected* ``}``

* **Autosomal Dominant**:             ``{“2-1”:`` *affected*, ``“0”:`` *unaffected* ``}``

* **Compensational**:                 ``{“0”:`` *affected*, ``“2-1”:`` *unaffected* ``}``

Comments:

    **Autosomal Dominant** - probably bad: variant presents for all affected and is absent for all unaffected

    **Homozygous Recessive** - variant probably breaks gene, but has no effect while there is second good (gene) copy 
        
    **X-linked** - variant probably bad, it affects all male samples and females in homozygous state
        
    **Compensational** - variant is probably good, it fixes (screens) up illness caused by other facts 

*Notes*: 
    
* we call group of affected samples as **problem group**

* for a dataset the **default problem group** is preset by different letters ``a`` and ``u`` in id of samples; however it is good if the user can define problem group directly

.. _compound-request:
        
Zygosity events and compound requests
-------------------------------------

Let us fix some diapason or diapasons of positions on chromosome as "gene" (see :ref:`below<gene_aproximations>` for details). Then for some fixed zygosity scenario it is possible to count how many variants with this scenario presents inside the "gene". Let us call these variants as "events".

    We are ready to define **compound request** in the following form:
    
    | ``[`` *list of* conditions for scenarios
    |       ``[`` *list*
    |           **[0]**: minimal count of events, **positive int**
    |           **[1]**: :ref:`zygosity scenario<zygosity-scenario>`
    |       ``]``, ...
    | ``]``

The result of compound request is not empty only if for all scenarios in the list there are not less than the defined count of events.

Strongly speaking, a compound request applies to "genes", and its result is either empty, or *list of lists* of variants that cause events. The current version of the system does not support so complex selection objects, so we interpret result of compound request as a joined plain list of variants.

.. _compound-heterozygous:

Compound heterozygous variants
------------------------------

The following compound request is important in practice. It applies to trio:

    | ``[``
    |       ``[1, {“1”: {`` *proband*, *proband's mother* ``}, “0”: {`` *proband`s father* ``}},``
    |       ``[1, {“1”: {`` *proband*, *proband's father* ``}, “0”: {`` *proband`s mother* ``}}``
    | ``]``
    
Comments.

* The main idea of request: let us consider case when only proband is affected. It might happen that on some "gene" each parent has (different) dangerous variant in heterozygous state. These variants have no effect because second copy of gene are not broken. But proband has both copies of "gene" broken: one copy is broken by one of dangerous variants, ans second copy - by another one. 
    
* From informational point of view, the detection of compound events is a clear tasks. In practice however there are serious difficulties to prepare proper setup for this detection. Results of the procedure might be good only if most part of benign variants are filtered out before the detection process. It is a matter of experiments, so the system provides extended functionality for this special kind of experimental activity.
    
.. _gene_aproximations:    
    
Approximations to gene locations
--------------------------------

The system supports 3 variants of gene approximation:

* ``"transcript"``: shared transcript

* ``"gene"``: shared gene

* ``"rough"``: non-intersecting transcripts
    
The first two variants use :term:`transcripts<transcript>` as a base filtering item, so they are applicable only in :term:`WS-datasets<WS-dataset>`. 

In practice the first variant is most good for precision purposes. But it might be not so good in recall: not all transcripts are well studied and registered up to now. For recall purposes use ``"rough"`` approximation: it causes many false positive effects however it filters out variants that can not be found with first two approximation variants.

Conclusion
----------
Detection for variants of standard scenarios and compound heterozygous variants are standard tasks in genomics, so it is important to support it in the most easy way. 

On another hand, the functionality based on direct definition of scenarios and/or compound requests is rather heavy for support and usage. But it is important, especially in complex cases, with many samples in case. 
