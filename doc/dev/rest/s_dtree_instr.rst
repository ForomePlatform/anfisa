Decision Tree modifying actions
=================================

.. index:: 
    Decision tree action; data structure

Actions modifying :term:`decision tree` can be performed by request :doc:`dtree_set`.

There are 4 types of modifying actions:
    
    ``"DTREE"``, ``"INSTR"``, ``"POINT"`` and ``"ATOM"``
    
For all types of actions format of data is list, and first element of list is type of action.
    
DTREE modifying actions
--------------------------

    These actions operates with whole decision tree as :doc:`../concepts/sol_work`. 

Format
^^^^^^
|   ``[``
|       **[0]**: action type, ``"DTREE"``
|       **[1]**: action name (from list below), *string* 
|       **[1]**: decision tree name, *string*
|   ``]``

Actions:
^^^^^^^^
    
    **UPDATE**: update (as well as create) decision tree with given name
    
    **DELETE**: delete decision tree with given name
    
INSTR modifying actions
--------------------------
Actions of this type manipulates with logical blocks of decision tree code.
Blocks are identified by index of first point.

.. _dtree_instr_actions:

For each :term:`point<decision tree point>` list of available actions is prepared in  **actions** property of :doc:`s_dtree_point`.

Format
^^^^^^
|   ``[``
|       **[0]**: action type, ``"INSTR"``
|       **[1]**: action name (from list below), *string* 
|       **[2]**: point no, *int*
|       **[3]**: *optional* additional option, possibly required for new actions
|   ``]``

Actions:
^^^^^^^^
            *actions for blocks of* ``"If"`` *type*:
    
    **JOIN-AND**, **JOIN-OR**: join If-block with If block above with AND or OR operation 

    **SPLIT**: split If block onto series of separate blocks by AND or OR operation
    
    **NEGATE**: negate condition in If-block
    
    **DUPLICATE**: duplicate logical block
    
            *action for blocks of* ``"Return"`` *type*:
    
    **BOOL-TRUE**, **BOOL-FALSE**: change decision for return operator

            *action for any block*:
    
    **DELETE**: delete logical block    
    
    **LABEL**: set/drop :term:`label<decision tree state label>`, not yet implemented
    
    **COMMENTS**: edit comments to block, not yet implemented

POINT modifying actions
-----------------------

Actions of this type are caused by insertion of new condition over filtering property into some :term:`point of decision tree<decision tree point>`.

Format
^^^^^^
|   ``[``
|       **[0]**: action type, ``"POINT"``
|       **[1]**: action name (from list below), *string* 
|       **[2]**: point no, *int*
|       **[3]**: condition, :doc:`s_condition`
|   ``]``

Actions:
^^^^^^^^

    **INSERT**: insert condition as a new point into decision tree
    
    **REPLACE**: replace the whole condition of If-block by new condition
    
    **JOIN-AND**, **JOIN-OR**: join new condition with current condition of If-block by AND or OR operation

.. _dtree_atom_actions:
                
ATOM modifying actions
----------------------
Actions of this type are caused by user requests for modification of existing atom conditions in decision tree.

Format
^^^^^^
|   ``[``
|       **[0]**: action type, ``"ATOM"``
|       **[1]**: action name (from list below), *string* 
|       **[2]**: atom location
|           ``[`` *list*
|               **[0]**: point no, *int*
|               **[1]**: atom no in point atom list, *int*
|           ``]``
|       **[3]**: *optional*, additional argument if required
|   ``]``

Actions:
^^^^^^^^

    **EDIT**: modify atomic condition, additional argument in place **[3]** is new :doc:`s_condition`
    
    **DELETE**: delete atom from the whole condition and simplify it, no additional argument requires
        
        *Note*: in case of one atom in point, please use action ``"INSTR"/"DELETE"`` instead of this one.

Used in request
----------------
:doc:`dtree_set`
