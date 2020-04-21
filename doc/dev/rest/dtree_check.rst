dtree_check
===========
        **Decision tree code check**

Synopsis
--------

.. index:: 
    dtree_check; request

**dtree_check** 

    **Arguments**: 

        **ds**: dataset name
        
        **code**: code of decision tree
        
    **Return value**: 
    
    | ``{`` *dictionary*
    |    "**code**":  code of decision tree
    |    **error**: *optional* error message, *string*
    |    **line**: *optional* error line no, *int*
    |    **pos**: *optional* position on error line, *int*
    |  ``}``
    
Description
-----------

Request checks if :term:`decision tree code` is correct. 

Returning properties **error**, **line**, **no** are set if error happens
and correspond to the first error in the code.
