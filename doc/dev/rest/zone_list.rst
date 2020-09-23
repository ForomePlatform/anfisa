zone_list
=========
        **Zone support information**

.. index:: 
    zone_list; request

Synopsis
--------

**zone_list** 

    **Arguments**: 

        **ds**: dataset name
        
        **zone**: *optional* zone name
    
        .. index:: 
            rec; argument of zone_list
        
    **Return value**: 
    
    |  * if **zone** is undefined,
    |       ``[`` *list of* :doc:`zone descriptors<s_zone>` ``]``
    |  * if **zone** is defined
    |       :doc:`zone descriptor<s_zone>`

Description
-----------
The request affects only :term:`workspaces<workspace>` and is a joined form of two different requests:

* It returns the complete list of available :term:`zones<zone>` (descriptors are in short forms)

* If zone is defined, it returns the complete information about this :term:`zone`

Zones are secondary mechanism for filtering variants in :term:`viewing regime`. Each zone represents list of values (variants) for some property of variant records. The user can select subset of this list, and view only variant records with selected values of properties.

Zone Tag supports special functionality that can be useful for the user. :term:`Tagging` mechanism is not well accurate, so the user can not use tags for accurate :term:`filtration`. However the user can restrict list of variants by tags - using zone mechanism.

Comment
-------
Name of a zone is some string with internal technical meaning. 
It is hidden for user: do not use it for rendering.

See also
--------
:doc:`../concepts/ws_pg`
