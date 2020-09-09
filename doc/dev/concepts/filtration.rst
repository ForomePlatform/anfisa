Filtration procedures
=====================

Filtration is the most important functionality of the system. A dataset contains many
:term:`variants<variant>` with a lot of associated data, and the system provides filtration 
tools to make effective selection of variants and their :term:`transcripts<transcript>`.

There are two types of filtration tools, and both are based on :term:`conditions` applied
to :term:`filtering properties<filtering property>` of variants (or transcripts). 

There is additional mechanism of :term:`functions` which are aggregation information 
objects that are used in conditions like filtering properties if arguments of function 
is properly set.) See :doc:`../rest/func_ref` for details and reference.

Thus conditions on filtering properties and functions are base atomic object of any 
filtration procedure, and any filtration procedure contains then and possibly join them 
somehow.

Typed of filtration procedures:

    - :term:`Filter` is just sequence of (atomic) :term:`conditions`, and this sequence
        applies to variants(transcripts) one by one, in conjunctional way; so the result condition
        of filter is a join of (atomic) conditions by operator AND
        
    - :term:`Decision tree` is more advanced filtration tool. It allows to combine atomic 
        conditions by all logical operators AND, OR and NOT and build essentially more 
        complex (but good enough for reading and understanding) rules of selection. 
        However, the base atomic  conditions used here are the same :term:`conditions` as above.

See also
--------
:doc:`filters_reg`

:doc:`dtree_syntax`

:doc:`../rest/func_ref`
