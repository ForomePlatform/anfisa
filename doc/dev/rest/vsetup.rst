vsetup
======
        **View data schema information**

Synopsis
--------

.. index:: 
    vsetup; request

**vsetup** 

    **Arguments**: 

        **ds**: dataset name
        
    **Return value**: view data schema and of dataset
    
|   ``[`` *list* of aspect descriptors
|        ``{`` *dictionary* 
|           "**name**":  aspect name, *string*
|           "**title**": aspect title, *string*
|           "**source**": type: presentation or technical , ``"view"`` *or* ``"data"``
|           "**field**": path to property in JSON terms, *optional string*
|           "**ignored**": if aspect is hidden, *boolean**
|           "**col_groups**": column groups, *optional*
|                ``[`` *list of pairs*
|                   `[` 
|                       **[0]**: column title, *string*
|                       **[1]**: column count, *int*
|                    ``]``, ...
|                ``]``
|           "**attrs**": properties information
|           ``[`` *list* data for attributes
|                ``{`` *dictionary*                
|                      "**name**": property name, *string*
|                      "**title**": title of property, *string*
|                      "**kind**": kinds of attribute, separated by space, *string*
|                      "**is_seq**": if value is sequence, *boolean*
|                      "**tooltip**", tooltip, *optional string*
|                 ``}``, ...
|            ``]``
|        ``}``
|   ``]``
    
Description
-----------

The request returns complete description of schema of :term:`aspects<aspect>` and 
properties available for :term:`dataset` in :term:`viewing regime`.

List of property kinds supported:

   ========== =========
   null
   list
   dict
   empty
   link
   string
   int
   numeric
   ========== =========
   
The request might be used for experimental extensions of the system 
functionality and user interface.
   
