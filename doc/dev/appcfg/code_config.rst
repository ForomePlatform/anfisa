Code configuration layer overview
=================================

.. index:: 
    Code configuration layer overview

The code of the system back end can be logically split onto two parts:

    * system kernel, supports functionality of the system in universal 
        informational context (as more universal as possible)
    
    * configuration layer, serves to adopt application data to 
        universal context

During process of developing of the system configuration tools become to be more separated the kernel, and more expandable and powerful. So we need a special layer of documentation on it. Up to the current stage of development of the system, there is no a simple way for the user to re-configure the system features directly, however this documentation layer might help users to formulate their requirements in proper terms.

*Note*: for purposes to describe parts of API we use source files where this part of API is used in the source of the system. So please consider these files as examples of API application, or as subject of modifications. This way of code reference is not traditional but most acceptable for our purposes in this context.

The code of configuration layer is located in repository of the system in directory ``app/config`` and concerns the following aspects of the system functionality:

* :term:`Solution items<solution item>`: predefinition of various data structures the help the user to exploit data in the system
    
        ``app/config/solution.py``

    Some parts of solution item configuration are applied in the followind procedure.
        
* Configuration of datasets used on stage of dataset creation
    
    There is a complex procedure running on stage of dataset creation. It analyzes input :term:`annotated JSON file`, stores information (with some changes) from it to internal data formats and so prepares data for use in system, for both :term:`viewing<viewing regime>` and :term:`filtration` purposes. (See details of format here: :doc:`ajson`)
            
    Once this procedure is applied to creating dataset, the content of dataset stands persistent, and only re-creation of dataset can change this content.
    
    So there are numerous of aspects to configure:
    
    * Configuration static for :term:`viewing regime` 
        
        * static part:  ``app/config/view_schema.py``
            :doc:`view_schema_py`
    
        * dynamic part: ``app/config/view_tune.py``
            :doc:`view_tune_py`
        
    * Configuration data for :term:`filtration regimes<Filtration>`
    
        * static part: ``app/config/flt_schema.py``
            :doc:`flt_schema_py`

        * dynamic part: ``app/config/flt_tune.py``
            :doc:`flt_tune_py`

See also
--------

:doc:`ajson`

:doc:`../adm/admin`
