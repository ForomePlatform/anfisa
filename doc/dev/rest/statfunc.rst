statfunc
========
        **Function filtering support**
        
.. index:: 
    statfunc; request

Synopsis
--------

**statfunc** 

    **Arguments**: 

        **ds**: dataset name
        
        **rq_id**: ID of request series
        
        **filter**: *optional* name of applying filter
        
        **conditions**: *optional* list of applying :doc:`condition descriptors<s_condition>`
            *in JSON string representation*

        **dtree**: *optional* name of applying decision tree

        **code**: *optional* code of applying decision tree
        
        **no**: *optional* position on tree, *int as string*
        
        **unit**: function name
        
        **param**: parameters of function
                *JSON string representation*
        
        **ctx**: *optional*, :doc:`context descriptor<s_stat_ctx>`
            *in JSON string representation*
            
    **Return value**: :doc:`s_prop_stat`

Description
-----------
Request returns status report for :term:`function<functions>` applied to selection determined by arguments:

- filter applies if either **filter** or **conditions** is set (see discussion :ref:`here<fiter_conditions>`)

- decision tree applies if either **dtree** or **code** is set (see discussion :ref:`here<dtree_code>`)
    
    in this case **no** is necessary, since decision tree defines series of selections
    
- otherwise selection is the full list of variants in dataset

See discussion and functions reference in :doc:`func_ref`.

See also
--------
:doc:`s_prop_stat` 

:doc:`func_ref`

:doc:`../concepts/filters_reg`
