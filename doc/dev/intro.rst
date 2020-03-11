Anfisa introduction
===================

Overview
--------

Anfisa is a Linux-based Python application (Python 3.5+) and provides access via HTTP/HTTPS
protocols. It deals with datasets of mutation variants in the human genome. 

The main purpose of the system is to study and select mutation variants for a given case 
of genomic data - dataset. The system provides variety of information accociated with 
variants. Part of this information is a result of evaluations of algorithms applying to 
the dataset itself. Another part consists of data selected from resources that accumulate
known information concerning the whole humanity (and widely the set of all alive 
biological forms).

Since it is a huge amount fo information, the system supports various mechanism for the user 
to effectively restrict his attention onto the most required information. The most powerful 
mechanism here is the filtering, i.e. selection of the required 

Terms
*****

Anfisa provides variety of properties associated with variants. Some properties are result of 
evaluations applied to the exact dataset. Others are selected from resources that accumulate 
known information concerning the whole humanity (and some for all alive biological forms). 
On the logical level of Anfisa, there properties can be used for two purposes:

* **Viewable properties** 
   Anfisa renders viewable properties, and the user can view and study them; properties of this kind might have various forms. 

* **Filtering properties**
    these properties can be used in filtering mechanism: the user can select variants with determined variety of these properties and view/study only the result(s) of filtering(s). Properties of this kind are determined in strict manner: 
    
    * :index:`numeric property`
        each filtering item has only one numeric value for such a property
    
    * :index:`enumerated property`
        values of such property is string from determined list of values. There are two sub-types:
        
        * :index:`status propertiy`
            each filtering item has only one value
        
        * :index:`multiple enumerated property`
            each filtering item can be associated with arbitrary count of values from the determined list
            
The datasets can be of two different kinds with Anfisa providing different functionality dependent on the kind:

* :index:`XL-dataset`
   (XL, eXtra Large) usually represents a whole exome (WES) or a whole genome and can encompass up to 10 million variants. Users can search subsets of variants, and form (secondary) workspaces from them to perform more detailed studies.

* :index:`Workspace`
   (WS) is a dataset of a small number of variants (up to 10000). Users can view and tag variants in it. Workspaces are either created as derivative datasets from an XL-dataset or can also be directly ingested into the system as primary datasets. The latter option is used for analyzing gene panels.

In case of XL-dataset filering item is variant itself.

In case of Workspace each variant can be interpreted in context of concrete transcript of gene coding, so the system provides multiple filtering items, :index:`"trancripts"` per one variant. In case of variant not participating in gene coding (located deep inside intron for example) it forms a single filtering item.

Dataset support
***************

:index:`Primary datasets` are created directly from prepared data and can be of type XL or WS. 
Only administrators of the system can create them in the vault of the system, as well remove them from there. Users can create secondary datasets using the logic discussing below. 

For any dataset the user can perform two kinds of activities: to view/study variants (and their transcripts) or to filter them. It is reasonable that filtering dominates in works with large amount of variants, and viewing dominates elsewhere.

Starting with a large (and even huge) amount of variants, the user can select small subset of important variants and study them. The ways of selection/filtering are automated but the user can control them completely in clear manner. 

Filtering is an automated powerful mechanism to select important variants from the whole list of variants. There are two kinds of filtering in system:

* :index:`Filtering process`
    In this context the user formulates a sequence of conditions than restricts the whole set of variants (transcripts) to its subset. 

* :index:`Decision tree`
    This context provides complex way to select the required items from the whole list
    
When a comparetively small subset of interesting variants is prepared, it can be saved in a :index:`secondary workspace` and continue studies inside it. Secondary workspaces are always of type WS. The user can produce more restricted workspases from each other.

`REST API`
----------

.. describe::`REST API`

is the kernel of the system. It is a variety of HTTP requests built within the
concept of REST API (ask Google about it). In short, these requests satisfy certain architectural
conditions and their responses have the form of JSON objects.

This documentation set describes this variety in details.  

External systems
----------------

Anfisa uses the following external systems:

MongoDB_
this database is used to store information about user activities; it does NOT
contain information about datasets.

.. _MongoDB: https://www.mongodb.com/

Druid_ OLAP system
this engine is used for effective support of XL-datasets (Druid is not
necessary while working without XL-datasets)

.. _Druid: https://druid.apache.org/

