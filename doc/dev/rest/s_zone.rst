Zone descriptor
===============

.. index:: 
    Zone descriptor; data structure

Format
------

| ``{`` *dictionary*, 
|        "**zone**": zone name, *string*
|        "**title**": title, *string*
|        "**variants**":  ``[`` *list of strings* ``]``
| ``}``

Description
-----------

The descriptor contains information about zones state. It is used in 
request :doc:`zone_list` as return value, either in single or serial form; 
    
In serial form **variants** is dropped.
Property **title** is used for rendering. Property **zone** is hidden for 
the user, and is base technical identifier of zone.

In current version the following zones are provided:

    ===========  =================   =======================
     **title**      **zone**
    ===========  =================   =======================
    Gene          ``Symbol``
    Gene_List     ``Panels``
    Sample        ``Has_Variant``
    Tag           ``_tags``
    Cohort        ``Variant_in``     *in special cases*
    ===========  =================   =======================
    
Used in requests
----------------
:doc:`zone_list`  :doc:`ws_list`   
