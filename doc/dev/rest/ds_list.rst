ds_list
=======
        **List of variants in auxiliary viewing regime**
        
.. index:: 
    ds_list; request

Synopsis
--------
**ds_list** 

    **Arguments**: 

        **ds**: dataset name
        
        **filter**: *optional* name of applying filter
        
        **conditions**: *optional* list of applying :doc:`condition descriptors<s_condition>`
            *in JSON string representation*

        **dtree**: *optional* name of applying decision tree

        **code**: *optional* code of applying decision tree
        
        **no**: *optional* position on tree, *int as string*
        
    **Return value**: 
    
    | ``{`` *dictionary*
    |       "**task_id**":  task ID, *int* 
    | ``}``

    **Return value for task**:    
    
    | ``{`` *dictionary*
    |    "**records**":  *optional* full list 
    |                if selection is sufficiently small 
    |        ``[`` *list* of :doc:`s_record` ``]``
    |    "**samples**":  *optional* samples list 
    |                if selection is sufficiently large 
    |        ``[`` *list* of :doc:`s_record` ``]``
    | ``}``
    
Description
-----------
The request is the principal one for organizing :ref:`auxiliary<auxiliary_viewing_regime>` variant of :doc:`../concepts/view`. So this request is used in context of  of :term:`XL-dataset` or :term:`decision tree`. 

The request does not return proper information at once. It creates :term:`background task`. The client needs to use request :doc:`job_status` to receive the proper result after some delay. 

Properties **records**, **samples** are discussed :ref:`here<auxiliary_viewing_regime>`.

Selection of variants is defined by arguments:

- filter applies if either **filter** or **conditions** is set (see discussion :ref:`here<fiter_conditions>`)

- decision tree applies if either **dtree** or **code** is set (see discussion :ref:`here<dtree_code>`)
    
    in this case **no** is neccessary, since decision tree defines serie of selections
    
- otherwize selection is the full list of variants in dataset

Comment
-------
Implementation of the request via :term:`background task` is strongly neccessary for :term:`XL-datasets<xl-dataset>`, since its evaluation might take essential time. It is not true in context of :term:`decision tree` of :term:`workspace`, so it is possible to add to REST API direct variant of the request in this case if a developper needs it.

See also
--------
:doc:`ws_list`
