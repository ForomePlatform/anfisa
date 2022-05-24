Property Status structure
=========================

.. index:: 
    Property Status; data structure

Format
------

| ``{`` *dictionary*, 
|        "**name**": property name, *string*
|        "**kind**": property kind, ``"numeric"``, ``"enum"`` *or* ``"func"``
|        "**vgroup**": group of property, *string*
|        "**title**": *optional* title, *string*
|        "**sub-kind**": *optional* sub-kind, *string*
|        "**render-mode**": *optional*
|               comma-separated render options, *string* 
|        "**tooltip**": *optional* tooltip, *string*
|        "**incomplete**": *optional* status is incomplete, ``true``
|        "**detailed**": *optional* transcript data is in counts, ``true``
|        "**classes**: facet classification of the property, 
|           ``[`` *list* of facet descriptors
|               ``[`` indexes of items in facet classification list 
|                       (usually with one element) *list of integers*
|               ``]``, ...
|           ``]``
|
|        *in case of* **kind** = ``"numeric"``
|        ----------------------------------- 
|        "**min**": *optional* minimum value, *int or float*
|        "**max**": *optional* maximum value, *int or float*
|        "**counts**": *optional* 
|               ``[`` *list*
|                       **[0]**: count of variants (transcipt if detailed, DNA otherwise), *int*
|                       **[1]**: *optional* (if detailed) count of DNA variants, *int*
|                       **[2]**: *optional* (if detailed) count of transcripts, *int*
|               ``]``
|        "**histogram**: *optional*, :doc:`s_histogram`
|
|        *in case of* **kind** = ``"enum"`` 
|        ----------------------------------- 
|        "**variants**":  *optional* ``[`` values status *list*  
|               ``[`` *list*
|                       **[0]**: value, *string*
|                       **[1]**: count of variants (transcipt if detailed, DNA otherwise), *int*
|                       **[2]**: *optional* (if detailed) count of DNA variants, *int*
|                       **[3]**: *optional* (if detailed) count of transcripts, *int*
|               ``]``, ...  ``]``
|
|           *additional fields for variety property*
|            -------------------------------------- 
|           "**panel-name**": *string* name of dual panel unit
|           "**panels**":     
|                   ``[`` *list of variants* for panel unit ``]``
|           "**split-info**": 
|                   ``[`` 
|                           *list of descriptors* of blocks of variants, see below
|                   ``]``
|           "**rest-count**": *optional int*, count of rest hidden present property variants
|
|           *additional fields for variety property*
|            -------------------------------------- 
|           "**variety-name**": *string* name of dual variety unit
|           "**panel-sol-version**": :ref:`indicator of state<sol_version_indicators>` for panels
|
|        *in case of* **kind** = ``"func"`` 
|        ----------------------------------- 
|        "**variants**":  ``null``*optional* ``[`` values status *list*  
|               ``[`` *list*
|                       **[0]**: value, *string*
|                       **[1]**: count of variants (transcipt if detailed, DNA otherwise), *int*
|                       **[2]**: *optional* (if detailed) count of DNA variants, *int*
|                       **[3]**: *optional* (if detailed) count of transcripts, *int*
|               ``]``, ... ``]``
|        "**err**": *optional*, error message, *string*
|        "**rq-id**:  ID of request series
|        "**no**": *optional* position on tree, *int as string* 
|         **...**: function environment
| ``}``

Description
-----------

The data structure is used in return values of requests :doc:`ds_stat`, :doc:`dtree_stat`, :doc:`statunits` and :doc:`statfunc`. It represents status report for a :term:`filtering property` applied to selected set of variants. In case of :term:`workspace` selection also applies to :term:`transcript variants<transcript variant>`. 

See discussion in :doc:`../concepts/status_report` for understanding general principle and details.

See discussion in :doc:`../concepts/prop_ux` for understanding UX settings for filtering properties. 

In context of requests :doc:`ds_stat`, :doc:`dtree_stat` status report can be incomplete. In this case the property **incomplete** is set and details of status (**min**/**max**/**count** for numeric properties and **variants** for enum ones) do not present in structure. 

