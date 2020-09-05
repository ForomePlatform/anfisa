macro_tagging
=============
        **Macro Tagging operation**

Synopsis
--------

.. index:: 
    macro_tagging; request

**tagging_selection** 

    **Arguments**: 

        **ds**: dataset name
        
        **tag**: tag name
        
        **off**: *optional* ``true`` or anything else 
        
        **filter**: *optional* name of applying filter
        
        **conditions**: *optional* list of applying 
            :doc:`condition descriptors<s_condition>`
            *in JSON string representation*

        **zone**: *optional* :
        
        | ``[`` list of zone settings
        |       ``[``
        |             **[0]**:  zone name, *string*
        |             **[1]**:  ``[`` variants ``]``, *list of strings*
        |        ``]``, ...
        | ``]``  *in JSON string representation*
        
    **Return value**: 
    
    | ``{`` *dictionary*
    |       "**tags-state**": indicator of tags update state
    | ``}``
    
    
Description
-----------

The request operates over all :term:`tag<tagging>` with given name for variants 
present in :term:`root dataset`. 

If option **off** is ``true``, the operation clears **tag** from all 
records of root dataset (see :doc:`ws_tags` for details).

If option **of** is not set to ``true``, the operation marks all filtered records in 
current dataset with **tag** and text value of tag as "True", and also clears
**tag** from all other records of root dataset.

For details of arguments **fiter**, **conditions**, **zone** see :doc:`ws_list`

See also
--------
:doc:`ws_list`

:doc:`ws_tags`

