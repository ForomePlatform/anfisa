Dataset Descriptor structure
============================

Format
------

| ``{`` *dictionary*, 
|       "**name**":         dataset name, *string*
|       "**kind**":         dataset kind, *either* ``"ws"`` *or* ``"xl"`` 
|       "**upd-time**:      time of last dataset update, 
|                               *string, time in ISO format*
|       "**note**":         user note to dataset, ``null`` or *string*
|       "**date-note**:     time of last note update, 
|                               ``null`` or *string, time in ISO format*
|       "**total**":        total number of variants, *int*
|       "**doc**":          dataset documentation, :doc:`s_doc_descr` 
|       "**ancestors**":    information on base datasets
|               ``[`` *list of* base datasets, root is the last
|                   ``[`` *list*
|                       [**0**]: name of ancestor dataset, *string*
|                       [**1**]: *optional* dataset documentation, :doc:`s_doc_descr`
|                   ``]``
|               ``]``
|       
|       *in case of* :doc:`dirinfo` *request*:
|       --------------------------------------
|       "**secondary**":  *optional* list of secondary workspaces, 
|                           *list of strings*
|
|       *in case of* :doc:`dsinfo` *request*:
|       -------------------------------------
|       "**metadata**":  metadata of dataset, *JSON structure*
|       "**unit-groups**": group names of filtering properties,
|           ``[`` *list of strings* ``]``

Description
-----------

The descriptor represents information about :term:`dataset`. It is used in 
context of two requests: 

    * :doc:`dirinfo` 
        returns collection of  descriptors 
        of all active datasets in the :term:`vault`. In this context 
        details of connection between datasets are required: dataset 
        can be :term:`secondary<secondary workspace>`, so one needs to 
        know base of it. :term:`Root dataset` is defined always, and 
        for a primary dataset equals to itself.

    * :doc:`dsinfo` 
        returns descriptor for one dataset.
        In this case descriptor contains details about metadata.
    
Descriptor provides reference **doc** to :term:`dataset documentation`, and if 
base dataset exists, reference to documentation for all **ancestors** if they are 
present in the vault.
    
Comment
-------

Important part of metadata is list of versions of sources used in dataset 
annotation. It is located in **metadata** returning property:

|         ``["versions"]: {`` *dictionary*
|                   source name, *string*: source version, *string* 
|                   ...
|               ``}``
    
Used in requests
----------------
:doc:`dirinfo`   

:doc:`dsinfo`

:doc:`s_doc_descr`

:doc:`../concepts/doc_pg`
