dirinfo
=======
        **Vault information**
        
.. index:: 
    dirinfo; request
    
Synopsis
--------
**dirinfo** 

    **Arguments**: *none*

    **Return value**: 
        .. index::
            version; property of dirinfo
            ds-list; property of dirinfo
            ds-dict; property of dirinfo
    
        | ``{`` *dictionary*
        |       "**version**": version of the system, *string*
        |       "**build-hash**": hash of the system build, *string*
        |       "**ds-list**": dataset names, *list of strings*
        |       "**ds-dict**": dataset descriptors, *dictionary*
        |             <dataset name> : *optional* :doc:`s_ds_descr`
        |       "**documentation**": ``[`` *list of* documentation sets
        |                    ``{`` *dict*
        |                         "**id**":    identifier of set, *string*
        |                         "**title**": title of set, *string*
        |                         "**id**": URL to top of set, *string*
        |                    ``}``, ...  
        |               ``]``
        | ``}``


Description
-----------
The request returns complete information for rendering directory page in User Interface. So it returns information about all :term:`datasets<dataset>` accessible in :term:`vault`.

Sorting order in **ds-list** output value represents hierarchical connections between datasets.

Details of **documentation** properties see description of :ref:`sphinx-doc-sets<sphinx-doc-sets>` option in service configuration.

.. _ReservedDSNames:

The dictionary **ds-dict** contains all names of datasets as well as all names reserved by the system. Name is reserved if it presents in the dictionary but its value is null. Do not try to use such names as a name of new dataset: the action will be blocked.
