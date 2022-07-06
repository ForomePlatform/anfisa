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
The descriptor contains information about zones state. It is used in request :doc:`zone_list` as return value, either in single or serial form; 
    
In serial form **variants** is dropped.

Property **title** is used for rendering. 

In current version the following zones are provided:

    ===========  =================   =======================
     **title**      **zone**
    ===========  =================   =======================
    Gene          ``Symbol``
    Gene List     ``Gene_Lists``
    Sample        ``Has_Variant``
    Tag           ``_tags``
    Cohort        ``Variant_in``     *in special cases*
    ===========  =================   =======================

Property **zone** is hidden for the user, usually it corresponds to name of :term:`unit`, filtering property. So the extended Front-End application logic can collect information about zones not only by :doc:`zone_list` but by :doc:`statunits` al well, using **zone** attribute as unit name.

The exceptional zone is tags, ``"_tags"``: tags must not be filtering property, but request :doc:`statunits` provides special support for this name and this logic. 
    
Used in requests
----------------
:doc:`zone_list`  

:doc:`ws_list`   

:doc:`statunits`   
