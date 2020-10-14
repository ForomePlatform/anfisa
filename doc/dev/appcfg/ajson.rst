Annotated JSON file format overview
===================================

.. index:: 
    Annotated JSON file format overview

Annotated JSON file is result of :term:`annotation pipeline` and is the principal 
source of data for a dataset. Usually it is archived by gzip or bzip2 because of its large size.

The file consists of text lines, each line is JSON record. The first record represents 
dataset metadata, next lines represent :term:`variants<variant>` of dataset. Usually variant data 
is long: kilobytes and more. Variants are sorted by chromosome/position, and this 
order defines order of variants in dataset :term:`viewing regime`. 

Here is not complete description of annotated JSON format, we discuss here general structure 
of it and features that are essential for Anfisa functionality. 
    
.. _metadata_fields:
    
Metadata fields
---------------

Metadata is represented in JSON as dictionary, and the following fields are essential for 
proper setup of dataset in Anfisa:

    * **"record_type"**, always ``"metadata"``
    
    * **"case"**, name of case
    
    * **"data_schema"**, kind of data schema, determines variant of logic for preparation and    configuration of dataset, in the current version only ``"CASE"`` is supported
    
    * **"modes"**, *list* of modes of data, the the current version of the system only two modes are supported, and determine which base reference is used in dataset: either ``"hg38"`` or ``"hg19"``
    
    * **"samples"**, *dictionary* representing information about samples in family: identifier, name, sex, if affected, and relations between samples
    
    * **"proband"**, identifier of proband in **"samples"** structure (proband must be always affected)
    
    * **"versions"**, *dictionary* representing versions of sources used in annotation process
    
    * **"cohorts"**, *list*, usually empty; in case if :term:`cohorts<cohort>` present, defines distribution of samples to cohorts
    
Variant data structure
-----------------------

Data for a variant is represented in JSON as dictionary with the following top blocks:

    * **"record_type"**, always ``"metadata"``
    
    * **"_view"**, *dictionary* representing data used for ":ref:`accurate presentation part<accurate_vs_technical>`" of :term:`viewing regime`
    
        "_view" dictionary is container of dictionaries, one per "accurate" :term:`aspects<aspect>`
    
    * **"_filtration"**, *dictionary* representing (most part of) data used for :term:`filtration`
    
        "_filtration" dictionary is container of data items, each one of these items forms content of :term:`unit` property fields
    
    * **"__data"**, *dictionary* representing ":ref:`technical presentation part<accurate_vs_technical>`" of :term:`viewing regime`

        "__Data" dictionary is container of fields represented in `"_main"` technical :term:`aspect`, but some fields in the dictionary can form separated technical aspects (usually multi-column ones and "VCF")
    
Thus, the blocks **"_view"** and **"__data"** are prepared for functionality of :term:`viewing regime`, and the functionality of :term:`filtration` is covered preferably by block **"_filtration"**, but can use other blocks of data.

.. _json_path_loc:

Location path notation in JSON variant annotation
-------------------------------------------------

To locate data inside JSON structure the following path notation is used:

    * any full path notation starts with ``/``, it means that location points to root of JSON annotation
    
    * next blocks in notation are read from left to right and means move of location inside blocks of data
    
    * block ``<identifier>/`` means move of location to identified field inside dictionary
    
    * block ``[]`` means that current point of location is a list, and moves location to elements of this list
    
    * relative path notation is equal to join of base path, symbol '/' and relative path, usually relative path is simple and contains only ``<identifier>``

*Examples of full paths*: 
    
    ``"/_view/bioinformatics/called_by[]"``
    
    ``"/__data/transcript_consequences[]"``
    
    ``"/_filters/dist_from_exon_worst"``

Fixed paths
-----------

The current version of the system assumes that information for :doc:`zygosity<../zygosity>` and :term:`transcripts<transcript>` correspondently are located in annotated JSON record by the following paths:

    ``/__data/zygosity``

    ``/_view/transcripts``

All other paths in use are subject of :doc:`configuration<code_config>`.
    
Modifications in annotated JSON record
--------------------------------------

.. _ajson_modifications:

On creation of dataset the JSON annotated variant record is being modifying by the following logic features of preparation process:

* The following fields are created (processed from deeper information inside JSON record) and are put in top level dictionary and are used in the system for navigation purposes:

    * ``"_label"`` - visualization label of variant, visible in list of variants
    
    * ``"_color"`` - color indication of variant significance
    
    * ``"_key"`` - unique identifier of variant (used in :term:`tagging` mechanism support for identification of records)
    
    * ``"_rand"`` - random integer, used for random variant sampling (:ref:`auxiliary viewing regime<auxiliary_viewing_regime>`)
    
* :doc:`flt_schema_py` logic allows to configure:
    
    * additional :ref:`pre-tranformations<flt_pre_tranform>` of record
    
    * creation of constrained :ref:`panels units<flt_unit_view>` and :ref:`transcript panels unit<post_unit_view>` might require to store result of evaluation inside annotated JSON record
    
See also
--------

:doc:`code_config`

:doc:`../adm/admin`
