ws_list
=======
        **Current list of variants**

.. index:: 
    ws_list; request

Synopsis
--------

**ws_list** 

    **Arguments**: 

        **ds**: dataset name
        
        **filter**: *optional* name of applying filter
        
        **conditions**: *optional* list of applying 
            :doc:`condition descriptors<s_condition>`
            *in JSON string representation*

        **zone**: *optional* :
        
        | ``[`` list of zone settings
        |       ``[``
        |             **[0]**:  zone name, *string*
        |             **[1]**:  ``[`` variants ``]``, *list of strings*
        |        ``]``, ...
        | ``]``  *in JSON string representation*
        
    **Return value**: 
    
    | ``{`` *dictionary*
    |       "**ds**":   dataset name, *string*
    |       "**total-counts**": ``[`` *list*
    |                       **[0]**: total count of variants, *int*
    |                       **[1]**: total count of transcripts, *int* ``]``
    |       "**filtered-counts**": ``[`` *list*
    |                       **[0]**: filtered count of variants, *int*
    |                       **[1]**: filtered count of transcripts, *int* ``]``
    |       "**records**: ``[`` *list* of :doc:`s_record` ``]``
    | ``}``
    
    
Description
-----------
The request is the principal one for organizing :ref:`full<full_viewing_regime>` variant of :doc:`../concepts/view`.

The request affects only :term:`workspaces<workspace>` and return list of :term:variant` record descriptors.

If arguments **filter**, **conditions**, **zone** are not set, result of request is the complete list of records in dataset returns. Otherwise result is restricted by :term:`filter` and/or condition on :term:`zones<zone>`.

Nonempty **zone** list can contain special pair of strings ``["NOT", true]``. In this case **zone** option works in reverse context: records satisfying condition on zones are filtered out. (It might be helpful for work with :term:`tagging`.)

To define :term:`filter` use either **filter** or **conditions**. See details :ref:`here<fiter_conditions>`.

Comment
-------
The request format supports applying of multiple zones, butthe current user interface allows to set only one zone at time. Extension of the user interface is expected in future development.

See also
--------
:doc:`ds_list`

:doc:`../concepts/ws_pg`

