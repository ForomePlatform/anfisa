statfunc
========

Synopsis
--------

.. index:: 
    statfunc; request

**statfunc** 

    **Arguments**: 

        **ds**: dataset name
        
        **filter**: *optional* name of applying filter
        
        **conditions**: *optional* list of applying 
            :doc:`condition descriptors<s_condition>`
            *in JSON string representation*

        **dtree**: *optional* name of applying decision tree

        **code**: *optional* code of applying decision tree
        
        **no**: *optional* position on tree, *int as string*
        
        **unit**: function name
        
        **param**: parameters of function
                *JSON string representation*
        
    **Return value**: :doc:`s_prop_stat`

Description
-----------

Request returns :ref:`status report<status_report>` 
for :ref:`function<functions_support>` applied to 
selection defined by arguments:

    - filter applies if either **filter** or **conditions** is set (see discussion
      :ref:`here<fiter_conditions>`)

    - decision tree applies if either **dtree** or **code** is set (see discussion
      :ref:`here<dtree_code>`)
      
      in this case **no** is necessary, since decision tree
      defines series of selections
        
    - otherwise selection is the full list of variants in dataset

Available in the current version functions and their parameters are documented
in :doc:`functions`. 

See also
--------
:doc:`s_prop_stat` 
:ref:`Function support<functions_support>`
:doc:`functions`
