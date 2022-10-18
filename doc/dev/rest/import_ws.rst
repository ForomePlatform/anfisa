import_ws
=========
        **Create workspace from archive file**

.. index:: 
    import_ws; request

Synopsis
--------

**import_ws** 

    **Arguments**: 

        .. index:: 
            name; argument of import_ws

        **name**: name of dataset to be created
        
        .. index:: 
            file; argument of import_ws

        **file**: archive contents 

    **Return value**: 
    
    | ``{`` *dictionary*
    |      "**created**": name of created archive, *string*
    |      *or*
    |      "**error**": error message, *string*
    | ``}``

Description
-----------
The functionality of import and :doc:`export<export_ws>`  :term:`workspaces<workspace>` serves for collaboraton purposes. Same workspace can be distributed between different instances of Anfisa to focus attention of various specialists to a difficult case represented in a short form. 

The request imports dataset archive in ``*.tgz`` form, produced in another Anfisa instance by :doc:`export_ws` operation. 

The name of new dataset **name** should be new one, it can not be name of existing dataset or :ref:`reserved<ReservedDSNames>` one. As a string, it should be nonempty, without space symbols and length limited by 255. 

See also
--------
:doc:`export_ws`
