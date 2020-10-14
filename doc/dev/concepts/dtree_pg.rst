Decision tree work page
=======================

:term:`Decision tree` page looks very complex. However, essential part of its functionality has strong back-end support, so the the Front End complexity is not so hard as one can expect. Essential portion of real difficulties in Front End application support focuses on the same issue as in other work pages: :doc:<status_report>.

The page provides the following functionality issues for work with with all :term:`datasets<dataset>`, :term:`xl-<xl-dataset>` and `ws-<ws-dataset>` ones
   
- :term:`Decision tree` complex representation with possibility to select any applicable :term:`point<decision tree point>`
    
- :ref:`Delayed report of point counts<dtree_points_report>`, actual for :term:`xl-datasets<xl-dataset>` where count evaluations might be heavy
    
- Complex of visualization of properties state, in context of current decision point selection, see :doc:`status_report`        

- :ref:`Auxiliary viewing regime<auxiliary_viewing_regime>`, in context of current decision point 
    
- Interactive modification of decision tree, see full reference in :doc:`../rest/s_dtree_instr`. Operations of this layer are split onto three categories of operations:
        
    - **INSTR**: manipulations with logical structure of the code
    
    - **POINT**: creation of new atomic conditions in context of available properties state, and placement of them into the code of decision tree
    
    - **ATOM**: tuning atomic conditions in decision tree code

- Operation support:
    
    - manual edition of decision tree code
    
    - support decision trees as :doc:`sol_work`
    
    - creation of :term:`secondary workspace`
        
In case of :term:`ws-dataset` the page uses :term:`transcripts<transcript>` as :term:`filtration` items, otherwise in case of :term:`xl-dataset` :term:`variants<variant>` are used.

Decision trees are powerful tool of :doc:`filtration`, they are integrated with other parts of the system by two ways:

- there is always a possibility to create :term:`secondary workspace` to save result of filtration workspace

- for :term:`ws-datasets<ws-dataset>` only: filtration results of all decision trees that are registered as :term:`solution items<solution item>` are available in :doc:`filters_reg` as values of special property :term:`Rules`.

Interactive modification level (see :doc:`../rest/s_dtree_instr` for reference) forms complete functionality to make any meaningful change in decision tree. So there is no need for the user to direct change of :doc:`Python code of decision tree<dtree_syntax>`. It might be useful only for control complex cases of boolean operations.
        
REST API requests 
-----------------
For support Decision Tree work page:

- :doc:`../rest/dsinfo`
    Dataset information

- :doc:`../rest/dtree_set`
    Decision tree page setup

- :doc:`../rest/dtree_counts`
    Delayed evaluations of item counts for decision tree points

- :doc:`../rest/dtree_stat`
    Filtering properties status report for decision tree page

- :doc:`../rest/dtree_check`
    Decision tree code check (used for validation of manual code edition)

- :doc:`../rest/dtree_cmp`
    Comparison of decision trees

- :doc:`../rest/ds2ws`
    Creation of secondary workspace

- see also :doc:`status_report` 
