Zone descriptor
===============

Format
------

| ``{`` *dictionary*, 
|        "**zone**": zone name, *string*
|        "**title**": *optional* title, *string*
|        "**variants**":  ``[`` *list of strings* ``]``
| ``}``

Description
-----------

The descriptor contains information about zone selection is used in API as follows:

    * In request :doc:`ws_list` it is used as input argument
    
      **title** is not necessary here, and **variants** means selection list 

    * Request :doc:`zone_list` returns zone descriptor either in single or serial form; 
    
        - In serial form **variants** is dropped
      
        - In single form **variants** means the complete list of values (but not selection) 

In current version the following zones are provided:

    ===========  =================   =======================
     title        zone_id
    ===========  =================   =======================
    Gene          ``Symbol``
    Gene_List     ``Panels``
    Sample        ``Has_Variant``
    Tag           ``_tags``
    Cohort        ``Variant_in``     *in special cases*
    ===========  =================   =======================
    
See also 
--------
Description in :doc:`zone_list`
    
Used in requests
----------------
:doc:`ws_list`   :doc:`zone_list`
