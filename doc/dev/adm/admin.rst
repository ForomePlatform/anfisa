Administration aspects overview
===============================

.. index:: 
    Administration aspects overview


Table of conventional names
---------------------------

.. _adm_notations:

The following notations are used in different places of administration documentation

  ====================== ==================================== =================================
    *Name*                   *Role*                             *Example*
  ---------------------- ------------------------------------ ---------------------------------
    *User/Group*
    ANFISA_ADMIN          User that runs service
    ANFISA_ADMIN_GROUP    Group of the user
  ---------------------- ------------------------------------ ---------------------------------
  \
    *Directories*   
    ANFISA_ROOT           Root directory                       ``/projects/anfisa``
    ANFISA_HOME           Top source directory                 ``/projects/anfisa/anfisa``
    ANFISA_WORK           Directory with service               ``/projects/anfisa/a-setup``
                          :ref:`subdirectories<setup_subdir>`
  ---------------------- ------------------------------------ ---------------------------------
  \     
    *URLs*
    ANFISA_HTML_BASE         top service URL                   ``http://<server>/anfisa/``
    ANFISA_HTML_APP_BASE     URL to LocalUI and REST           ``http://<server>/anfisa/app/``
  ====================== ==================================== =================================
  
Running the service
-------------------

The service itself and the utilities (see below) should be run under the same user ``ANFISA_ADMIN``.

In standalone mode​ the service is started with either of the following command sequences: ::

    $ cd $ANFISA_HOME
    $ python -m app.run [​path to configuration file]

or ::

    $ env PYTHONPATH=”$ANFISA_HOME”
    $ python -m app.run [path to configuration file]

