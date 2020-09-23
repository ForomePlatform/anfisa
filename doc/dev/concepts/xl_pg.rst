XL-dataset work page
====================

:term:`XL-dataset` page is essentially simpler than :doc:`ws_pg`, and contains only subset of ws-functionality. But in context of :term:`XL-dataset` evaluations might be heavy, so the main focus of the Front End application support for this page is an issue of heavy evaluations and long delays.

The page supports the following functionality issues:
    
- Full complex of :doc:`filters_reg` with its features:

    - :doc:`status_report`
    
    - support :term:`filters<filter>` as :doc:`sol_work`

    - the logic of regime requires top detailization of information, so  :term:`transcripts<transcript>` are used as :term:`filtration` items instead of :term:`variants<variant>`

- :ref:`Auxiliary viewing regime<auxiliary_viewing_regime>` as the main regime    

- operation support:
    
    - creation of :term:`secondary workspace`
    
    - :term:`Export` operation: form and provide access to download Excel document with properties of filtered variants, in case if count of variants is limited (up to 300 variants). 
        
REST API requests 
-----------------
For support WS-dataset work page:

- :doc:`../rest/dsinfo`
    Dataset information

- :doc:`../rest/ds_list`       
    List of variants in in auxiliary viewing regime

- :doc:`../rest/reccnt`
    Aspect-based full view presentation of variant

- :doc:`../rest/export`
    Export operation

- :doc:`../rest/ds2ws`
    Creation of secondary workspace

- see also :doc:`filters_reg` 
