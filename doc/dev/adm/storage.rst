app.storage - Dataset creation and upload
=========================================

.. index:: 
    storage; administration utility

The utility used to create or drop a dataset in the vault of the system. It is recommended to run it
from ``$ANFISA_HOME`` directory, or use ``PYTHONPATH`` env variable to set this directory as
python base.

Here are the options of the utility: ::

  $ cd $ANFISA_HOME
  $ python -m app.storage --help
  usage: storage.py [-h] [-d DIR] [-c CONFIG] [-m MODE] [-k KIND] [-s SOURCE]
                    [-i INV] [-f] [-C] [--reportlines REPORTLINES]
                    [--delay DELAY] [--nodruidpush]
                    names [names ...]
  
  positional arguments:
    names                 Dataset name(s)
  
  optional arguments:
    -h, --help            show this help message and exit
    -d DIR, --dir DIR     Storage directory control file
    -c CONFIG, --config CONFIG
                          Anfisa configuration file, used only if --dir is
                          unset, default = anfisa.json
    -m MODE, --mode MODE  Mode: create/drop/druid-push/doc-push/register/favor
    -k KIND, --kind KIND  Kind of dataset: ws/xl, default = ws, actual if --dir
                          is unset
    -s SOURCE, --source SOURCE
                          Annotated json, actual if --dir is unset and mode =
                          create
    -i INV, --inv INV     Annotation inventory
    -f, --force           Force removal, actual if mode = create
    -C, --nocoord         Druid: no use coordinator
    --reportlines REPORTLINES
                          Portion for report lines, default = 100
    --delay DELAY         Delay between work with multiple datasets, in seconds
    --nodruidpush         No push into Druid, if mode = create

Examples
********

Create workspace dataset PGP3140 from source file::

    $ python3 -u -m app.storage -m create -k ws -f -s ~/tmp/PGP3140.json PGP3140
    
Drop dataset PGP3140::

    $ python3 -m app.storage -m drop -k ws PGP3140

 
Comments
********

    * For options: **--dir**, **--config**, **--source**, **-inv** see discussion in :doc:`a_adm_formats`        
        
    * **--mode​** option determines one of the following operations:
        
        - **create** ​ dataset
        
        - **drop** ​ dataset

        *supplementary commands:*

        * **druid-push** - reinstalls only the Druid part of xl-dataset
        
        * **doc-push​** - reinstalls the documentation for dataset
        
        * **register** - special mode to register (and to rewrite) 
        
        * (The utility provides also mode **favor** as a part of some experimental subproject. 
            Currently this mode is not actual.)

    * **--kind** option is set to ``ws`` by default, use ``xl`` if you need an 
        xl-dataset (in case of **--dir** is set this information is used from :doc:`a_storage_dir` 


    * **--force** ​ option is used if one needs to refill an existing dataset with a fresh 
        version of source, and is out of use otherwise

    * *Name of database*: in case of an xl-database it must begin with the prefix ``xl_`` 
        or ``XL_``. Secondary workspaces created by this xl-dataset will have the same name 
        but with other prefixes, of the form “ws<​number​>_”.

