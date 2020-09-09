dirinfo
=======
        **Vault information**

Synopsis
--------

.. index:: 
    dirinfo; request

**dirinfo** 

    **Arguments**: *none*

    **Return value**: 

        .. index::
            version; property of dirinfo
            ds-list; property of dirinfo
            ds-dict; property of dirinfo
    
        | ``{`` *dictionary*
        |       "**version**": version of the system, *string*
        |       "**ds-list**": dataset names, *list of strings*
        |       "**ds-dict**": dataset descriptors, *dictionary*
        |             <dataset name> : :doc:`s_ds_descr`
        | ``}``


Description
-----------

The request returns complete information for rendering directory page in User Interface.
So it returns information about all :term:`datasets<dataset>` accessible in :term:`vault`.

Sorting order in **ds-list** output value represents hierarchical connections between datasets.
