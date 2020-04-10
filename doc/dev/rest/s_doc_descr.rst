Dataset document descriptor
===========================

.. index:: 
    Dataset document descriptor; data structure

Format
------

* Document descriptor:

    |   ``[``
    |       **[0]**: document name
    |       **[1]**: URL to document, **string**
    |   ``]``

* Folder descriptor:

    |   ``[``
    |       **[0]**: folder name name
    |       **[1]**: ``[`` * list of* document or folder descriptors ``]``
    |   ``]``

Description
-----------

Lists of document descriptor are properties **doc** and **base-doc** of
:doc:`s_ds_descr` that is returning property of request :doc:`dsinfo`

Descriptors represent recursive structure of documents provided with :term:`dataset`.

In context of JS distinction between two types of descriptors can be made by
check of ``Array.isArray(doc_entry[1])``.

URL of document hs relative form to the top URL of the system

See also
--------
:doc:`dsinfo`

:doc:`s_ds_descr`
