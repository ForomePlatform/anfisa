Record descriptor
=================

Format
------

| ``{`` *dictionary*, 
|       "**no**":    variant order number, *int*
|       "**lb**:     variant label, *string*
|       "**cl**":    variant color code, *string*
|  ``}``

Description
-----------

The descriptor contains the short information about variant sufficient 
to render variant in variant list presentation.

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
:doc:`ws_list`   :doc:`ds_list`
