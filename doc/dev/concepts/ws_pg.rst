Workspace page
==============

:term:`WS-dataset` page is the most complex of working pages, because it is used by the user for the most important goals: to detect single variant (or small number of variants) as a final result of dataset analysis, from large (but comparatively small, up to some thousands of variants) dataset.

The page supports the following functionality issues:
    
- :ref:`Full viewing regime<full_viewing_regime>` as the main regime    

- Full complex of :doc:`filters_reg` with its features:

    - :doc:`status_report`
    
    - support :term:`filters<filter>` as :doc:`sol_work`

    - the logic of regime requires top detailization of information, so  :term:`transcripts<transcript>` are used as :term:`filtration` items instead of :term:`variants<variant>`

- manual user work with :term:`tagging` tools to associate variants with tags and notes

    Front End can support tools to navigate the user between variants with fixed tag. Take care with these tools: the user can drop tag from variant and might be confused by tag navigation response.
    
- :term:`Zone` panel that provides "secondary" :term:`filtration` tool that can be combined with :doc:`filters_reg`

- operation support:
    
    - creation of :term:`secondary workspace`
    
    - :term:`Export` operation: form and provide access to download Excel document with properties of filtered variants, in case if count of variants is limited (up to 300 variants). 

- Special feature of Workspace page: Rules are available in :doc:`filters_reg`. Rules is special aggregated :term:`multiset property` that detects what :term:`decision trees<decision tree>` are positive on the variant. 

    This issue closes up long circle of functionality logic: decision trees are complex :term:`solution items<solution item>` that can be used for detection for variety of properties of variants, so at the WS-dataset working page the user can apply all of them to get final result.
        
REST API requests 
-----------------
For support WS-dataset work page:

- :doc:`../rest/dsinfo`
    Dataset information

- :doc:`../rest/ws_list`
    Current list of variants

- :doc:`../rest/reccnt`
    Aspect-based full view presentation of variant

- :doc:`../rest/zone_list`
    Zone support information

- :doc:`../rest/ws_tags`
    Tagging variant information retrieval and modifications

- :doc:`../rest/export`
    Export operation

- :doc:`../rest/ds2ws`
    Creation of secondary workspace

- see also :doc:`filters_reg` 
