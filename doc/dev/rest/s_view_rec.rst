View Record structure
================================

.. index:: 
    View Record; data structure


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
See also :doc:`../concepts/view`

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

Markup details
^^^^^^^^^^^^^^
    
Most part of aspects represent data by ``<table>`` with two columns with title and 
value of property.

    Exceptions are:

    - Some aspects provide multiple value columns:: Quality, VEP Transcripts, 
        Colocated Variants and Cohorts;

        Value columns in aspects VEP Transcripts and Cohorts are grouped, so 
        the table for these aspects has header title row with joined cells and 
        titles of groups, and also contain counters for rows.

    - Aspect VCF represent data by ``<pre>`` in preformatted text form.

Cells in tables are marked by specific CSS classes:

    - title cells (in title column and in title row) are marked by class ``title``

    - value cells with no value are marked by class ``none``

    - other value cells are marked by class ``norm``
    
Aspect VEP Transcripts
^^^^^^^^^^^^^^^^^^^^^^
The aspect visualizes :term:`transcripts<transcript>` data, and transcripts are 
subjects of filtering, so rendering of this aspect actively interacts
with the user interface in  context of :term:`WS-dataset`.

Columns representing filtered (selected) transcripts are highlighted: all cells
in these columns are marked by CSS class ``hit``. (The correspondent header joined 
cell is marked by class ``hit`` too).

All other cells in the table are marked by class ``no-hit``. 

In practice the users often need to hide non hit columns to have more informative
view of hit transcripts ant their data. 

For this purpose the header title cell for column group containing all hit columns 
includes empty tag ``<span id="tr-hit-span">``. 
Contents of this span can be rendered on the Front End
side to provide functionality of hide or show all transcript columns but hit ones. 

In the Front End one can use call ``document.getElementsByClassName("no-hit")`` to 
select all cells that are to hide or to show.

Aspect General
^^^^^^^^^^^^^^
Contents of aspect can be changed as a result of user activity in context of
:term:`WS-dataset`:

    - Rows "Presence in filters" and "Presence in decision trees" contain
        operative information what :term:`filters<filter>` and 
        :term:`decision trees<decision tree>` are positive on the variant in view

    - Row "Transcripts" contain transcript short descriptions, and the variants
        selected by current filter are marked by ``hit`` CSS class.

Aspect Cohorts
^^^^^^^^^^^^^^
The aspect Cohorts is special one and appears only for special datasets with 
cohorts of patients and no exact proband sample.

Usually dataset with cohorts includes very many samples, and it is important to
visualize only necessary cohorts and hide others. 

For this purpose all cells representing a cohort with name ``<cohort name>`` 
are marked by class with name ``cohort_<cohort name>``. 

So the Front End can provide functionality of hide/show cohorts based on selection
of cell elements with a determined CSS class.
    
Used in requests
----------------
:doc:`reccnt`   

:doc:`single_cnt`
