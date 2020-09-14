app.adm_mongo - MongoDB storage administration
===============================================

.. index:: 
    app.adm_mongo, administration utility

Some kinds of :doc:`solution items<../concepts/sol_work>` are stored in a 
separated storage on the server side, in Mongo DB instance. The 
administration utility app.adm_mongo is used to view, dump, restore and clean up 
this information.

The system used Mongo DB storage in a very soft ant flexible manner:

    * The can be a situation when a dataset is present but not registered on 
        Mongo DB level; it just means that there is no specific information
        on dataset that was stored in Mongo DB
        
    * Vice versa: there can be a dataset registered in Mongo DB but not present
        in the system; it means that a dataset with this name existed some time
        before in the system, some specific information on this dataset was stored 
        in Mongo DB, but later the dataset was removed.
        
In practice, these flexible features of Mongo DB layer are useful. Especially
in case of re-creation of dataset by new version of data. But sometimes there can 
be a need to make clean up procedure in Mongo DB layer, and the utility provides 
mode **drop** for it.

The utility output is data of JSON format, or multiple JSON records, one per line. 
In case of use option **--pretty** the output is formally incorrect, so use this 
option only for view purposes.

Here are the options of the utility: ::

    $ cd $ANFISA_HOME
    $ python -m app.adm_mongo --help
    usage: adm_mongo.py [-h] [-c CONFIG] [-a ASPECTS] [--pretty] [--dry] [-m MODE]
                        [datasets [datasets ...]]

    positional arguments:
    datasets              Dataset names or pattern with '*'

    optional arguments:
    -h, --help            show this help message and exit
    -c CONFIG, --config CONFIG
                            Anfisa config file
    -a ASPECTS, --aspects ASPECTS
                            Aspects: All/Filter/Dtree/Tags/Info
    --pretty              Pretty JSON print
    --dry                 Dry run: just report instead of data change
    -m MODE, --mode MODE  Command: list/dump/restore/drop

Comments on options
-------------------

    * **--config** option: path to :doc:`configuration`
        
    * **--aspects** There are 4 kinds of information that are stored in Mongo DB in the current 
        version of the system. On level of the utility they form *aspects* of information,
        distinguished by single capital letters:

        * **F** - :term:`filters<filter>`
        * **D** - :term:`decision trees<decision tree code>`
        * **T** - :term:`tags<tagging>`
        * **I** - information notes for datasets
        * **A** - all, union of all aspects
        
        The default value of **--aspects** is `FDT`
    
        Aspects **F**, **D**, **T** are applicable to :term:`primary datasets<primary dataset>` only.
        
        Aspect **I** is applicable to any dataset in the system, and it is excluded from the default
        value of **--aspects**

    * **--mode**
    
        The following modes are provided:
        
        * **list**
            The mode prints all datasets registered in Mongo DB, datasets options should be empty
        
        * **dump**
            Reports contents of Mongo DB correspondent to the determined databases and determined aspects.
            
            Note: use option **--pretty** for view purposes and do not use this options if you 
            need back up data and expect to use output in further **restore** operation(s)
        
        * **restore**
            This mode is used either to restore data from back-up, or to populate specific 
            information items between datasets. Use empty datasets options in the first case, 
            and only the single dataset name in second one.
            
            The content of restored data are read from standard input, for example
            
            ::
                python -m app.adm_mongo -m restore PGP3140 < [path to file with dumped data]
                
        * **drop**
            The mode just cleans up all data from Mongo DB that corresponds to datasets and 
            **--aspect** options
            
    * **--pretty** option affects only **dump** mode, and makes output readable, do not use this
            option to store in files and further attempts to use **restore** mode
            
    * **--dry** option, affects only in **restore** mode: does not perform real 
        restore operation but reports (to standard error stream) on all the changes in data
