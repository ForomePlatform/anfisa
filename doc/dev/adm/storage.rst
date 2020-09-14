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

    * For options: **--dir**, **--config**, **--source**, **-inv**, **--kind** see discussion in :doc:`a_adm_formats`        
        
    * **--mode​** option determines one of the following operations:
        
        - **create** ​ dataset
        
        - **drop** ​ dataset

        *supplementary commands:*

        * **druid-push** - reinstalls only the Druid part of xl-dataset
        
        * **doc-push​** - reinstalls the documentation for dataset
        
        * **register** - special mode to register (and to rewrite) 
        
        * (The utility provides also mode **favor** as a part of some experimental subproject. 
            Currently this mode is not actual.)

    * **--force** ​ option, affects only  **create** mode,  is used only if dataset already 
        exists but needs to be re-created with a fresh version of source

    * **--nocoord** experimental option, affects only **drop** mode, in case of xl-dataset does not 
        initiate removal of dataset data in Druid 
        
    * **--nodruidpush** experimental mode, applicable in **create** regime, in case of
        xl-dataset does not initiate push data to Druid
        
    * **--reportlines** not an essential option, affects only  **create** mode,
        controls interval between notifications
        during dataset data preparation
        
    * **--delay** not an essential mode, affects only  **create** mode, controls pause b
        etween pushes of data for 
        multiple datasets into Druid
    
    * *Name of database*: in case of an xl-database it must begin with the prefix ``xl_`` 
        or ``XL_``. Secondary workspaces created by this xl-dataset will have the same name 
        but with other prefixes, of the form “ws<​number​>_”.

