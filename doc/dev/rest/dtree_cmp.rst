dtree_cmp
=========
        **Comparison of decision trees**

.. index:: 
    dtree_cmp; request

Synopsis
--------
**dtree_cmp** 

    **Arguments**: 

        **ds**: dataset name
        
        **dtree**: *optional* name of applying decision tree

        **code**: *optional* code of applying decision tree
        
        **other**: name of second decision tree *string*
        
    **Return value**: 
    
    | ``{`` *dictionary*
    |    "**cmp**":  compare report
    |       ``[`` *list* of blocks
    |           ``[`` *list of strings* ``]``
    |       ``]``
    |  ``}``
    
Description
-----------
Request reports difference between two :term:`decision tree` :term:`codes<decision tree code>`. 

First decision tree is set by either **dtree** or **code** (see discussion :ref:`here<dtree_code>`)
 
Second decision tree should be registered as :doc:`solution item<../concepts/sol_pack>`, so it is stored on server side by name **other**.

Result of comparison is split onto string blocks. In each block two first letters on the line are the same, value of first letter indicates meaning of the block, second letter on line is always space ' '.

Comment
-------
The request is out of use in the current version. But it can be used to extend the system functionality in next releases.
