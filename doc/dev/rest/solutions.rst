solutions
=========
        **Solution items information**

.. index:: 
    solutions; request

Synopsis
--------

**solutions** 

    **Arguments**: 

        **ds**: dataset name

        **entry**: *optional* entry name
        
    **Return value**: 
    
    If **entry** is set returns *optional string*, kind of :term:`solution item`
    
    Otherwise: lists of solution items available in dataset
    
|  ``{`` *dictionary*
|        name of solution type, *string*: ``[`` *list of strings* ``]``
|        ...
|  ``}``

Description
-----------

In geneicic context (without **entry** in arguments) the request returns names of preset :doc:`../concepts/sol_pack` available for :term:`dataset`

Panel names are split to groups by unit/property names for which these panels are made. Key for group is 

``panel/`` *property*

(In current version all panels are made for ``Symbol``, so return dictionary contains now only ``"panel/Symbol"`` entry)

Types of solution items supported in the current version:

  =================    ===
  filter
  dtree
  zone
  tab-schema
  -----------------    ---
  panel/*property*
  =================    ===

The request might be used for experimental extensions of the system functionality and user interface.

If **entry** is set, the requests returns kind of registered :term:`solution item`, if any. The purpose of this call is discussed :ref:`here<sol_items_namespace>`. 

See also
--------
:doc:`../concepts/sol_pack`
