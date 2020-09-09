adm_update
==========
        **Force vault state update**

Synopsis
--------

.. index:: 
    adm_update; request

**adm_update** 

    **Arguments**: *none*

    **Return value**: ``"Updated"`` *as plain string*

Description
-----------

Initiates checking procedure for all :term:`datasets<dataset>` in the :term:`vault` immediately. 
Does not wait for end of the procedure.

Comment
-------

Standard procedure of the vault check starts on server in background periodically 
(once per 30 seconds by default :ref:`service configuration<job_vault_check_period>`)
Using this call, one can initiate the check procedure immediately.
