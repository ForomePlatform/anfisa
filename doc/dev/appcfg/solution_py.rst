Configuration of solution pack API
===================================

.. index:: 
    Configuration of solution pack API

This is description of part of API of code configuration layer dealing with :term:`solution items<solution item>`. Here we explain application of this API in the source file

``app/config/solution.py``

Solution Pack API
-----------------

Solution pack is a named collection of named :term:`solution items<solution item>` of various kinds. Solution items are being registered in solution pack with option **requires**: what *modes* should be hold on dataset to make this item available.

*Note*: to prevent mistakes in usage of solution items of different types, name of any solution item must be unique between all names of solution items. 

Solution packs should be defined in process before work with any dataset. Creation of dataset is simple:

::

    base_pack = SolutionPack("CASE")
    
    # ...
    # and later, after configuration:
    SolutionPack.regPack(base_pack)

Instance of class SolutionPack provides the following methods for registering various solution items:

::

    class SolutionPack:
        def regFilter(self, flt_name, cond_seq, requires = None):
            ...
        def regDTree(self, tree_name, fname_seq, requires = None):
            ...
        def regItemDict(self, name, the_dict, requires = None):
            ...
        def regPanel(self, panel_name, panel_type, 
            fname = None, items = None, requires = None):
            ...
        def regZone(self, zone_title, unit_name, requires = None):
            ...
        def regTabSchema(self, tab_schema, requires = None):
            ...

    # Helpers

    class ConditionMaker:
        @staticmethod
        def condNum(unit_name,
                min_val = None, min_eq = True, max_val = None, max_eq = True):
            ...
        @staticmethod
        def condEnum(unit_name, variants, join_mode = "OR"):
            ...
        @staticmethod
        def condFunc(unit_name, func_args, variants, join_mode = "OR"):
            ...
        
    def cfgPathSeq(seq_file_names):
        ...
    
    def cfgPath(file_name):
        ...

    class ReportTabSchema:
        def __init__(self, name, use_tags = False):
            ...
        def addField(self, name, field_path):
            ...
        def addMustiStrField(self, name, separator, field_path_seq):
            ...
            
    # System configuration callback
    def completeDsModes(ds_h):
        ...
            
*Remarks*:

    * All functions for registration has the same argument **requires**. If not empty, the value of it should be set of strings, meaning modes that should be hold for dataset to make the redistered item available.
    
    * For two types of solution items, filters and decision tree codes, their names automatically completes with prefix symbol `⏚` to make distinction between these preset items and dynamical ones, see :doc:`../concepts/sol_work` for detais.
    
    * For two kinds of solution items, decision tree codes and panels definition of item requires file with content. In the the current version of system these files are fixed in repository and located in code subdirectory ``app/configure/files``. Extensions for these files are ``.pyt`` and ``.lst`` corespondently. 
    
    Helper functions ``cfgPathSeq()`` and ``cfgPath()`` are used in code to transform file names of this files to their full path in ``app/configure/files`` directory, correspondently for list of names and for a single name.
            
* **regFilter** (self, flt_name, cond_seq, requires = None)

    Registration of :term:`filter` as naming solution item. 
    
    *Note* The name of filter automatically completes with prefix symbol `⏚` to make distinction between these preset items and dynamical ones, see :doc:`../concepts/sol_work` for detais.

    *Example*: ::
    
        base_pack.regFilter("HighConfidence", [
            ConditionMaker.condEnum("FT", ["PASS"]),
            ConditionMaker.condNum("Max_GQ", min_val = 50),
            ConditionMaker.condNum("FS", max_val = 30),
            ConditionMaker.condNum("QUAL", min_val = 40)]
            requires = {"WS"})
            
    Here is a definition and registration of filter with name ``HighConfidence`` (for users ``⏚HighConfidence``) available if mode ``WS`` is on, i.e. if dataset is a :term:`workspace`.
    
    Content of filter is sequence of :term:`conditions`, to create a condition one needs to use the helpers in class ``ConditionMaker``. The document :doc:`../rest/s_condition` detailed description of another presentation of the same objects, see it for explanation and details.
    
    Different meaningful filters contain duplication of the same conditions, so in practical application code (in ``app/config/solution.py``) lists of conditons are constructed as concatenation of various predefined lists. 
    
