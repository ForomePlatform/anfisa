Decision Tree Syntax Reference
==============================

In the text below we define and discuss a dialect of Python that 
is used to formulate decision tree by its code.

:term:`Decision tree` is an algorithm of :term:`filtration` that allows
to build complex procedure of :term:`variants<variant>` 
(and :term:`transcripts<transcript>`) selection.

Decision tree logic
-------------------

The procedure of filtration builds resulting set by the following logic: 
    
    - on the first stage we have the whole set of items (variants or transcripts) 
        as working selection.
        
    - (intermediate) If-instruction of decision tree selects some subset of 
        working selection;
        including Return-instruction determines what shoult be done with this set: 
        either add it to the resulting 
        set on decision ``True`` or just drop it on ``False``:
        
|      **if** *condition* :
|           **return** *bool decision*
        
    - after If-instruction the selection set is (probably) reduced, and next instruction
        is applied to this reduced set; next instruction is one more If-instruction, or...
        
    - final instruction in code is always Return-instruction that determines what 
        should be done to the rest of working selection: to add it to the resulting 
        set on ``True`` or drop in on ``False``:
    
|       **return** *bool decision*

There is only one other type of available instruction, Label-instruction:

|       **label** (*string*)
    
This instruction can be inserted to decision tree code before any If-instruction. So 
the user has a possibility to mark state of working selection by label mark. This mark
can be used in complex procedures (see :term:`functions` reference: :doc:`../rest/func_ref`,
functions :ref:`Compound_Heterozygous()<Compound_Heterozygous>` and 
:ref:`Compound_Request()<Compound_Request>`).

Syntax principles
-----------------

There are three levels of details in description of Decision Tree Python dialect:

    - **neccesary level**: the dialect deals with very restricted subset of Python, 
        so only small amount of Python constructions are allowed in it; below is
        complete description of this subset
        
    - **good practice level**: some constructions discussed below are recommended as
        "good practice"; analogous constructions that are not recommended by such a way
        might be refactored to its "good practice" analogues in process of interactive 
        changes of decision tree

    - **simplification level**: since the dialect of Python is very "thin", for purposes 
        of easy typing and reading it suports the following "simplifications":
            
            - **string constants** can be typed without quote symbols ``""`` or ``''`` if they 
                are correct Python identifiers or constants ``True, False, None``
            
            - **lists vs. sets**: in case when code refers list objects with ``[]`` parentheses, 
                it is good practice to use set notation with ``{}``; indeed in practically
                all cases of usage elements order in "list" does not matter, and ``{}`` 
                are more easily readable
                
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

    - All these instructions (but including Return-sub-instruction of If-instruction) must 
        start line, no indentation
        
    - Top-level Return-instruction must be the last nonempty line of code

    - Label-instruction can be used before any If-instruction
    
    - Empty lines between top-level constructions are acceptable
    
    - Comments are acceptable only in form of full line, not as a rest of coding line: 
        such lines should start with ``#`` letter, possibly after spaces (note also that 
        comments are not acceptable after finishing instruction)
        
    - It is good practice to place comment lines only before top-level instructions
    
    - *condition* in If-instruction might be heavy, so one needs multiple lines for it;
        It is god practice to use parentheses to group these lines, but not symbols ``\``.
    
Condition constructions
-----------------------

Combined conditions
^^^^^^^^^^^^^^^^^^^
Operators ``and``, ``or`` and ``not`` and parentheses ``()`` are fullly acceptable
to build complex conditions from atomic ones.

Atomic condition uses identifier of correspondent :term:`filtering property` once 
per atomic condition. (See also :doc:`../rest/s_condition` for understanding of atomic 
operations.)

Atomic numeric condition
^^^^^^^^^^^^^^^^^^^^^^^^
Has form of usual Python comparison operation with operators ``<``, ``<=``, ``==``,
``>=``, ``>``. Might have double form, for example:

    |   *min value* < *property_id* <= *max_value*
    
Best practice: use only operators ``<``, ``<=``, ``==``; in case of operator ``==``
place property identifier on the left.

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
    
Comments:

    - notation above uses ``{}`` set parentheses; it is a good practice, however
        list parentheses ``[]`` are acceptable
        
    - if enumerated property is :term:`status<status property>` one, operator **in**
        is completely adequate 
        
        In case of :term:`multiset<multiset property>` this notation is sophisticated: 
        in reality condition is positive when intersection
        of two sets is nonempty; it can be "explained" by a way that object 
        representing filtering property redefines operator **in** from the left
        
    - in case of **AND** join mode interpretation of **all()** preudo-function is 
        sophisticated even more: it can be "explained" if result of **all()** 
        redefines" **in** operation in a very specific way from the right.
    
    - in terms of Decision tree there is no strong need in **NOT** join mode,
        since operator ``not`` is supported outside atomic conditions
        
Atomic function conditions
^^^^^^^^^^^^^^^^^^^^^^^^^^
Conditions have form similar to enumerated ones up to change *property id* to 

    *function_name* (*parameters*)

Syntax of usage parameters is standard one for Python. Since all values of
parameters must be JSON objects (up to change JS constants ``true/false/null``
to Python ones ``True/False/None``), there should be no problems in setting 
parameters up. ("Simplifications" are also acceptable in parameters).
    
See :doc:`../rest/func_ref` for reference of available functions and their parameters.

Decision Tree system support
----------------------------

The following objects are explicated from code of decision tree:

    * **Points** correspond to instruction in code; each If- or Return- instruction
        correspons to a point with state of selection set: either working one or pre-final.
        The user needs to know how many items (variants/transcripts) are in these sets,
        and moreover has possibility to study distribution of values for filtering 
        properties of items in these sets. (See :doc:`dtree_pg` for details)
    
    * **Atomic conditions** are "atomic" fragments of condition in If instructions.
        There can be many atomic conditions in one If instruction.
        It is important functionalify of the system to locate them and provide 
        their modifications. 
    
    * **State labels** can be defined in code by Label instructions. They 
        are used with complex :term:`functions`. This functionalify requires 
        high level of qualification and attendacy of the user, however it 
        might be very important in practice.
        
Two regimes of decision tree modifications are supported in the system:

    * manual typing and modifications of decision tree code
    
    * interactive actions modifying various details of decision tree, see 
        :doc:`../rest/s_dtree_instr` for reference.
        
Interactive regime allows to make any meaningful transformation of decision tree,
so there is no strong need to use manual regime at all. Manual regime requires 
is helpful for complex manipulations with boolean logic of conditions. 

See also
--------
:doc:`filtration`

:doc:`dtree_pg`

:doc:`../rest/s_condition`

:doc:`../rest/func_ref`

:doc:`../rest/s_dtree_instr`

