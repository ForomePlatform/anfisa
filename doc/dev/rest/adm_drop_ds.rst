adm_drop_ds
================
        **Drop of dataset**
        
.. index:: 
    adm_drop_ds; request

Synopsis
--------
**adm_drop_ds** 

    **Arguments**:
    
        **ds**: dataset name

    **Return value**: ``"Dropped <dataset name>"`` *as plain string or* ``null`` 

Description
-----------
Some :term:`WS-datasets<WS-dataset>` can be dropped (i.e. removed) in automatical way via this request. 
The configuration option :ref:`adm-drop-datasets<adm_drop_datasets>` determines for what dataset names this operation is allowed on the instance of the system. 

Comment
-------
Usually it is the system administrator competence to decide where it is time to drop a dataset. This method was added for testing purposes. But there can be other possibilities to use this functionality in concrete environments.
