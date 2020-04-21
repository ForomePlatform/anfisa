ds2ws
=====
        **Creation of secondary workspace**

Synopsis
--------

.. index:: 
    ds2ws; request

**ds2ws** 

    **Arguments**: 

        **ds**: dataset name
        
        **filter**: *optional* name of applying filter
        
        **conditions**: *optional* list of applying 
            :doc:`condition descriptors<s_condition>`
            *in JSON string representation*

        **dtree**: *optional* name of applying decision tree

        **code**: *optional* code of applying decision tree

        **ws**: name of creating workspace
        
        **force**: forcing remove previous instance of workspace,
                *optional* 
        
    **Return value**: 
    
    | ``{`` *dictionary*
    |       "**task_id**":  task ID, *int* 
    | ``}``

    **Return value for task**:    
    
    | ``{`` *dictionary*
    |       "**ws**": name of workspace created, *string*
    |  ``}``
    
Description
-----------

The request starts :term:`background task` for creation :term:`secondary workspace`.

The client needs to use request :doc:`job_status`
to receive the proper result or error status of task after some delay. 

Selection of variants is defined by arguments:

    - filter applies if either **filter** or **conditions** is set (see discussion
      :ref:`here<fiter_conditions>`)

    - decision tree applies if either **dtree** or **code** is set (see discussion
      :ref:`here<dtree_code>`)

Secondary workspace should be of limited size: **not more than 9000 variants**.
