Dataset document descriptor
===========================

.. index:: 
    Dataset document descriptor; data structure

Format
------
* Document descriptor:

    |   ``[``
    |       **[0]**: document name
    |       **[1]**: *path to document, **string**
    |   ``]``

* Folder descriptor:

    |   ``[``
    |       **[0]**: *optional* folder name name
    |       **[1]**: ``[`` * list of* document or folder descriptors ``]``
    |   ``]``

Description
-----------
Document descriptor describes additional documents associated with :term:`dataset`.

Document descriptors are used inside :doc:`s_doc_descr` in two forms: as property **doc** and inside list property **ancestors**

:doc:`s_doc_descr` are used as returning properties of requests :doc:`dsinfo` and :doc:`dirinfo`.

Descriptors represent recursive structure of documents.

In context of JS distinction between two types of descriptors can be made by check of ``Array.isArray(doc_entry[1])``.

Name of folder is null only for top level folder of dataset documentation.

For dataset with name ``<ds name>`` the system provides access to documents by URL of the following form:

    ``<URL to application back end>/dsdoc/<ds name>/<path to document>``

See also
--------
:doc:`s_ds_descr`

:doc:`dsinfo`

:doc:`dirinfo`

:doc:`../concepts/doc_pg`
