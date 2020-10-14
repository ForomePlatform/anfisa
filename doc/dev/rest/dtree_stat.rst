dtree_stat
==========
        **Filtering properties status report for decision tree page**

.. index:: 
    dtree_stat; request

Synopsis
--------

**dtree_stat** 

    **Arguments**: 

        **ds**: dataset name
        
        **tm**: *optional* time delay control option, in seconds, *float as string*

        **dtree**: *optional* name of applying decision tree

        **code**: *optional* code of applying decision tree
        
        **no**: position on tree, *int as string*

    **Return value**: 
    
    | ``{`` *dictionary*
    |      "**total-counts**": count of items in dataset
    |           ``[`` *list*
    |               **[0]** count of variants, *int*
    |               **[1]** *optional* count of transcripts, *int*
    |           ``]``
    |      "**filtered-counts**": count of items filtered
    |           ``[`` *list*
    |               **[0]** count of variants, *int*
    |               **[1]** *optional* count of transcripts, *int*
    |           ``]``
    |      "**stat-list**": ``[`` *list of* :doc:`s_prop_stat` ``]``
    |      **rq_id**": unique request id, for use in secondary requests, *string*
    |  ``}``
    
Description
-----------
The request supports :doc:`../concepts/status_report` in context of :doc:`../concepts/dtree_pg`. Filtering properties status data are collected in context of :term:`decision tree point`.

See explanations of input argument **tm** and returning properties **stat-list**, **rq-id** :doc:`here<../concepts/status_report>`

Applied :term:`decision tree` is defined by either **dtree** or **code** arguments, see discussion :ref:`here<dtree_code>`. 

Comments
--------
The request is much more simple comparing to its analogue :doc:`ds_stat`; both methods initiate :doc:`../concepts/status_report`.

See also
--------
:doc:`statunits`     

:doc:`statfunc`

:doc:`../concepts/status_report`
