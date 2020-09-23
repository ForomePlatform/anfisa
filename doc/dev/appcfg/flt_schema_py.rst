Configuration of filtration schema API
======================================

.. index:: 
    Configuration of filtration schema API
    
This is description of part of API of code configuration layer dealing with configuration of data of :term:`filtration` mechanism, see :doc:`../concepts/filtration` for details. Here we explain application of this API in the source file

``app/config/flt_schema.py``
    
::

    def defineFilterSchema(metadata_record):
        ...

    class FilterPrepareSetH(...):
        def __init__(self, metadata_record,  modes = None, ...)
            ...
        @classmethod
        def regNamedFunction(cls, name, func):
            ...
        def regPreTransform(self, transform_f):
            ...
        def viewGroup(self, view_group_title):
            ...
            
        def intValueUnit(self, name, vpath, title = None,
                default_value = None, diap = None,
                conversion = None, render_mode = None, tooltip = None):
            ...
        def floatValueUnit(self, name, vpath, title = None,
                default_value = None, diap = None,
                conversion = None, render_mode = None, tooltip = None):
            ...
        def statusUnit(self, name, vpath, title = None,
                variants = None, default_value = "False",
                accept_other_values = False, value_map = None,
                conversion = None, render_mode = None, tooltip = None):
            ...
        def multiStatusUnit(self, name, vpath, title = None,
                variants = None, default_value = None,
                compact_mode = False,
                accept_other_values = False, value_map = None,
                render_mode = None, tooltip = None, conversion = None):
            ...
        def presenceUnit(self, name, var_info_seq, title = None,
                render_mode = None, tooltip = None):
            ...
        def panelsUnit(self, name, unit_base, panel_type, title = None,
                render_mode = None, tooltip = None, view_path = None):
            ...
        def transcriptIntValueUnit(self, name, trans_name, title = None,
                default_value = None, render_mode = None, tooltip = None):
            ...
        def transcriptFloatValueUnit(self, name, trans_name, title = None,
                default_value = None, render_mode = None, tooltip = None):
            ...
        def transcriptStatusUnit(self, name, trans_name, title = None,
                variants = None, default_value = "False",
                render_mode = None, tooltip = None, bool_check_value = None):
            ...
        def transcriptMultisetUnit(self, name, trans_name, title = None,
                variants = None, default_value = None,
                render_mode = None, tooltip = None):
            ...
        def transcriptPanelsUnit(self, name, unit_base, panel_type,
                title = None, view_name = None,
                render_mode = None, tooltip = None):
            ...

The filtration schema is configured in ``defineFilterSchema()`` function as instance of ``FilterPrepareSetH`` class.

class FilterPrepareSetH
-----------------------
        
The whole information required for :term:`filtration` mechanism is collected in an instance of class FilterPrepareSetH, and :ref:`metadata<metadata_fields>` is the base information for creation of this instance. 

Preparation set logic uses :doc:`solution pack<solution_py>` and applies solution items from it according to detected :ref:`modes<dataset_modes>` applicable for dataset being preparing for creation.

* **regNamedFunction()** is static method that allows to define a named function to use it in :doc:`list_conv`.

.. _flt_pre_tranform:

* **regPreTransform()** method registers application layer callback to :ref:`modify<ajson_modifications>` annotated JSON record on stage of dataset creation

* **viewGroup()** defines new group of units in filter :term:`unit` collection

All :term:`units<unit>` in the filtration schema are grouped in blocks with names. It is just subject of visual presentation, there is no internal logic in this grouping. However, names of visual groups must be unique, and we use Python construction ``with`` to markup groups in code: ::

    with filters.viewGroup(<group_name>):
        #define units
        ....

.. _unit_definition:
        
Unit definition
---------------

The following is description of creation methods for different types of units, see discussion in :doc:`../concepts/filtration` for details.

Common options of methods:

* **name**, *string* - unique identifier of unit, and it is important for this name to be an identifier in Python terms, since all constructions over units can be formulate in Python syntax, see :doc:`../concepts/dtree_syntax`

* **vpath**, *string* - for most kinds of units it is :ref:`path<json_path_loc>` to data in annotated JSON record

* **title**, *optional string* - human readable description of unit, can be not defined if **name** is sufficient

* **default_value** - default value of unit if data is not defined in annotated JSON record, it is good practice to set this option always

* **conversion** - *optional list*; representation of conversion method applied to data got from **vpath** to form value of unit for variant, see :doc:`list_conv`

* **render_mode** - *optional string*; used in UI to represent values of unit (see :doc:`../rest/s_prop_stat` for details)

