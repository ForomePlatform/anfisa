Viewing regimes
===============

Since :term:`variants<variant>` have variety of properties the system provides full functionality for view and study these properties. In this regime the main control structure is list of variants. Usually they are :term:`filtered<filtration>`: variants in the list are selected from the whole :term:`dataset` by :term:`filters<filter>`, :term:`decision trees<decision tree>` and :term:`zones<zone>`.

The user can select any of variant form the list, and view and study the whole information about this variant. See also details :doc:`view_pre`.

On different pages the system provides two variants of viewing regime

.. _full_viewing_regime:

* Full viewing regime
    
    REST API request: :doc:`../rest/ws_list`

    In context of comparatively small :term:`workspace` user can see all selected variants. Features of workspace functionality, :term:`tagging` and :term:`zone` mechanisms are integrated with this regime.         
    
.. _auxiliary_viewing_regime:
    
* Auxiliary viewing regime

    REST API request: :doc:`../rest/ds_list`

    In contexts of :term:`XL-dataset` or :term:`decision tree` viewing regime looks simpler - no integration with tagging and zones. But in these contexts there is no guarantee that selection is small enough, so the system makes special preparations to restrict list of visible variants:

    * If list is comparatively small (less than 300 variants), visible list if full one (property **records** is used in request :doc:`../rest/ds_list`)
        
    * If list is comparatively large (more than 50 variants), only 25 randomly selected samples are visible (property **samples** is used in request :doc:`../rest/ds_list`)

See also
--------

:doc:`view_pre`
