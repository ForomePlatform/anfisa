Condition descriptor
====================

.. index:: 
    Condition descriptor; data structure


:term:`Conditions` are the kernel objects of the system, since they are atomic objects that are used in :doc:`../concepts/filtration`. 

:term:`Filters<filter>` are just list of conditions, conjunction of them. So it is important functionality for user to define and modify conditions interactively in :doc:`../concepts/filters_reg`. 
    
In context of :term:`decision tree` conditions have form of :term:`decision tree atomic condition`, and the user can modify them in interactive way in :doc:`../concepts/dtree_pg`. 

Format for numeric property
---------------------------

| ``[`` *list* 
|       **[0]**: ``"numeric"``
|       **[1]**: name of property, *string*
|       **[2]**: bounds, 
|          ``[`` *list*
|                **[0]**: minimal bound, *optional numeric*
|                **[1]**: is minimal bound non-strict, *boolean*
|                **[2]**: maximum bound, *optional numeric*
|                **[3]**: is maximal bound non-strict, *boolean*
|          ``]``
| ``]``

Comments
^^^^^^^^
    
    - Format of condition allows define one or both minimal and maximal bounds 
        for (single) numeric property
    
    - ``true`` value for indicators on positions **[1]** and **[3]** means 
        that equality to the bound is ok; 
        
    - condition is correct if at least one of bounds is set (positions **[0]**/**[2]**)
        and indicators (positions **[1]** and **[3]** are ``true`` or ``false``);
        there are a variety of ways to make improper condition: formally it can be 
        correct but never true for any variant, please take care of it
        
    - format of condition makes no distinction between integer and float numerics, 
        please take care of it 
    

Format for enumerated property 
------------------------------

| ``[`` *list* 
|       **[0]**: ``"enum"``
|       **[1]**: name of property, *string*
|       **[2]**: join mode: ``"OR"`` *or* ``"AND"`` *or* ``"NOT"``
|       **[3]**: value variants:
|          ``[`` *list of strings* ``]``
| ``]``

Comments
^^^^^^^^
Format of condition allows to define conditions for both :term:`status<status property>` and :term:`multiset properties<multiset property>` with some remarks
    
- In case of :term:`status property` join mode ``"AND"`` is out of sense. 
    Otherwise it selects variants for which all the selected values are set on for the property. 

- Join mode ``"NOT"`` is just negation to join mode ``"OR"``

- For single value selection (length of array in position **[3]** is 1) there is no difference between join modes ``"OR"`` and ``"AND"``

Format for function condition
-----------------------------

| ``[`` *list* 
|       **[0]**: ``"func"``
|       **[1]**: name of property, *string*
|       **[2]**: join mode: ``"OR"`` *or* ``"AND"`` *or* ``"NOT"``
|       **[3]**: value variants:
|          ``[`` *list of strings* ``]``
|       **[4]**: function arguments, *JSON structure*
| ``]``

Comments
^^^^^^^^
See :doc:`func_ref` for functions definition and reference.

All notes to condition for enumerated property are actual in this case too.

Different functions have different format of function arguments (position **[4]**) and their own specific check if condition is good for this function.

Available functions and their arguments are documented in :doc:`func_ref`

