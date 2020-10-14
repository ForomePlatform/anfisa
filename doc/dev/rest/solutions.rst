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
        
    **Return value**: lists of solution items available in dataset
    
|  ``{`` *dictionary*
|        name of solution type, *string*: ``[`` *list of strings* ``]``
|        ...
|  ``}``

Description
-----------

The request returns names of preset :doc:`../concepts/sol_pack` available for :term:`dataset`

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

See also
--------
:doc:`../concepts/sol_pack`
