csv_export
==========
        **Export to CSV format operation**
        
.. index:: 
    csv_export; request
    
Synopsis
--------
**export** 

    **Arguments**: 
    
        **ds**: dataset name
        
        **filter**: *optional* name of applying filter
        
        **conditions**: *optional* list of applying :doc:`condition descriptors<s_condition>`
            *in JSON string representation*

        **zone**: *optional* :doc:`zone descriptor<s_zone>`
            *in JSON string representation*

        **schema**: name of data schema
        
        .. index:: 
            schema; argument of csv_export        

    **Returns**: 
    
    Page in CSV format for download
    
Description
-----------
The request creates preentation of selected variants in CSV format. 

This method is not a proper REST API call: it does not return a JSON object but file in CSV format.

Selection is defined by:

    - :term:`filter` applies if either **filter** or **conditions** is set (see discussion :ref:`here<fiter_conditions>`)

    - :term:`zone` applies if **zone** is set - actual for :term:`workspaces<workspace>` only. (Nonempty **zone** list can contain special pair of strings ``["NOT", true]``. In this case **zone** option works in reverse context: records satisfying condition on zones are filtered out.)

In current version of the system schemes are defined in source code of the server as :term:`solution items<solution item>`, so the list of it is fixed. The schema `csv` is supportd for simple variant of export. 

.. warning:: TODO: add list and descriptions of available schemes

