Anfisa introduction
===================

Anfisa is a Linux-based Python application (Python 3.5+) and provides access via HTTP/HTTPS
protocols. It deals with datasets of mutation variants in the human genome. 

The main purpose of the system is to study and select mutation variants for a given case 
of genomics data - dataset. The system provides variety of information associated with 
variants. Part of this information is a result of evaluations of algorithms applying to 
the dataset itself. Another part consists of data selected from resources that accumulate
known information concerning the whole humanity (and widely the set of all alive 
biological forms).

Datasets
--------
The system works with :term:`datasets<dataset>` that are available in :term:`vault` of 
the system. A dataset usually represents genomics information for a medical :term:`case`
and concerns a proband patient with relatives. But system supports also datasets
with data for :term:`cohorts<cohort>` of persons, to perform scientific studies.

:term:Primary datasets are loaded externally by 
administrators of the system, :term:`secondary workspaces<secondary workspace>`
can be created by the user from existing datasets.

Variants and transcripts, kinds of datasets
-------------------------------------------

Main informational unit of the system is :term:`variant` that presents in genome in 
a determined location (chromosome/position) and changes referenced sequence of 
genomics letters ("ref") to an alternative subsequence ("alt"). In regime of 
`XL-datasets<xl-dataset>` (eXtra Large) Anfisa system provides work with millions and 
more variants. 

For small datasets, :term:`workspaces, WS-datasets<ws-dataset>` Anfisa
provides more intensive and ways for work. In particular, in this regime
it uses :term:`transcripts<transcript>` as atomic informational units, which are application 
of known transcription scenario to a variant. Also, Anfisa supports 
:term:`tagging` manual functionality and additional :term:`zone` filtration tool
to provide access of the user to the short and exact required information portion.

Since it is a huge amount of information, the system supports various mechanism for the user 
to effectively restrict his attention onto the most required information. The most powerful 
mechanism here is :doc:`concepts/filtration`. They are :term:`filtering regime` and 
:term:`decision trees<decision tree>`. These tools can be used to search for the most 
important variants inside datasets, as well as produce 
:term:`secondary datasets<secondary workspace>` for more accurate work with reduced 
amount of variants.

Variants and transcripts properties
-----------------------------------

Properties of :term:`variants<variant>` and :term:`trancripts<transcript>` are used 
in the system for two main purposes:

    * :term:`viewing properties<viewing property>` represent information on 
        variants/transcripts in form understandable by the user, they are the main 
        atomic items for :term:`viewing regimes<viewing regime>`
        
    * :term:`filtering properties<filtering property>` of variants/trancripts
        form the low data level for :term:`filtration` processes, as objects
        for definition of :term:`conditions`

.. _work_pages:
        
Work pages of the system
------------------------

There are 4 kinds of Front End pages support by the system:

    * :doc:`concepts/ws_pg`
    
    * :doc:`concepts/xl_pg`
    
    * :doc:`concepts/dtree_pg`
    
    * :doc:`concepts/doc_pg`
    
There is also directory pages for the whole :term:`vault` and its portions with fixed 
:term:`root dataset`, they are provided on Back End level by request :doc:`rest/dirinfo`

Architecture: Back End, REST API, Front End
-------------------------------------------

**Back End** is the kernel of the system. It is written on Python language
and it supports the kernel functionality of the system.

**Front End** is an application that provides the user a comfort access to the system 
from an Internet browser. 

To access the Back End the Front End uses the set of HTTP requests that is 
**REST API** of Anfisa. "REST" term means that the API satisfies certain 
architectural conditions and their responses are in JSON format.

This documentation set describes Anfisa REST API in details.  

External systems
----------------

Anfisa uses the following external systems:

MongoDB_
this database is used to store information about user activities; it does NOT
contain information about datasets.

.. _MongoDB: https://www.mongodb.com/

Druid_ OLAP system
this engine is used for effective support of :term:`XL-datasets<xl-dataset>` 
(Druid is not necessary while working without XL-datasets)

.. _Druid: https://druid.apache.org/

