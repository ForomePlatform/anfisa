Filtering properties restriction
================================

There are a lot of different :term:`filtering properties<filtering property>` provided for :term:`filtration` mechanism in the system. So the system provides :term:`clasification of properties<filtering properties classification>` and the user can restrict available filtering properties based on this classification, or restore full variety of properties.

The classification uses three facet classification lists, and each filtering property has association in each of facet lists. In most situations each property associates with only a single item in each facet lists. But it is possible for a specific property to be accociated with multiple items in a single facet list.

The complete list of filtering properties is available in the :term:`filtration regimes<filtration>` by default. The user can define restriction, and it is Front End application that should provide this functionaliy. Most useful criterium of restriction is defined on only one of facets, by selection of a subset of items from facet classification list. Front End application also can combine restrictions of two or more facets. 

There are the following requirements for the The Front End application in context of restriction mechanism:

    * There cannot be a scenario to define a criterium of facet restriction with empty set of unrestricted properties

    * Properties can be used in current filter or decision tree but restriced by criterium on facet restriction; the user should handle these properties properly

Rest API requests support this functionality by providing sufficient information for filtering properties classification:

    * :doc:`../rest/s_ds_descr` structure provides **classes** field that describes structure of filtering properties classification
    
    * :doc:`../rest/s_prop_stat` structure contains **classes** field that describes classification for the specific property

See also
--------
:doc:`filtration`

:doc:`filters_reg`

:doc:`dtree_pg`

:doc:`../rest/s_ds_descr`

:doc:`../rest/s_prop_stat`
