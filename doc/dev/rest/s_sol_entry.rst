Solution Entry descriptor
=========================

.. index:: 
    Solution Entry descriptor; data structure

Format
------

| ``{`` *dictionary*, 
|        "**name**": entry name, *string*
|        "**rubric**": *optional* entry rubric, *string*
|        "**standard**": entry is standard (pre-set), *boolean*
|        "**eval-status**": evaluation status of entry, 
|                   ``"ok"`` *or* ``"runtime"`` *or* ``"error"``
|        "**upd-time**: *optional* timestamp of last update of entry,
|                   *string, time in ISO format*
|        "**upd-from**: *optional* dataset name for last update of entry,
|                   *string*
|        "**sol-version**": indicator of stat for solution entries 
|                   of this kind, *string*
| ``}``

Description
-----------
The descriptor contains information about information objects in aspect of :term:`solution items<solution item>`. Used in requests returning information about:
    
* :term:`filters<filter>`: :doc:`ds_stat`

* :term:`decision trees<decision tree>`: :doc:`dtree_set`
    
**eval-status**: ``"error"`` corresponds to fully incorrect entry state (syntax errors for example), ``"runtime"`` corresponds to problems on entry evaluaton
    
See also
--------
:doc:`ds_stat`  

:doc:`dtree_set`
