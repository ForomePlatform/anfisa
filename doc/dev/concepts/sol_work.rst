Solution items in work
======================

Here we discuss usage of three kinds of items: :term:`filters<filter>`, :term:`decision trees<decision tree>` and :term:`symbol panel<symbol panel>`.

Filters and decision trees
--------------------------

Item of such kinds is some complex object, and in practice it has one of three status states (note that the user can use item always):

    * preset solution, see :doc:`sol_pack`
        The user can not modify it, Names of such solutions are marked by preffix symbol `⏚`
    
    * dynamical solution
        The user can create, modify, rename and delete it. This item is persistent object, so the user can use it in next sessions.
        
    * working solution
        Item in this state is editable but temporary. It can be stored as solution one (by setting its name). 

For both kinds of solution items there is REST API request provides operations over solution items: create/update and delete:

    - for filters: :doc:`../rest/ds_stat`
    
    - for decision trees: :doc:`../rest/dtree_set`
        
If request in REST API uses :term:`filter` item, it can be determined in argument:

.. _fiter_conditions:

    - **filter** *either* as name of filter solution item
    
    - **conditions** *or* list of :term:`condition<conditions>` descriptors, as working copy of item

If request in REST API uses :term:`decision tree` item, it can be determined in argument:

.. _dtree_code:

    - **dtree** *either* as name of decision tree solution item
    
    - **code** *or* as :term:`decision tree code`, as working copy of item
    
.. _panels_as_sol_items:

Panels
------

Panels are lists of names (symbols), and their usage as solution items is slightly different from one for filters and decision trees:

    - Panels are split onto groups by panel type. The full name of solution item type for panels has prefix ``panel.``, the current version of the system supports only one type "Symbol", so the full name of this type is ``panel.Symbol``
    
    - Preset and dynamical panels are supported as well as for filter and decision tree types. The difference is: dynamical panel names are marked by prefix symbol ⚒, and vice versa preset panel names are not marked
    
.. _active_symbols:

    - Instead of working solution, each panel type has single one special hidden panel that is stored persistently. The symbols in this panel are interpreted as :term:`active<active symbols>`. So this special panel is used as default panel in symbol/panel filtration complex, see details :doc:`here<variety>`

Notes
-----
.. _sol_version_indicators:
    
* For each type of solution items the system provides version integer indicators of the type common state: indicator increases if any solution item of this type created, updated or deleted. Indicators are reset on restart of the system. Indicators can be used in the Front-End logics for detection when the correspondent information on solution items should be reloaded from Back-End.
 
* Names of dynamical solution items must start with any letter ("alpha") symbol (any alphabet) and must not contain spaces; in terms of js the criterium is as follows:
    
    ::
        
        /^\S+$/u.test(name) && (name[0].toLowerCase() != name[0].toUpperCase())

See also
--------
:doc:`sol_pack`
:doc:`variety`