* **tooltip** - *optional string*; explanation of unit meaning to render in UI as tooltip (title in HTML terms)

* for status/multi-status units:

    * **variants** - *optional list of strings*, if presents full list of variants in prepared order (otherwise list of variants is sorted in alphabetical order)

    * **accept_other_values** - *optional boolean*, if ``True``, the full list of variants can be completed by other values, if any found in data

    * **value_map** - *optional dictionary*, if presents it is a translation map of values (usually in use for technical values ``"True"/"False"`` in cases when their meanings are not clear for the user)

Ordinary unit types
^^^^^^^^^^^^^^^^^^^

    * **intValueUnit()**
    
    * **floatValueUnit()**
        
        Values for units of these types are numeric, numeric **default_value** option is required
        
        **diap** - *optional list* of two numeric bounds, lower and upper, if present turns on control that real values in data satisfy these bounds
        
    * **statusUnit()**
        
        Value for unit of status type is a string, all values form list of variants.
        
    * **multiStatusUnit()**

        Value for unit of status type is a list of strings, all values in lists from list of variants. 
        For multi-status units natural default value is empty list, to it is not necessary to define **default_value** option for these units.
    
        **compact_mode** - *optional boolean** set this option to ``True`` if list of variants for this unit is large (hundred or more items)
        
Constrained unit types
^^^^^^^^^^^^^^^^^^^^^^

    * **presenceUnit()**
    
        Presence unit is multi-status unit which values are automatically calculated on dataset creation. 
        
        **var_info_seq** - *list of pairs*: ``[<key>, <path>]``, where ``<key>`` is set as one of unit values if data in annotated JSON record that :ref:`corresponds<json_path_loc>` to ``<path>`` is defined and not empty
        
    * **panelsUnit()**
    
        **unit_base**, *string*: Panels unit is a transformation of another unit with name **unit_base**. The base unit usually have large list of variants (in the current version of system we work with ``Symbol`` unit which variant list contains whole gene symbols nomenclature, it is tens of thousands variants...
        
        **panel_type**, *string*: ...Then there are :term:`gene lists<gene list>` registered as :term:`solution items<solution item>` in :doc:`solution pack<solution_py>`. In the current version of the system they are registered with panel_type ``Symbol``. Thus it is automatic procedure to detect panels that correspond to the given variant, and Panels unit is implementation for this procedure.
        
        .. _flt_unit_view:
        
        **view_path** - *optional string*: Evaluation of panels applied to a variant is an nontrivial procedure, so there might be a need to show its result to the user. If this option is set, result of evaluation of panel list is put to annotated JSON record by the given  :ref:`path<json_path_loc>`

Transcript unit types
---------------------

Transcript units are units with information for :term:`transcripts<transcript>` but not :term:`variants<variant>`, see :doc:`../concepts/filters_reg` for details. So these units are hidden and inactive for :term:`XL-datasets<xl-dataset>`, and active only for :term:`workspaces<workspace>`. 

Activation of these units is a part of logic for :doc:`dataset derivation<../rest/ds2ws>` procedure, so it might happen essentially later than the :term:`primary dataset` was created, and there is no a good way for careful check of values of these datasets. Thus API for their definition is simpler: there is no options **conversion** and **diap** (for numeric units). 

* **trans_name** - common required option, *string*: is used instead of *vpath* option of ordinary units. In the current version of the system all data for transcript units must be :ref:`located<json_path_loc>` in annotated JSON records by path ``/_view/transcripts``, and **trans_name** is extension of this path for the given unit.

    * **transcriptIntValueUnit()**
            
    * **transcriptFloatValueUnit()**
    
    * **transcriptStatusUnit()**
    
        **bool_check_value**, *optional boolean*: is actual for status transcript units to transform boolean data values to their string representation ``"True"/"False"``
        
    * **transcriptMultisetUnit()**

    * **transcriptPanelsUnit()**
    
.. _post_unit_view:

        **view_name**, *optional string**: is used instead of **view_path** for ordinary panels units. Since evaluation of transcript panels unit value is an nontrivial procedure, there might be a need to show its result to the user. If this option is set, result of evaluation of panel list is put to annotated JSON record by the path ``/_view/transcripts`` extended by **view_name**. 
        
        The correspondent viewing attribute in :doc:`view_schema_py` must be signed by special :ref:`attribute kind<attribute_kinds>` ``"posted"``
            
See also
--------

:doc:`../concepts/filtration`

:doc:`code_config`

:doc:`flt_tune_py`

:doc:`list_conv`

:doc:`ajson`
