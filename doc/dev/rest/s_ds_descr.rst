Dataset Descriptor structure
============================

.. index:: 
    Dataset descriptor structure; data structure

Format
------

| ``{`` *dictionary*, 
|       "**name**":             dataset name, *string*
|       "**kind**":             dataset kind, *either* ``"ws"`` *or* ``"xl"`` 
|       "**create-time**:       time of dataset installation,
|                                  *string, time time in ISO format*
|       "**upd-time**:          time of last dataset configuration update, 
|                                   ``null`` or *string, time in ISO format*
|       "**note**":             user note to dataset, ``null`` or *string*
|       "**date-note**:         time of last note update, 
|                                   ``null`` or *string, time in ISO format*
|       "**total**":            total number of variants, *int*
|       "**doc**":              dataset documentation, :doc:`s_doc_descr` 
|       "**ancestors**":        information on base datasets
|               ``[`` *list of* base datasets, root is the last
|                   ``[`` *list*
|                       [**0**]: name of ancestor dataset, *string*
|                       [**1**]: *optional* dataset documentation, :doc:`s_doc_descr`
|                       [**2**]: *optional* time of dataset installation, *string, time time in ISO format*
|                   ``]``, ...
|               ``]``
|       
|       *in case of* :doc:`dirinfo` *request*:
|       --------------------------------------
|       "**secondary**":  *optional* list of secondary workspaces, 
|                           *list of strings*
|
|       *in case of* :doc:`dsinfo` *request*:
|       -------------------------------------
|       "**meta**":     metadata of dataset, *JSON structure*
|       "**unit-classes**":  descriptor of :ref:`properties classification<properties_classification>`
|               ``[`` *list* of facet classifications
|                   ``{``
|                       **title**: title of facet classification, *string*
|                       **values**: titles of values, *list of strings*
|                   ``}``, ...
|               ``]``
|       "**unit-groups**": group names of filtering properties,
|           ``[`` *list of strings* ``]``
|       "**cohorts**": *optional* list of cohort names 
|           ``[`` *list of strings* ``]``
|       "**export-max-count**:  maximum record count available for 
|                       export operations (:doc:`csv_export`, :doc:`export`), *int*
|       "**receipts**: *optional* list of specifications for dataset derivations
|           ``[`` *dictionary*
|               "**kind**": kind of derivation: ``"filter"`` or ``"dtree"``, *string*
|               "**eval-update-info**: *list*
|                    [**0**]: creation time, *string in ISO format*
|                    [**1**]: base dataset name, *string*
|               "**panels-supply**: dynamic panels used in receipt *optional dictionary*
|                    ``{``
|                       panel kind: *list of strings*
|                    ``}``   
|                   *for kind* ``filter``:
|               "**f-presentation**": *list of strings**
|                           list of filter criteria in form of Python code 
|               "**filter-name**": *optional* name of filter, if filter is named
|                   *for kind* ``dtree``:
|               "**p-presentation**: *list* of point presentations
|                    [**0**]: presentation in form of Python code with HTML markup, *string*
|                    [**1**]: count of variants selected, *optional int*
|                    [**2**]: mode of selection, *optional boolean*
|               "**dtree-name**": *optional* name of decision tree, if tree is named
|           ``]``


Description
-----------

The descriptor represents information about :term:`dataset`. It is used in context of two requests: 

* :doc:`dirinfo` 
    returns collection of  descriptors of all active datasets in the :term:`vault`. In this context details of connection between datasets are required: dataset can be :term:`secondary<secondary workspace>`, so one needs to know base of it. :term:`Root dataset` is defined always, and for a :term:`primary dataset` equals to itself.

* :doc:`dsinfo` 
    returns descriptor for one dataset.
    In this case descriptor contains details about metadata.

Descriptor provides reference **doc** to :term:`dataset documentation`, and if base dataset exists, reference to documentation for all **ancestors** if they are present in the vault.
    
Comment
-------
Important part of metadata is list of versions of sources used in dataset annotation. It is located in **meta** returning property:

|         ``["versions"]: {`` *dictionary*
|                   source name, *string*: source version, *string* 
|                   ...
|               ``}``
    
Property **receipts** is actual for derived datasets and contains complete information how the dataset was derived, i.e. produced from root dataset. Information is given in human readable form for render purposes. Receipts are sorted in stack order: the first receipt in array corresponds to the latest derivation filtration.
    
Receipts might use :doc:`panels<../concepts/variety>` as dynamical :doc:`solutions<../concepts/sol_work>`, so the internal property **panels-supply** fixes actual state of used panels at moment of derivation.
    
Used in requests
----------------
:doc:`dirinfo`   

:doc:`dsinfo`

:doc:`s_doc_descr`

:doc:`../concepts/doc_pg`

:doc:`../concepts/prop_ux`
