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
|        "**detailed**": *optional* transcript are in counts, ``true``
|
|        *in case of* **kind** = ``"numeric"``
|        ----------------------------------- 
|        "**min**": *optional* minimum value, *int or float*
|        "**max**": *optional* maximum value, *int or float*
|        "**counts**": *optional* 
|               ``[`` *list*
|                       **[0]**: count of transcripts (if detailed) or variants, *int*
|                       **[1]**: *optional* count of variants (if detailed), *int*
|               ``]``
|
|        *in case of* **kind** = ``"enum"`` 
|        ----------------------------------- 
|        "**variants**":  *optional* ``[`` values status *list*  
|               ``[`` *list*
|                       **[0]**: value, *string*
|                       **[1]**: count of transcripts (if detailed) or variants, *int*
|                       **[2]**: *optional* count of variants (if detailed), *int*
|               ``]``, ...  ``]``
|
|        *in case of* **kind** = ``"func"`` 
|        ----------------------------------- 
|        "**variants**":  ``null``*optional* ``[`` values status *list*  
|               ``[`` *list*
|                       **[0]**: value, *string*
|                       **[1]**: count of transcripts (if detailed) or variants, *int*
|                       **[2]**: *optional* count of variants (if detailed), *int*
|               ``]``, ... ``]``
|        "**err**": *optional*, error message, *string*
|        "**rq-id**:  ID of request series
|        "**no**": *optional* position on tree, *int as string* 
|         **...**: function environment
| ``}``

Description
-----------

The data structure is used in return values of requests :doc:`ds_stat`, :doc:`dtree_stat`, :doc:`statunits` and :doc:`statfunc`. It represents status report for a :term:`filtering property` applied to selected set of variants. In case of :term:`workspace` selection also applies to :term:`transcripts<transcript>`. 

See discussion on :doc:`../concepts/status_report` for understanding general principle and details.

In context of requests :doc:`ds_stat`, :doc:`dtree_stat` status report can be incomplete. In this case the property **incomplete** is set and details of status (**min**/**max**/**count** for numeric properties and **variants** for enum ones) do not present in structure. 

In complete state details of status are always set. If status reports for filtering properties (of numeric or enum type) is incomplete, use request :doc:`statunits` to get them in complete state. 

In **detailed** case (:term:`workspace` context) the main items for counting are :term:`transcripts<transcript>`, so count values form pair of values in list, first one is for transcripts, second for :term:`variants<variant>`.
Otherwise only single variant count is provided in lists. 

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

Functions support
^^^^^^^^^^^^^^^^^
For functions property status structure is formed in two different contexts:

- requests :doc:`ds_stat`, :doc:`dtree_stat` just declare placement of function between filtering properties, so requests return structure with ``null`` as **variants** and additional properties of function environment
    
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
