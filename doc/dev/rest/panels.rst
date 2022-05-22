panels
=======
        **Panels information and manipulation**
        
.. index:: 
    panels; request

Synopsis
--------
**panels** 

    **Arguments**: 

        **ds**: dataset name
        
        **tp**: symbol type (only ``Symbol`` is supported currently)

        **instr**: *optional modifier* 
        
    |       ``[``
    |           **[0]**: option, ``"UPDATE"`` *or* ``"DELETE"``
    |           **[1]**: filter name, *string*
    |           **[2]**: symbol list, *optional list of strings*
    |       ``]`` *in JSON string representation*
        
    **Return value**: 
    
    | ``{`` *dictionary*
    |       "**type**": *string*, input symbol type
    |       "**panels**": *list of strings*, available panel names
    |       "**panel-sol-version**": :ref:`indicator of state<sol_version_indicators>` for panels
    |       "**db-version**": *list of strings*, string descriptor for versions of sources for symbol database
    |  ``}``
    
Description
-----------
The main purpose of the request is to report content of :ref:`symbol panels<panels_as_sol_items>`. 

The value of **panel-sol-version** indicator is useful especially in this request: it indicates when panel list is changed.

Also it reports versions of sources used to build gene symbols database, in **db-version**.

See also
--------
:doc:`../concepts/sol_work`  

:doc:`symbol_info`

