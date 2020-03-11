ws_list
=======

Synopsis
--------

.. index:: 
    ws_list; request

**ws_list** 

    **Arguments**: 

        **ds**: dataset name
        
        **filter**: *optional* name of applying filter
        
        **conditions**: *optional* list of applying 
            :doc:`condition descriptors<s_condition>`
            *in JSON string representation*

        **zone**: *optional* :doc:`zone descriptor<s_zone>`
            *in JSON string representation*
        
    **Return value**: 
    
    | ``{`` *dictionary*
    |       "**ds**":   dataset name, *string*
    |       "**total-counts**": ``[`` *list*
    |                       **[0]**: total count of variants, *int*
    |                       **[0]**: total count of transcripts, *int* ``]``
    |       "**filtered-counts**": ``[`` *list*
    |                       **[0]**: filtered count of variants, *int*
    |                       **[0]**: filtered count of transcripts, *int* ``]``
    |       "**records**: ``[`` *list* of :doc:`s_record` ``]``
    | ``}``
    
    
Description
-----------

The request is the principal one for organizing :ref:`full<full_viewing_regime>`
variant of :ref:`viewing regime<viewing_regimes>`.

The request affects only :term:`workspaces<workspace>` and return list of 
:term:variant` record descriptors.

If arguments **filter**, **conditions**, **zone** are not set, 
result of request is the complete list of records in dataset returns. 
Otherwise result is restricted by :term:`filter` and/or condition on :term:`zone`.

To define :term:`filter` use either **filter** or **conditions**. See details 
:ref:`here<fiter_conditions>`.

See also
--------
:doc:`ds_list`