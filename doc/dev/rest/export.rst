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

- :term:`filter` applies if either **filter** or **conditions** is set (see discussion :ref:`here<fiter_conditions>`)

- :term:`zone` applies if **zone** is set - actual for :term:`workspaces<workspace>` only. (Nonempty **zone** list can contain special pair of strings ``["NOT", true]``. In this case **zone** option works in reverse context: records satisfying condition on zones are filtered out.)

Resulting file is created on servers side and is ready for download from moment of creation and later.

(Cleaning of these files are subject of Anfisa administration)
