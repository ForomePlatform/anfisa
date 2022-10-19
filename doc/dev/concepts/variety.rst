Variety and panel filtering complex
===================================

Variety and panel filtering properties complex is a special pair of :term:`enumerated filtering properties<enumerated property>`. The complex is based on support of :term:`symbol panels<symbol panel>` as :ref:`solution items<panels_as_sol_items>`.

The variety of symbols for some dimension might be too wide. Gene symbols is the base example of such dimension (estimately 20000 items, only protein coding genes are taken in account), and currently it is the single dimesion of such a kind that is supported in the system. Since the nomenclature of symbols is so wide, the user has plenty of reasons to make selections for some groups of symbols. These groups form :term:`symbol panels<symbol panel>`, and the system provides functionality to operate them as :ref:`solution items<panels_as_sol_items>`. This is the beackground of variery/panel complex.

The complex is needed when nomenclature of symbols is too wide. Gene symbols is the base example of such a nomenclature, and the system iterprets it as "dimension" named as ``Symbol``. There are plenty of reasons to select some of these symbols, form :term:`symbol panel<symbol panel>` and use these panels in :term:`filtration process<filtration>`. So the system provides functionality for access and modification of symbol panels as :term:`solution items<solution item>`. And this is the background functionality of variery and panel complex support.   

.. index:: 
    variety filtering property

:term:`Variery filtering unit<variety property>`, is a special subtype of :term:`enumerated unit<enumerated property>` that collects statistics (see :doc:`status_report`) in a special restricted way. In contrast to the ordinary :term:`enumerated property`, the statistics for this property does not include whole list of property values(symbols):
    
    - only :term:`active symbols` are traced in complete form; 
    
        - by default, active symbols form special hidden symbol panel, see details :ref:`here<panels_as_sol_items>`
        
        - active symbol list can be controlled manually with :doc:`ctx<../rest/s_stat_ctx>` argument
        
    - other symbols are traced only if they really present in the applied set (with positive count, ones with zero count are ignored), and only if the list of these symbols is short enough (up to 300 now) 
    
.. index::
    panel filtering property

:term:`Panel filtering unit<panel property>` is just :term:`enumerated unit<enumerated property>` that represents presence of symbols from variety unit (all symbols, not only active ones) in available symbol panels. 

Currently the system provides two pairs of units:
    
    - **Symbols/Panels** for all datasets
    
    - **Transcript_Gene/Transcript_Gene_Panels**, his pair is actual for :term:`WS-datasets<WS-dataset>` and deals with :term:`transcript variants<transcript variant>`. 

.. _actsym_purpose:
    
Initially list of active symbols for a new dataset is empty, and it is a responsibility of user to point out here the symbols of interest. But the application can help the user in this completion. On REST API level there is parameter **actsym** in two requests (:doc:`../rest/ds_stat`, :doc:`../rest/dtree_set`); if this option is on, all symbols used in :doc:`filtration tools<filtration>` are automatically added to active symbol list. Other helpful features can be implemented in the Front-End application.
    
*Technical notes*: 

* There is technical difference between panel units and ordinary enumerated ones. Evaluation of statistics for panel and variety unit pair is just the single evaluation procedure, so the real statistics for panels is a part of statistical report of variety unit, and formal statistics for panel unit is kept empty. 

* Both pairs of variety/panel complex in the current version use the same named dimensions: variety unis use the same named dimension ``Symbol``, and panel units use ``panel.Symbol``. This markup feature allows to detect usage of concrete symbols and panels from :doc:`filtration tools<filtration>`. 

* Technical name of hidden panel of :term:`active symbols` for dimension ``Symbol`` is ``__Symbol__`` 