In complete state details of status are always set. If status reports for filtering properties (of numeric or enum type) is incomplete, use request :doc:`statunits` to get them in complete state. 

In **detailed** case (:term:`workspace` context) the main items for counting are :term:`transcript variants<transcript variant>`, so count values form triplet of values in list, first one is for transcript variants, second for :term:`DNA ones<DNA variant>`, and last for :term:`transcripts<transcript>`.
Otherwise only single DNA variant count is provided in lists. 

The field **classes** provides property classification information, see :doc:`../concepts/restrict_flt`.

Property **sub-kind** can have the following values (transcipt-based subkinds are provided only in :term:`workspace` context):

  ================   ====================
   **kind**           **sub-kind**
  ================   ====================
   ``"numeric"``      ``"int"`` 
   
                      ``"float"``
                      
                      ``"transcript-int"`` 
                      
                      ``"transcript-float"``
  ----------------   --------------------
    ``enum``          ``"status"`` 
                      
                      ``"multi"``

                      ``"transcript-status"`` 
                      
                      ``"transcript-multi"``
  ----------------   --------------------
    ``func``          *type of function*
  ================   ====================
  
Variants for enumerated properties
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
Complete status report for enumerated filtering properties contains counters for all value variants registered in dataset. So in generic case report contains multiple entries with zero counts. 

On stage of rendering status report it is reasonable to hide entries with zero counts. Really, there is no need for user to see values that do not present in selection. So in "normal" case they are to be hidden.

But: rendering of status report can be done in context of existing condition, and that condition might refer variants with zero count in current selection. In this case zero count variants should be visible and actual of them should be checked. 

Moreover: some variants referred in condition might not be registered in this concrete dataset, and the user does not need to care of that fact. So these variants should be added to list of variants *on the client side* (with zero counts).

And yet one problem: some variant lists have uncontrolled size. For example, it happens with property ``Symbol`` in almost any XL-dataset: indeed, tens of thousands known genes can appear in this list! In context of workspace, with no more than 9000 variants, this list is not more than some thousands, it is comparatively good. But even in this case: the user has problems in selection of interested variant in so huge lists. 

It is really heavy problem for the current version of the system. In future release there should appear an effective and (probably) complex solution of this problem.

Variety/panel properties
^^^^^^^^^^^^^^^^^^^^^^^^
Variety and panel properties are enumerated properties with specific behavior discussed :doc:`here<../concepts/variety>`:

    - **variants** for panel property status structure is always empty, real content of this list contains in dual variety property status structure in the field **panels**
    
    - **variants** for variety property status structure is joined list of blocks, and **split-info** list describes these blocks in format ``[`` *string* block type, *int* count of variants in block ``]``. Block is present only if it is not empty, it contains sorted list of symbols, and there can be up to two blocks in any case:
    
        - block of type ``"active"`` represents full statistic for :term:`active symbols`, it is the first block, if presents
        
        - block of type ``"rest"`` represents statistic for all symbol with non-zero statistic that are not active, only if the length of this block is small enough (300 items tn the current version)
        
        - block of type ``"used"`` represents full statistic for non-active symbol used in applied filter or decision tree, if such symbols exist and if ``"rest"`` block is absent (i.e. list of rest is too large)
        
        - **rest-count** presents in response only if ``"rest"`` block is absent

.. _functions_support:
        
Functions support
^^^^^^^^^^^^^^^^^
For functions property status structure is formed in two different contexts:

- requests :doc:`ds_stat`, :doc:`dtree_stat` just declare placeholders of function in **functions** list, so requests return structure with ``null`` as **variants** and additional properties of function environment
    
- request :doc:`statfunc` returns property status with non-optional **variants** or **err** in case of error in evaluation; 
    
    the client can send multiple requests of such kind in short period of time, so for purposes of request identification the property status in this case contains also:
    
    - functional environment: values of all arguments, 
    
    - value **rq_id** (and **no** in context of decision tree)

See :doc:`func_ref` for details and function reference.

See also
--------
:doc:`ds_stat` 

:doc:`dtree_stat` 

:doc:`statunits` 

:doc:`statfunc`

:doc:`../concepts/prop_ux`

:doc:`../concepts/restrict_flt`

:doc:`../concepts/variety`
