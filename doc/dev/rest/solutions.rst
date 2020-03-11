solutions
=========

Synopsis
--------

.. index:: 
    solutions; request

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

The request returns names of preset :ref:`solution items<solution_items>` available for :term:`dataset`

Types of solution items supported in the current version:

  ==============    ===
  filter
  dtree
  panel
  zone
  tab-schema
  ==============    ===

The request might be used for experimental extensions of the system 
functionality and user interface.
