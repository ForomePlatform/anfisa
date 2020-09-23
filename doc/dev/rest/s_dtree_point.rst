Decision Tree Point descriptor
==============================

.. index:: 
    Decision Tree Point descriptor; data structure

Format
------

| ``{`` *dictionary*, 
|        "**kind**": kind of point, 
|                          ``"If"``, ``"Return"``, "``"Label"`` *or* ``"Error"``
|        "**level**": level of point, ``0`` *or* ``1``
|        "**decision**": decision of point, *boolean* or ``null``
|        "**code-frag**": HTML-presentation of code, *string*
|        "**actions**: actions applicable to point, ``[`` *list of strings* ``]``
| ``}`` 


Description
-----------
Data structure is used in returning properties of request :doc:`dtree_set` and contains information about :term:`point of decision tree<decision tree point>`. 

There are 4 kinds of points: 

    **If** corresponds to ``if`` Python instruction, 
    
        Has condition with atomic :term:`condition<conditions>` on filtering properties, and possibly complex structure formed by AND/OR/NOT operations
        
        Followed by point of type **Return** with **level** equal to ``1``
        
    **Return** corresponds to ``return`` Python instruction
    
        Only this kind of points has **decision** property with boolean value.
        
        There are two cases for **Return** points:
        
        - Point follows any **If** statement, only in this case **level** property equals to ``1``.
            
        - Last point of decision tree is always **If** point with **level** equal to ``0``.
        
    **Label** corresponds to instruction ``label(...)`` and defines 
        :term:`state label on decision tree<decision tree state label>`. 
        
    **Error** corresponds to incorect Python-style block in decision tree
    
Points of last two kinds are not applicable for counting items in dataset.

If it is not discussed above, **decision** is always ``null`` and **level** is always ``0``.

Property **code-frag** contains ready HTML-presentation of code fragment that corresponds to 
point:
    
- Since it is being evaluated using Pygments_ package, it is essential for the User Interface to provide proper CSS support for Pygments styles; 

- Code fragment presentation of **If** point contains empty HTML ``<span>`` tags for marking up  atomic conditions:
    
    ``<span class="dtree-atom-mark" id="__atom_1-1"></span>``, 

    where ``1-1`` are replaced by two integers indexing atomic condition. 
    
    Atomic condition might be marked by warning:

    ``<span class="dtree-atom-mark warn" id="__atom_1-1" title="..."></span>``, 
            
    The Front End application can use this markup to set up proper access to atomic conditions and as result to support code  modifying actions of type ``"ATOM"``, see details  :ref:`here<dtree_atom_actions>`. 
    
    See also description of property **cond-atoms** in :doc:`dtree_set`.

- Code fragment presentation of **Error** point uses HTML ``<span class="line-error">`` to to markup lines with bad code. Also it uses ``<span class="note-err" title="...">`` with special symbol inside in presentation of the first line of error fragment. This ``<span>`` contains error message, and the user can see if when mouse cursor is over this span.
                
.. _Pygments: https://pygments.org/
    
Actions of ``"INSTR"`` type available for the point are prepared in **actions** property. See list of all supported actions is :ref:`here<dtree_instr_actions>`.

Used in request
----------------
:doc:`dtree_set`
