export
======
        **Export operation**

.. index:: 
    export; request

Synopsis
--------
**export** 

    **Arguments**: 

        **ds**: dataset name
        
        **filter**: *optional* name of applying filter
        
        **conditions**: *optional* list of applying 
            :doc:`condition descriptors<s_condition>`
            *in JSON string representation*

        **zone**: *optional* :
        
        | ``[`` list of zone settings
        |       ``[``
        |             **[0]**:  zone name, *string*
        |             **[1]**:  ``[`` variants ``]``, *list of strings*
        |             **[2]**:  false, *add it if negation of condition is required*
        |        ``]``, ...
        | ``]``  *in JSON string representation*
        
    **Return value**: 
    
    | ``{`` *dictionary*
    |      "**kind**": ``"excel"``
    |      "**fname**": URL to excel file to download
    |  ``}``
    
Description
-----------
The request creates exported Excel file for selected variants. 

The count of records in the reports is limited. See :doc:`csv_export` for details of this limitation.

Selection is defined by:

- :term:`filter` applies if either **filter** or **conditions** is set (see discussion :ref:`here<fiter_conditions>`)

- :term:`zone` applies if **zone** is set - actual for :term:`workspaces<workspace>` only (see :doc:`ws_list` for details).

Resulting file is created on servers side and is ready for download from moment of creation and later.

(Cleaning of these files are subject of Anfisa administration)

See also
--------
:doc:`csv_export`     
