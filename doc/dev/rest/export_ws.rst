export_ws
=========
        **Export workspace as archive**

.. index:: 
    export_ws; request

Synopsis
--------

**export_ws** 

    **Arguments**: 

        **ds**: dataset name
        
        .. index:: 
            support; argument of export_ws

        **support**: *optional* with support information 

        .. index:: 
            doc; argument of export_ws
        
        **doc**: *optional* with full documentation
        
    **Return value**: 
    
    | ``{`` *dictionary*
    |      "**kind**": kind of archive, *string* ``"tar.gz"``
    |      "**url**": path to archive for download, *string*
    | ``}``

Description
-----------
The functionality of :doc:`import<import_ws>` and export :term:`workspaces<workspace>` serves for collaboraton purposes. Same workspace can be distributed between different instances of Anfisa to focus attention of various specialists to a difficult case represented in a short form. 

The request affects only :term:`workspace` kind of datasets, and produces archive in ``*.tgz`` form ready for download. This file can be used in another Anfisa instance to create dataset duplicate by using :doc:`import_ws` operation. 

By default both options **support** and **doc** are on, use values ``no``, ``off`` or ``0`` to turn them off.

Option **support** controls if :doc:`solution items<../concepts/sol_pack>` (tags, filters, decision trees) are stored in archive or not. If yes, all of them will be restored on export dataset archive on another Anfisa instance.

Option **doc** controls if full dataset documentation is stored in archive. It is actual if the workspace is a derived one, and full documentation refers to the base full dataset. By default this full documentation will be attached to archive. 

See also
--------
:doc:`import_ws`