* **regDTree** (self, tree_name, fname_seq, requires = None)

    Registration of :term:`decision tree code` as naming solution item. 
    
    *Example*: ::
    
        base_pack.regDTree("Trio Candidates",
            cfgPathSeq(["quality.pyt", "rare.pyt", "trio.pyt"]),
            requires = {"trio_base"})

    Different meaningful decision tree codes contain duplication of the same blocks, so the method provides construction of decision tree from sequence of portions of code. 

* **regPanel** (self, panel_name, panel_type, fname = None, items = None, requires = None)

    Registration of panels, in other words :term:`gene lists<gene list>`. Most panels are used for preparation of panel :term:`units<unit>` (see details in :doc:`flt_schema_py` the discussion of **panelsUnit()** function). 
    
    Items in panel can be defined either via file name or items directly.
    
    *Example*: ::
    
        base_pack.regPanel("ACMG59", "Symbol",
            cfgPath("acmg59.lst"))

    In the current version of system the following types of panels are used:
        
        * ``"Symbol"`` panel type is used define sets of gene identifiers
        
        * ``"_tags"`` panel type is used for panel ``"Check-Tags"`` to define set of checked :term:`tags<tagging>` (see :doc:`../rest/ws_tags` for details)
         
* **regItemDict** (self, name, the_dict, requires = None)

    Registration of dictionary of items. 

* **regZone** (self, zone_title, unit_name, requires = None)

    Registration of :term:`zone` as naming solution item
    
    Unit name must correspond to :term:`enumerated property` that presents in dataset. (One "zone" dealing with tags is predefined)

* **regTabSchema** (self, tab_schema, requires = None)

    Registration of instance of ``ReportTabSchema`` helper class that defines tabular representation of selected data for records.
    
    These instances are used in functionality of :doc:`export in CSV format<../rest/csv_export>` and :doc:`representation variant data in tabulated form<../rest/tab_report>`.
    
    For explanation of paths used in field definitions see :ref:`here<json_path_loc>`
    
    *Example*: ::
    
        csv_tab_schema = ReportTabSchema("csv", use_tags = False)
        csv_tab_schema.addField("chromosome", "/_filters/chromosome")
        csv_tab_schema.addMustiStrField("variant", "|", [
            "/_filters/chromosome",
            "/_filters/start",
            "/_filters/ref",
            "/_filters/alt"])
        base_pack.regTabSchema(csv_tab_schema)

Logic of solution item requirements for dataset
-----------------------------------------------

.. _dataset_modes:

The inscance of solution pack is being created on the very start of the service (as well as of ``../adm/storage`` utility), and then datasets are loaded (resp. created) with usage of this fixed solution pack. But not all solution items are applicable for all datasets, so the logic of requirements is provided.

On creation of dataset the system determines what modes are applicable for the dataset:
    
    * modes stored in :ref:`metadata<metadata_fields>` are regisered for dataset
    
    * modes either ``WS`` or ``XL`` are regisered dependently of dataset type
    
    * mode ``ZYG``, if dataset provides information about zygosity of variants (usually yes)
    
    * the system configuration callback ``completeDsModes()`` is being evaluated; in case of data schema `CASE` in the current version of the system the following modes can be registered inside this callback (see reference of :ref:`metadata fields<metadata_fields>` for explanation of terms used below):
    
        * ``trio`` if family has at least one sample with both parents in case
        
        * ``trio_pure`` if proband has both parens in case
        
        * ``cohorts`` if cohorts are defined in dataset

Thus at the very beginning of work with a dataset the lits of its modes is determined, so any solution item is applicable for the dataset if its required modes are all applicable for dataset.

See also
--------
    
:doc:`code_config`

:doc:`../concepts/sol_pack`
