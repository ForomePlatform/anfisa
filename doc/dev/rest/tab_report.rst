tab_report
==========
        **Viewing data in tabulated form**

.. index:: 
    tab_report; request

Synopsis
--------

**tab_report** 

    **Arguments**: 

        **ds**: dataset name
        
        **seq**: list of record order numbers *in JSON string representation*
    
        .. index:: 
            seq; argument of tab_report

        **schema**: name of data schema

        .. index:: 
            schema; argument of tab_report        
        
    **Return value**: *list of dictionaries*

Description
-----------
The request prepares view presentation for series of :term:`variant` records in form defined by schema.

See also :doc:`../concepts/view_pre`

In current version of the system schemes are defined in source code of the server, so the list of it is fixed.

.. warning:: TODO: add list and descriptions of available schemes

See also
--------
:doc:`../concepts/view_pre`

:doc:`../concepts/view`
