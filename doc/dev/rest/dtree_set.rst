dtree_set
=========
        **Decision tree page setup**

.. index:: 
    dtree_set; request

Synopsis
--------

**dtree_set** 

    **Arguments**: 

        **ds**: dataset name
        
        **tm**: *optional* time delay control option, in seconds, *float as string*

        **dtree**: *optional* name of applying decision tree

        **code**: *optional* code of applying decision tree 
        
        **instr**: *optional modifier* :doc:`s_dtree_instr`
                   *in JSON string representation*
        
    **Return value**: 
    
    | ``{`` *dictionary*
    |      **kind**: kind of dataset, ``"ws"`` *or* ``"xl"``
    |      "**total-counts**": count of items in dataset
    |           ``[`` *list*
    |               **[0]** count of variants, *int*
    |               **[1]** *optional* count of transcripts, *int*
    |           ``]``
    |      "**point-counts**": point counts of items
    |           ``[`` *list of* :doc:`s_point_count` ``]``
    |      "**code**": code of decision tree, *string*
    |      "**points**": 
    |           ``[`` *list of* :doc:`s_dtree_point` ``]``
    |      "**cond-atoms**": atomic conditions
    |           ``{`` *dictionary* 
    |                 point no, *int*: ``[`` *list of* :doc:`s_condition` ``]``
    |           ``}``
    |      "**labels**": ``[`` *list of string* ``]`` - defined state labels 
    |        
    |      "**error**": *optional* diagnostics for first error, *string*
    |      "**line**": *optional* line no for first error, *int*
    |      "**pos**": *optional* line position for first error, *int*
    |
    |      "**dtree-name**: *optional* name of current decision tree, *string*
    |      "**eval-status**": status of decision tree evaluation
    |              ``"ok"`` if evaluation is correct, other *string* otherwise
    |      **hash**: hash code associated with current tree code, *string*
    |      **dtree-list**: names of all decision trees available for dataset
    |           ``[`` *list of* :doc:`s_sol_entry` ``]``
    |      **rq_id**": unique request id, for use in secondary requests, *string*
    |  ``}``
    
Description
-----------
The request is the principal one for organizing :doc:`../concepts/dtree_pg` for all :term:`datasets<dataset>`.

If **dtree** argument is set, :term:`decision tree` with this name should be registered on the server side as :term:`solution item`. Otherwise the argument **code** must contain :term:`decision tree code`.

If **instr** argument is set (see details in :doc:`s_dtree_instr`) and instruction 
is of type ``"DTREE"``, request modifies decision tree :term:`solution item`: create, update or 
delete item with given name.

If **instr** argument is set and instruction is of other types (``"INSTR"``, ``"POINT"`` *or* ``"ATOM"``), the code of decision tree is being modified in request, and returning property **code** contains result of modifications. See :doc:`s_dtree_instr` for details.

Returning properties:

    **code**: Decision tree is defined by its code written in a dialect of Python. Returning property **code** contains actual state of it.

    **points**: Decision tree splits into sequence of :term:`decision tree points<decision tree point>`. Each point sontrols one or more lines in Python code, possibly with comment lines. Property **points** contain information on them, see :doc:`s_dtree_point` for details. 
    
    **point-counts**: Another portion of information for points, in form of list of :doc:`s_point_count`. Information can be incomplete, since evaluation of counts might be heavy procedure. Input argument **tm** controls the timeout in this case. To receive from server rest of counts the client needs to start series of delayed request :doc:`dtree_counts` using property **rq-id** as input argument. See details of this mechanism :ref:`here<dtree_points_report>`

    **cond-atoms**: Point of kind ``"If"`` contains one or many :term:`decision tree atomic conditions<decision tree atomic condition>`, or in short form "atoms". Atoms are active zones in user interface: the user can change atomic condition and it causes modification of decision tree of kind ``"ATOM"``
    
        Atoms are indexed by pair of integers: index of point and index in list of point atoms, so property **cond-atoms** is organized as dictionary with integer keys(indexes of points of type ``"If"``) and values as list of :doc:`s_condition` structures.
    
    **labels**: The property contains all :term:`state labels<decision tree state label>` defined on decision tree, it might be used for rendering purposes.
        
    **error**, **line**, **pos**: in case of errors in code of decision tree, these tree properties refer first error in the code, it might be used in rendering or work with code of decision tree
        
    **eval-status**: property is either ``"ok"`` or evaluation error report

    **dtree-list**: names of all decision trees available for dataset, this properties supports work with decision tree as :doc:`solution item<../concepts/sol_pack>`
 
Comments
--------
The request is partial analogue to :doc:`ds_stat`. Both methods are principal for support main :ref:`work pages<work_pages>` for two mechanisms of :term:`filtration` in the system.

See also
--------
:doc:`dtree_counts`     

:doc:`dtree_stat`

:ref:`Decision tree points counters evaluation with delays<dtree_points_report>`

:doc:`../concepts/dtree_syntax`
