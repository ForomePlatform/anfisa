Solution items in work
======================

Here we discuss usage of two kinds of items: :term:`filters<filter>` and :term:`decision trees<decision tree>`

Item of such kinds is some complex object, and in practice it has one of three status states (note that the user can use item always):

    * preset solution, see :doc:`sol_pack`
        The user can not modify it, names of such solutions have preffix symbol `⏚`
    
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
 
Names of filters and decision trees must start with any letter ("alpha") symbol (any alphabet) and must not contain spaces; in terms of js the criterium is as follows:
    
    ::
        
        /^\S+$/u.test(name) && (name[0].toLowerCase() != name[0].toUpperCase())

See also
--------
:doc:`sol_pack`
    
