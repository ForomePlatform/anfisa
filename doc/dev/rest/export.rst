export
======
        **Export operation**

Synopsis
--------

.. index:: 
    export; request

**export** 

    **Arguments**: 

        **ds**: dataset name
        
        **filter**: *optional* name of applying filter
        
        **conditions**: *optional* list of applying 
            :doc:`condition descriptors<s_condition>`
            *in JSON string representation*

        **zone**: *optional* :doc:`zone descriptor<s_zone>`
            *in JSON string representation*
        
    **Return value**: 
    
    | ``{`` *dictionary*
    |      "**kind**": ``"excel"``
    |      "**fname**": URL to excel file to download
    |  ``}``
    
Description
-----------

The request creates exported Excel file for selected variants. Selection should be of limited size: **not more than 300 variants**.

Selection is defined by:

    - :term:`filter` applies if either **filter** or **conditions** is set (see discussion
        :ref:`here<fiter_conditions>`)

    - :term:`zone` applies if **zone** is set - actual for :term:`workspaces<workspace>` only.

Resulting file is created on servers side and is ready for download from moment of creation and later.

(Cleaning of these files are subject of Anfisa administration)
