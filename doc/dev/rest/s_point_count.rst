Decision Tree Point Count descriptor
====================================

.. index:: 
    Decision Tree Point Count descriptor; data structure

Format
------

|   *either*
|   `   `[`` *list**
|           **[0]** count of variants, *int*
|           **[1]** *optional* count of transcripts, *int*
|       ``]``
|   *or*
|       ``0`` - point not applicable
|   *or*
|       ``null`` - status incomplete

Description
-----------

The data represents information for counts of :term:`variants<variant>`, and in case of
:term:`ws-dataset` of :term:`transcripts<transcript>` also.
        
If point is not applicable for counting, data is  ``0``.

If evaluation of counts is incomplete, data is ``null``.


Used in requests
----------------
:doc:`dtree_set`    :doc:`dtree_counts`
