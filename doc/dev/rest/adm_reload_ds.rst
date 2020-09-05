adm_reload_ds
=============
        **Force dataset reload**

Synopsis
--------

.. index:: 
    adm_reload_ds; request

**adm_update** 

    **Arguments**:
    
        **ds**: dataset name

    **Return value**: ``"Reloaded <dataset name>"`` *as plain string*

Description
-----------

The method reloads dataset in memory.

Comment
-------

The method can be used in administrative work, especially if dataset set 
of :doc:`solutions<../concepts/sol_work>` is changed by :doc:`../adm/adm_mongo` utility.  
