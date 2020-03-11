View Record structure
================================

Format
------

| ``[`` *list* of aspect descriptors
|   ``{`` *dictionary*, 
|       *aspect descriptor common properties*:
|       --------------------------------------
|       "**name**":     aspect name, *string*
|       "**title**:     title, *string*
|       "**kind**":     kind, *either* ``"norm"`` *or* ``"tech"`` 
|       "**type**":     type, *either* ``"table"`` *or* ``"pre"``
|
|       *in case of* ``type="table"``:
|       ---------------------------------
|       "**columns**":  column count, *int*
|       "**colhead**":  ``null`` or 
|           ``[`` *list* of column groups
|               ``[`` 
|                       **[0]**: title (html-escaped), *string*
|                       **[1]**: count, *int*
|                ``]``, ...
|            ``]``
|       "**rows**":    *empty* or
|            ``[`` *list* of attribute descriptors
|               ``[``
|                    **[0]**: attribute name (out of use), *string*
|                    **[1]**: attribute title
|                    **[2]**: 
|                      ``[``  *list* of cell descriptors  
|                           ``[``
|                               **[0]**: content (html-escaped), *string*
|                               **[1]**: cell render class name, *string*
|                           ``]``
|                      ``]``, ...
|                    **[3]**: (if present) tooltip. **string** or ``undefined```
|                ``]``, ...
|            ``]``
|        
|       *in case of* ``type="table"``:
|       ---------------------------------
|       "**content**":  pre-formatted content (VCF record), *string*
|   ``}``, ...
| ``]``


Description
-----------

The data structure represents complete information sufficient for render
full presentation of a variant in :term:`Viewing regime`. 
See also :ref:`Variant data presentations<variant_data_presentation>`

Full information is split onto series of :term:`aspects<aspect>`. 
Aspect usually has form of table. In simple cases table contains two columns, 
for title and contents of properties. One special aspect represents 
raw data in VCF format, so has form of preformatted text.

It is supposed that technical aspects (kind="tech") contain information 
in more raw form and are useful for deep studies. 

Table aspect information is prepared for rendering tables in HTML. Information 
is split onto rows with fixed length. Left column is control one and contains property titles. 
Minimal column count is 1, it means one column for titles and one for values.

For complex aspect tables column structure can contain groups of columns with common title.

Row can have tooltip.
    
Used in requests
----------------
:doc:`reccnt`   :doc:`single_cnt`
