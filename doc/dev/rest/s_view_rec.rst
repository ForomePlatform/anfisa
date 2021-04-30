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
|           ``[`` *list* of column groups, to represent heading row if the table
|               ``[`` 
|                       **[0]**: title (html-escaped), *string*
|                       **[1]**: count, *int*
|                ``]``, ...
|            ``]``
|       **colgroup**: ``null`` or *optional*
|           ``[`` *list* of class names of columns, *strings* ``]``

|       "**rows**":    *empty* or
|            ``[`` *list* of attribute descriptors, to represent main content of the table
|               ``{``
|                    "**name**": attribute name (technical), *string*
|                    "**title**": attribute title
|                    "**cells**": 
|                      ``[``  *list* of cell descriptors  
|                           ``[``
|                               **[0]**: content (html-escaped), *string*
|                               **[1]**: cell render class name, *string*
|                           ``]``
|                      ``]``, ...
|                    "**tooltip**": tooltip, **string** or ``undefined``
|                    "**render**": render mode, **string** or ``undefined``
|                ``]``, ...
|            ``]``
|       "**parcontrol**":  to represent control <div> before the table, 
|                               **string** or ``undefined``
|       "**parmodes**": technical json information on parcontrol modes, 
|                               **list of JSON objects** or ``undefined``
|        
|       *in case of* ``type="pre"``:
|       ---------------------------------
|       "**content**":  pre-formatted content (VCF record), *string*
|   ``}``, ...
| ``]``


Description
-----------
The data structure represents complete information sufficient for render full presentation of a variant in :term:`Viewing regime`. See also :doc:`../concepts/view`

Full information is split onto series of :term:`aspects<aspect>`. Aspect usually has form of table. In simple cases table contains two columns, for title and contents of properties. One special aspect represents raw data in VCF format, so has form of pre-formatted text.

It is supposed that technical aspects (kind="tech") contain information in more raw form and are useful for deep studies. 

Table aspect information is prepared for rendering tables in HTML. Information is split onto rows with fixed length. Left column is control one and contains property titles. Minimal column count is 1, it means one column for titles and one for values.

For complex aspect tables column structure can contain groups of columns with common title.

Row can have tooltip.

Markup details
--------------

* Aspect VCF represents data in pre-formatted text form with use of <pre> tag.

* Most part of aspects represent data by ``<table>`` with two columns with title and value of property. Only **columns** and **rows** in aspect descriptor properties are sufficient to support this kind of aspects. 

* Some aspect (currently VEP Transcripts, Quality,Colocated Variants and Cohorts) represent data in a multi-column form, so the following additional properties are supported (see more details about concrete aspects below):

    - **colhead** is used when columns are logically grouped; the property represents header row with joined cells, each cell corresponds to a group of columns. Content of cell consists of title of group, column counter and possibly additional blocks (<span>) for UI controls placement
    
    - **parcontrol** is used when control information can not be put inside the table, the property  represents a block of document (<div>) above the table and containing blocks for UI controls placement

    - **colgroup** represents <colgroup> tag of the table; it is used when there is need in multiple regimes of columns collapse for the user needs (contemporary browsers do not support collapse of whole columns properly, however <colgroup> tag is the proper place to report information on column base)
    
    
Cells in tables are marked by specific CSS classes:

- title cells (in title column and in title row) are marked by class ``title``

- value cells with no value are marked by class ``none``

- other value cells are marked by class ``norm``

- in case of logically selected column the class ``hit`` is added to all cells in the column

.. _dynamic_aspects_features:

Dynamic features in aspects
---------------------------

The following is explication of date rendering features that depend on current state of the user session.
    
Aspect General
^^^^^^^^^^^^^^
Contents of aspect can be changed as a result of user activity :

- In in context of :term:`WS-dataset`:

    - Rows "Presence in filters" and "Presence in decision trees" contain
        operative information what :term:`filters<filter>` and 
        :term:`decision trees<decision tree>` are positive on the variant in view

    - Row "Transcripts" contain transcript short descriptions, and the variants
        selected by current filter are marked by ``hit`` CSS class.

- Row "Has_Variant" reports list of samples containing current variant. If some samples are active in context of current filter or decision tree condition, presence of these samples is highlighted and grouped on top of report list. 

Aspect VEP Transcripts
^^^^^^^^^^^^^^^^^^^^^^
The aspect visualizes :term:`transcripts<transcript>` data, and transcripts are subjects of filtering, so rendering of this aspect actively interacts with the user interface in  context of :term:`WS-dataset`.

Transcript columns are grouped, so **colhead** property is used in the aspect descriptor. Only transcripts of the first group can be selected in context of :term:`WS-dataset`.

In practice the users often need to hide unselected (non hit) columns to have more informative
view of the selected (hit) transcripts and their data. 

So all cells in hit columns are marked with CSS class ``hit``, and all others with class ``no-hit``.

Header cell for the group contains title and column counter as well as empty ``<span id="tr-hit-span">``. So the Front End application can fill this span with controls to provide functionality of collapse/expansion of columns in the table. 

Aspect Cohorts
^^^^^^^^^^^^^^

The aspect Cohorts is special one and appears only for special datasets with 
cohorts of patients and no exact proband sample. The appearance of cohorts in dataset affects behavior of Quality aspect.

Aspect Quality
^^^^^^^^^^^^^^

The aspect Quality possess samples as column objects, so there can be two variants of dynamical behavior actual for the user:

- If some samples are  :ref:`active<active_samples>` in context of current filter or decision tree condition, these samples are highlighted; if there are more than 3 samples in case, the user should have possibility to collapse unselected columns.

- If cohorts present in the dataset, the user should have possibility to collapse/open samples from each cohort in a separated way.

To support this functionality the following features are used in aspect descriptor, so Front End application can fill these spans with controls to perform dynamical behavior of collapse/restore unnecessary columns by up to two ways:

* Property **parcontrol** is used: 

    - in case of presence current samples selection (and more than 3 samples in case) it contains ``<span id="act-samples-ctrl">`` with counter of samples as initial contents
    
    - in case of cohorts presence, it contains empty ``<span id="cohorts-ctrl">``
    
* Property **colgroup** is used to mark columns by CCS classes: ``no-hit`` for inactiv samples  and ``cohort-<cohort name>`` for marking samples from different cohorts.

    
Used in requests
----------------
:doc:`reccnt`   

:doc:`single_cnt`
