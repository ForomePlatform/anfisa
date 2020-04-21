statunits
=========
        **Delayed evaluations for filtering property status data**

Synopsis
--------

.. index:: 
    statunits; request

**statunits** 

    **Arguments**: 

        **ds**: dataset name
        
        **tm**: *optional* time delay control option, in seconds, *float as string*

        **rq_id**: ID of request series
        
        **filter**: *optional* name of applying filter
        
        **conditions**: *optional* list of applying 
            :doc:`condition descriptors<s_condition>`
            *in JSON string representation*

        **dtree**: *optional* name of applying decision tree

        **code**: *optional* code of applying decision tree
        
        **no**: *optional* position on tree, *int as string*
        
        **units**: list of property names 
                *list of strings in JSON string representation*
        
    **Return value**: 
    
    | ``{`` *dictionary*
    |      "**rq-id**": ID of request series, *string*
    |      "**units**": evaluated status reports
    |           ``[`` *list* of :doc:`s_prop_stat` ``]``
    | ``}``

Description
-----------

Requests of this type initiates :doc:`../concepts/status_report`
and form series of requests initiated by request 
:doc:`ds_stat` or :doc:`dtree_stat`, see details in references.

**rq_id** argument should be get from result of initiation request.
Arguments **filter**, **conditions** or **dtree**, **code**, **no**
should be the same as in initiation request.

Returning data must contain status report for first property (the first 
entry in **units** as property name), other properties can be not evaluated
if there is no enough time (see details for argument **tm** in references).

See also
--------
:doc:`ds_stat` 

:doc:`dtree_stat`

:doc:`../concepts/status_report`

:doc:`../concepts/filters_reg`
