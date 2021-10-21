Dataset document descriptor
===========================

.. index:: 
    Dataset document descriptor; data structure

Format
------
* Document descriptor:

    |   ``[``
    |       **[0]**: document name
    |       **[1]**: path to document, **string**
    |       **[2]**: *optional* content information, **dictionary**    
    |   ``]``

* Folder descriptor:

    |   ``[``
    |       **[0]**: *optional* folder name
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

Content information in document desciptor is available only if document was automatically created on dataset setup, and actually it is just a wrapper around image or images. So the Front-End application can reformat it in an appropriate way. The following cases are currently supported:

    |   ``{``
    |       **type**: "img"
    |       **image**: image URL, **string**
    |       **tooltip**: *optional* image tooltip, **string** 
    |   ``}``
    
    |   ``{``
    |       **type**: "seq_img"
    |       **images**: image URLs, **list of strings**
    |       **names**: *optional* short names of images, **list of string** 
    |   ``}``
 
    
See also
--------
:doc:`s_ds_descr`

:doc:`dsinfo`

:doc:`dirinfo`

:doc:`../concepts/doc_pg`
