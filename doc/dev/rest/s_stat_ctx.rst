Property status context descriptor
==================================

.. index:: 
    Property status context descriptor; data structure

Format
------

| ``{`` *dictionary of options*
| ``}``

Description
-----------
The descriptor is used as parameter **ctx** in requests that :doc:`collect statistics<../concepts/status_report>` for filtering properties. Generic purpose for it is to tune this collection procedures for different filtering properties. Up to now it affects only :doc:`variety/panel units<../concepts/variety>`.

Variety context options:
------------------------

|   **max-rest-size**: *integer*

The option changes upper bound for non-zero symbols report; default value is 300 so with this option the Front-End can change this bound

|   *unit_name.* **base-panel**: *string*


Using this option, of this kind (name of variety unit is part of option name), the Front-End can obtain detailed statistics for genes in specific panel. This regime does not generate **panels** returning value in response.

For example: ``"Symbol.base-panel": "ACMG59"``
    
See also
--------
:doc:`../concepts/status_report`

:doc:`../concepts/variety`

:doc:`ds_stat`  
:doc:`dtree_stat`  
:doc:`statunits`  
:doc:`statfunc`  
