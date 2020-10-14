Decision Tree Syntax Reference
==============================

In the text below we define and discuss a dialect of Python that is used to construct a decision tree.

:term:`Decision tree` is an algorithm of :term:`filtration` that allows to build complex procedure of :term:`variants<variant>`  selection.

Decision tree logic
-------------------

A Decision Tree consists of a sequence of branching points. A result of application of any Decision Tree is a set that we will call "final selection". The process starts with a set consisting of all of the variants (in a whole genome of patient family members or a cohort of patients). This set "travels" through a tree trunk. At each branching point a subset of variants is removed from the set and is either excluded from further consideration (thrown away) or unconditionally included in the final selection. Variants that have been neither excluded or included continue their "travel".

- Initially we have the whole set of items (variants) as working selection.
    
- At each branching point:
    - If-instruction selects some subset of working selection;
    - Return-instruction determines whether the selected subset should be included in the "final selection" (return ``True``) or excluded (return ``False``):
        
|      **if** *condition* :
|           **return** *bool decision*
        
    - after If-instruction the selection set is (probably) reduced, and next instruction is applied to this reduced set; next instruction is one more If-instruction, or...
        
    - final instruction in code is always Return-instruction that determines what should be done to the rest of working selection: to include it in the "final selection" (``True``) or to exclude it (``False``):
    
|       **return** *bool decision*

There is only one other type of available instruction, Label-instruction:

|       **label** (*string*)
    
This instruction can be inserted to decision tree code before any If-instruction. So the user has a possibility to mark state of working selection by label mark. This mark can be used in complex procedures (see :term:`functions` reference: :doc:`../rest/func_ref`, functions :ref:`Compound_Heterozygous()<Compound_Heterozygous>` and :ref:`Compound_Request()<Compound_Request>`).

Syntax principles
-----------------

There are three levels of details in description of Decision Tree Python dialect:

- **neccessary level**: the dialect deals with very restricted subset of Python, so only small amount of Python constructions are allowed in it; below is complete description of this subset
    
- **good practice level**: some constructs discussed below are recommended as "good practice"; similar constructs that are not considered good practices could be refactored to their "good practice" analogues in the process of interactive changes of a decision tree

- **simplification level**: since the dialect of Python is very "thin", for purposes of easy typing and reading it supports the following "simplifications":
        
    - **string constants** can be typed without quote symbols ``""`` or ``''`` if they are correct Python identifiers or constants ``True, False, None``
    
    - **lists vs. sets**: in case when code refers list objects with ``[]`` parentheses, it is good practice to use set notation with ``{}``; indeed in most cases, order of elements in a "list" is irrelevant, while ``{}`` are more readable
                
Top level constructions
-----------------------

There are three top level constructions available in the dialect:

|   **if** *condition* :
|       **return** *bool decision*
|
|   **return** *bool decision*
|
|   **label** (*string*)

The following rules must be hold:

    - All instructions (excluding Return-sub-instruction of If-instruction) must start at the first character of a line, no indentation
        
    - A top-level Return-instruction must be the last nonempty line of code

    - Label-instruction can be used before any If-instruction
    
    - Empty lines between top-level constructions are allowed
    
    - Comments are acceptable only as a full line, not as a part of a line with code; 
        comments should start with ``#`` character, possibly after spaces (note also that comments are not acceptable after the last instruction)
        
    - It is a good practice to place comment lines only before top-level instructions
    
    - *condition* in If-instruction might be quite long, so one might need multiple lines; 
        It is good practice to use parentheses to group these lines, instead of ``\`` characters.
    
Condition constructions
-----------------------

Combined conditions
^^^^^^^^^^^^^^^^^^^
Operators ``and``, ``or`` and ``not`` and parentheses ``()`` are fully supported for building complex conditions from atomic ones.

Atomic condition uses identifier of corresponding :term:`filtering property` once per atomic condition. (See also :doc:`../rest/s_condition` for understanding atomic operations.)

Atomic numeric condition
^^^^^^^^^^^^^^^^^^^^^^^^
Has form of usual Python comparison operation with operators ``<``, ``<=``, ``==``, ``>=``, ``>``. Double form is acceptable, for example:

    |   *min value* < *property_id* <= *max_value*
    
Best practice: use only operators ``<``, ``<=``, ``==``; in case of operator ``==`` place property identifier on the left.

Atomic enumerated condition
^^^^^^^^^^^^^^^^^^^^^^^^^^^
Has different form in dependency of join mode of condition:

    |   **OR**:
    |           *property_id* **in** ``{`` *set*/*list of value strings* ``}``
    |
    |   **AND**:
    |           *property_id* **in** **all** ``({`` *set*/*list of value strings* ``})``
    |
    |   **NOT**:
    |           *property_id* **not in** ``{`` *set*/*list of value strings* ``}``
    |
    
Notes:

    - notation above uses ``{}`` set parentheses; though it is recommended as a good practice, list parentheses ``[]`` are also supported
        
    - operator **in** is supported for all enumerated properties, including :term:`status<status property>` (single-value properties) and :term:`multiset<multiset property>` (multi -value properties).

        For :term:`status<status property>` its semantic is simple and intuitive.
        
        In case of :term:`multiset<multiset property>` this notation is more sophisticated: the condition is positive when intersection of two sets is nonempty, i.e. at least one value of the property matches at least one value in the given set; it can be "explained" by a way that object representing filtering property redefines operator **in** from the left
        
    - in case of **AND** join mode interpretation of **all()** pseudo-function is even more sophisticated: it can be "explained" if result of **all()** redefines" **in** operation in a very specific way from the right.
    
    - in terms of Decision Tree there is no strong need for **NOT** join mode, because operator ``not`` is supported outside atomic conditions
        
Atomic function conditions
^^^^^^^^^^^^^^^^^^^^^^^^^^
Function conditions have similar form to enumerated conditions with a  change of *property id* to

    *function_name* (*parameters*)

Syntax for parameters is Python standard. Since all values of the parameters must be JSON objects (however, with a change of JS constants ``true/false/null`` to Python counterparts ``True/False/None``), there should be no problems in setting parameters up. ("Simplifications" are also acceptable for parameters).
    
See :doc:`../rest/func_ref` for reference of available functions and their parameters.

Decision Tree system support
----------------------------

The following objects are explicated from the code of decision tree:

* **Points** correspond to instruction in code; each If- or Return- instruction corresponds to a point with state of selection set: either working one or pre-final. The user needs to know how many items (variants) are in these sets, and moreover has possibility to study distribution of values for filtering properties of items in these sets. (See :doc:`dtree_pg` for details)

* **Atomic conditions** are "atomic" fragments of condition in If instructions. There can be many atomic conditions in one If instruction. It is important functionalify of the system to locate them and provide their modifications. 

* **State labels** can be defined in code by Label instructions. They are used with complex :term:`functions`. This functionalify requires high level of qualification and attendacy of the user, however it might be very important in practice.
        
A decision tree can be modified in either of two ways:

* manual typing and modifications of decision tree code

* interactive actions modifying various details of decision tree, see :doc:`../rest/s_dtree_instr` for reference.
        
Interactive regime allows to make any meaningful transformation of decision tree, so there is no strong need to use manual regime at all. Manual regime requires is helpful for complex manipulations with boolean logic of conditions and, of course for copy/paste operations.

See also
--------
:doc:`filtration`

:doc:`dtree_pg`

:doc:`../rest/s_condition`

:doc:`../rest/func_ref`

:doc:`../rest/s_dtree_instr`