(Make sure if :ref:`Python virtual environment<virtualenv>` is properly activated.

In server mode​, while setting the :ref:`uWSGI<uWSGI>` container, also run the process by the user ``ANFISA_ADMIN`` and use the correct configuration file.

The following commands start resp. stop the uWSGI service: ::

    $ sudo systemctl start anfisa
    $ sudo systemctl stop anfisa

Sharing data between multiple users
-----------------------------------

The current version of the service makes no distinction between users who share access to datasets and perform different actions in a commonly shared environment. It is supposed that these users form a team of experts, and can make agreements about sharing conflicts in an informal way.

Using server configuration (anfisa.json)
----------------------------------------

In both modes the main configuration file is important. There is the file from the repository ``$ANFISA_HOME/anfisa.json.template​``. This file is the default configuration of the service. To use it in stand-alone mode just copy it to ``anfisa.json`` to the same directory.

It is assumed that it is enough to run the stand-alone mode of the service in the default configuration, just copy template to ``anfisa.json`` to the same directory.

In the server mode, as well as in the stand-alone one but with some modifications, one needs to make a copy of this file and put it in another directory.​ ``$ANFISA_ROOT`` is recommended. The name of this file can be the same, ​anfisa.json​, or can be changed. It is important to provide access to the same configuration for administrator utilities and for the stand-alone mode to use it in the start service command.

REST API
--------

REST API​ is the kernel of the system. It is a variety of HTTP requests built within the concept of REST API (ask Google about it). In short, these requests satisfy certain architectural conditions and their responses have the form of JSON objects. Both Legacy UI and NextGen Frontend provide HTML pages, and use these requests in a way hidden from the users to transfer data and actions upon the service. If the NextGen Frontend was perfect, there would be no need to use the internal UI at all. However, the configuration aspects for REST API and the internal UI are close to each other.

.. _file_transfer:

File content transfer aspect
----------------------------

The aspect of transferring file content is a technical one. However, it produces some complexity in the configuration and needs a detailed explanation. Any WEB-service needs to transfer file content in response to HTTP requests. When we have a “main server” (NGINX/Apache/... ), it is good practice to configure it to perform such requests. So in the server mode two kinds of files (used by internal UI) are transferred on the “main server” level: control files ``*.js`` and ``*.css``, and images. (See also the next note, on anti-cache mechanism).

In the stand-alone mode there is no such thing as “main server”, so file transfer requests should be supported by the service itself. The option ​**dir-files** in :doc:`configuration` regulates these operations.

Therefore we have two different mechanisms in different modules to do the same thing, and may it look too complex in the context of this document.

There is a third kind of files that should be transferred. Any Export operation produces an Excel file ``*.xlsx`` that should be downloaded by a client (see below in the section about Export). These transfers happen rarely, and the internal service mechanism (via **​dir-files**) is sufficient for them, so there is no need to configure the “main server” for their support.

.. _anti_cache:

Anti-cache mirroring mechanism
------------------------------

It is used for purposes of the internal UI in the server mode. The problem it solves is the following. The internal UI uses some files (with extensions ``*.js`` and ``*.css``), and these files are checked out from the repository. So after a push from the repository these files can change. If these files were used by the UI directly, there would be a possibility that the user’s browser will ignore changes in such a file and use some outdated cached copy of its previous version instead of the fresh version of it. The workaround for this problem is to create a mirror directory, copy into it all the necessary files but slightly modify their names in such a way that different versions of the same file will have different names.

This mechanism is recommended for the server mode. However, it can be set up in the stand-only mode as well.

.. _setup_subdir:

Directory structure: vault, datasets, logs, export directory
------------------------------------------------------------

Strictly speaking, there is no real necessity in the existence of two “standard’ directories:​ ``$ANFISA_ROOT​`` and​ ``$ANFISA_WORK``. ​But the system strongly requires all the subdirectories placed under ``$ANFISA_WORK``. One can place them anywhere on the computer and modify configuration (​anfisa.json​) correspondingly.

* ``$ANFISA_WORK/vault``  - vault directory
    Information of all the datasets supported by the system is placed here: one dataset - one directory. (There might be a serious need to place this directory in another location: it can happen if the size of a dataset grows and one needs to move the directory to another disk. Just move it, and change the “data-vault” line in the config file correspondingly)
    
    *Note*: there is no strong need to have this directory excactly inside ``$ANFISA_WORK``. It might be large, so there might be a reason to move it on another disk, so just redefine option **data-vault** in :doc:`configuration`. 

* Subdirectories of the vault directory

    Directories for subsets should be created by calls of the app.storage utility made by user $ANFISA_ADMIN. Removal of an XL-dataset should be also done using this utility, because connection to Druid is required in this process. The removal of a workspace also can be done this way, but it is just equivalent to removal of the corresponding directory.

    Please note that this directory contains the empty file ​active​. To turn a dataset out of use in terms of the service one needs to remove this file and restart the service. To re-activate the dataset just create the file active​ once again (by the utility touch)

* ``$ANFISA_WORK/​export`` - export directory

    This is the place where the excel-template file is located. The main need is in the subdirectory

    ``$ANFISA_WORK/export/work``

    This is the place where the system stores all the Excel files generated for export. Each file here is used only once, but there is no automatic procedure to clean files from here later. This clearance should be done by the system administrator periodically

*  ``$ANFISA_WORK/​logs`` - log directory

    In the stand-alone mode only the ​anfisa.log​ file is stored here, plus its old portions. In the server mode there are two log files: ​anfisa.log​ and ​uwsgi.log.​ The former collects all errors that occurred “inside service logic”, the latter collects meaningful errors at the start of the service.

    There is no automatic procedure to cleanse this directory either. Administrator should do it periodically.

* ``$ANFISA_WORK/​ui​`` - mirroring directory

    Used in the anti-cache mechanism in the server mode. See details above

Dataset internal structure
--------------------------

Minimal dataset data is just :term:`annotated JSON file`: ``<dataset>.json.gz``

In expanded form, dataset data forms directory with the following:

    * :doc:`Inventory<a_inventory>` of dataset: ``<dataset>.cfg``

    * Annotated JSON: `<dataset>.json.gz` (see :doc:`a_adm_formats` for details)

    * Optional subdirectory doc/ with supplementary documentation materials
    
    * Optional: BAM-files for samples in dataset case

    * May be more files
    
File dataset structure
----------------------

Dataset in system is represented in form of sub-directory inside ``$ANFISA_WORK/vault`` with name equals to dataset name and the following files:

    * ``dsinfo.json`` - principal information on dataset, in JSON format, contains metadata information and schemas prepared for both viewing regime and filtration purposes

    * ``active`` - empty file, just remove it to pull the dataset off the system, and restore it (shell command ``touch active``) to push the dataset up again
    
    * ``doc/`` - directory with documentation on dataset
    
    * ``fdata.json.gz`` - complete data used in :term:`filtration`, good for use in process of :doc:`Druid<../intro>` ingestion push  
    
    * ``pdata.json.gz`` - "short" information about variants, contains only information for representation of variant in short form
    
    * ``vdata.ixbz2`` - "full" information about variants, contains full annotated JSON records (with :ref:`some modifications<ajson_modifications>` that can be done on creation stage); the format of file "ixbz2" is special in-house one: it allows direct block access for data with blocks compressed by bzip2 algorithm; 
    
    * ``stat.json`` - information on value distributions for both viewing and filtration fields, collected on creation stage  

See also
--------

:doc:`configuration`

:doc:`../appcfg/ajson`
