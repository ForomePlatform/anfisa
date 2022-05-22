symbols
=======
        **Symbol selection**
        
.. index:: 
    symbols; request

Synopsis
--------
**symbols** 

    **Arguments**: 

        **ds**: dataset name
        
        **tp**: symbol type (only ``Symbol`` is supported currently)

        **list**: *optional* list of symbols
            *in JSON string representation*

        **panel**: *optional* name of applying panel
        
        **pattern**: *optional* applying name pattern

    **Return value**: 

    |  ``null`` (if panel name is improper)
    |  *or*
    | ``{`` *dictionary*
    |    "**panel**":  *optional string* input panel name, in panel mode
    |    "**panel-sol-version**": :ref:`indicator of state<sol_version_indicators>` for panels, in panel mode
    |
    |    "**panel**":  *optional string* input name pattern, in pattern mode
    |
    |    "**type**": *string*, input symbol type
    |    "**all**": *list of strings*, list of all filtered symbols
    |    "**in-ds**": *list of strings*, list of symbols actual for the dataset
    | ``}``
    
Description
-----------
The request is the single proper way to select symbols for varieties (only ``Symbol`` variety for gene symbols is supported currently). There are three modes to select symbol: by direct list of symbols, by panel name and by name pattern. The request filters known symbols (so list mode is meaningful also), and  reports in **in-ds** if these symbols are actual for the dataset. 

Argument **pattern** is expected as sequence of letters (alpha), digits and ``'*```, "star" symbol, which means any sequence of symbols. Pattern should be meaningful enough: not less than 3 symbols length, and not less than 2 alpha-numeric symbols inside. 

See also
--------
:doc:`../concepts/sol_work`
