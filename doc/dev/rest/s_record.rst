Record descriptor
=================

.. index:: 
    Record descriptor; data structure

Format
------

| ``{`` *dictionary*, 
|       "**no**":    variant order number, *int*
|       "**lb**:     variant label, *string*
|       "**cl**":    variant color code, *string*
|       "**dt**:  *optional* details map, *string*
|  ``}``

Description
-----------
The descriptor contains the short information about variant sufficient to render variant in variant list presentation.

Property **dt** returns in case of request :doc:`ws_list` and represents bitmap of selected :term:`transcripts<transcript>`. Map contains of symbols ``0``, ``1`` and is used in request  :doc:`reccnt` as argument **details** for proper highlight of selected transcripts.

Current list of color codes:

    ================ ==
    ``grey``
    ``green``
    ``yellow``
    ``yellow-cross``
    ``red``
    ``red-cross``
    ================ ==
    
Used in requests
----------------
:doc:`ws_list`   

:doc:`ds_list`
