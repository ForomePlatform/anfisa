Configuration of viewing schema API
===================================

.. index:: 
    Configuration of viewing schema API

This is description of part of API of code configuration layer dealing with configuration of data of :term:`variants<variant>` for full viewing regime, see :doc:`../concepts/view` for details. Here we explain application of this API in the source file

``app/config/view_schema.py``

::

    class AspectSetH:
        def __init__(self, aspects):
            ...
        def __getitem__(self, name):
            ...

    class AspectH:
        def __init__(self, name, title, source, field = None,
                attrs = None, ignored = False, col_groups = None,
                mode = "dict"):
            ...
        def setAttributes(self, attrs):
            ...
            
    class AttrH:
        def __init__(self, name, kind = None, title = None,
                is_seq = False, tooltip = None):
            ...
            
    class ColGroupsH:
        def __init__(self, attr_title_pairs = None,
                attr = None, title = None, single_group_col = False):
            ...

    def defineViewSchema(metadata_record = None):
        ...


Viewing schema is list of :term:`aspects<aspect>`, so we define each aspect one by one. 

The viewing schema is configured in ``defineViewSchema()`` function as instance of ``AspectSetH`` class, that represents list of :term:`aspects<aspect>`, as instances of ``AspectH`` class.

Aspects initialization
----------------------

* **name** of aspect is technical identifier not visible for the user

* **title** is visible title of aspect

* **source** is name of the top dictionary of aspect data in annotated JSON :term:`variant` record

* **field** is *optional*, if presents it is sub-field of top data dictionary that contains aspect data

* **mode** = ``"dict"`` 

    Almost all aspects have mode ``dict`` and correspond to table presentation of data. 

    Most of them are single-valued tables, so have representation in two columns: one for name of field, another for value. For this aspects the option **col_groups** is ``None``. 
    For this case of aspect top data handler must be a dictionary, and each name/value pair correspond to the table row.

    *Example* of single-valued aspect: ::
    
        AspectH("view_gnomAD", "gnomAD", "_view", field = "gnomAD")
        
    As it is defined, all data in annotation JSON variant record with start :ref:`path<json_path_loc>` ``/_view/gnomAD`` are put into aspect with technical name ``view_gnomAD``.
    
    Some aspects have multi-column representation, for these items the option **col_groups** is an instance of ``ColGroupsH`` class. This instance defines one or many groups of columns in table. Each group is defined by name (identifier) and title (visible for users, might be empty).
    
    Note that representation model does not make distinction between tables with stable count of columns and dynamical one (when count can vary between different variants).
    
    * Definition of ColGroupsH without option **single_group_col** corresponds to case when aspect top data handler must be a dictionary with fields named as names of column groups. Values of these fields must be empty (undefined), or lists. And each entry of this list corresponds to a column in the table.
    
        *Examples*: ::
        
            AspectH("view_transcripts", "Transcripts", "_view",
                col_groups = ColGroupsH([("transcripts", "Transcripts")]))
            AspectH("transcripts", "VEP Transcripts", "__data",
                col_groups = ColGroupsH([
                    ("transcript_consequences", "Transcript"),
                    ("regulatory_feature_consequences", "Regulatory"),
                    ("motif_feature_consequences", "Motif"),
                    ("intergenic_consequences", "Intergenic")]))
    
    * If option **single_group_col** is set to ``True``, presentation table consists of fixed count of columns, and each column group contains only one column. In this case aspect top data handler, as in previous case, must be a dictionary with fields named as names of column groups. But values of these fields are not lists but dictionaries, and each of them corresponds to a column in the table.
    
        *Example* (simplified): ::
        
            AspectH("view_cohorts", "Cohorts", "_view", field = "cohorts",
                col_groups = ColGroupsH([["A", "A"], ["B", "B"]], single_group_col = True)))

* **mode** == ``"string"``

    The mode is needed to represent technical data in form of long text. 

    *Example* ::

        AspectH("input", "VCF", "__data", field = "input", mode = "string")]

Attribute definition
--------------------
    
On creation of dataset all the data in :term:`annotated JSON file` is parsed, checked and registered. So there is no strong need to register all the data attributes in annotated data: they will be automatically detected and added to the correspondent aspects. However, it is good practice to register all attributes implicitly for purposes of control and accuracy in presentation of data.
        
Options of attribute definition
    
* **name** is identifier of attribute, is equal to name of field in dictionary of the aspect in annotated data record

    In case of multi-column aspect, attribute value is fetched by this identifier for each of columns in correspondent dictionary in annotated JSON variant record. There is no difference if value is null or undefined: the correspondent cell in the table is shown as empty. If all values in row are empty, the row is being hidden. 

.. _attribute_kinds:

* **kind** should be one of the following strings:
    
    ``"null", "list", "dict", "empty", "link", "string", "int", "numeric", "json"``

    ``"json"`` is recommended for all complex types of JSON objects
    
    There are two exceptional kinds also: they mean not real attributes but placeholders:
    
    * ``"place"`` - this attribute placeholder should be replaced but another attribute with runtime evaluation, see :doc:`view_tune_py` for details
    
    * ``"posted"`` - this attribute placeholder is going to be controlled by dynamical state of filter :term:`unit`, see :ref:`details here<post_unit_view>`
    
* **title** is *optional* visible (in left column of table) name of attribute, by default equals to **name**

* **is_seq** is *optional boolean*, if set to ``True``, means that value of attribute is always list
                
* **tooltip** is *optional*, is present the user can see this text as tooltip (title in HTML terms) of attribute

    *Examples*: ::
        AttrH("ref", title = "Ref")
        
        AttrH("genes", title = "Gene(s)", is_seq = True,
            tooltip = "Gene Symbol (Ensembl classification)")
    
See also
--------

:doc:`code_config`

:doc:`view_tune_py`

:doc:`ajson`
