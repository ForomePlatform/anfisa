adm_update.py - Update secondary datasets
=========================================

.. index:: 
    app.adm_update, administration utility

The utility is used to update :term:`secondary workspaces<secondary workspace>`
automatically. There are two cases of use for this application:

    * either primary dataset(s) has been changed, and the user needs to update
        correspondent secondary dataset(s)
        
    * or the logic of solutions are being changed, and the user needs to 
        recreate secondary dataset in an informal way, use **--force** option
        in this case
    
The logic of utility is based on fact that any secondary dataset keeps inside
"receipt" of its creation from base dataset. This receipt is either :term:`filter`
or :term:`decision tree<decision tree code>`. So procedure of re-creation
can be evaluated automatically. (See also option **--plainreceipt** for details).
    
Here are the options of the utility: ::

    $ cd $ANFISA_HOME
    $ python -m app.adm_update --help
    usage: adm_update.py [-h] [-d DIR] [-c CONFIG] [-m MODE] [-f] [-p]
                        [names [names ...]]

    positional arguments:
    names                 Dataset name(s)

    optional arguments:
    -h, --help            show this help message and exit
    -d DIR, --dir DIR     Storage directory control file
    -c CONFIG, --config CONFIG
                            Anfisa configuration file, used only if --dir is
                            unset, default = anfisa.json
    -m MODE, --mode MODE  Mode: scan/update
    -f, --force           Force update
    -p, --plainreceipt    Plain receipt in restore, solution names are ignored

Comments on options
-------------------

    * **--config** (:doc:`configuration`) or **--dir** (:doc:`a_storage_dir`), use only 
        one option from these two, the option **--dir** might be slightly more helpful: 
        it allows to detect if primary dataset is outdated comparing to its source
    
    * **--force** option is applicable for mode **update** if secondary dataset 
        needs to be re-created by some informal reason
        
    * **--plainreceipt** is applicable for mode **update** in case when "receipt" of dataset 
        creation (either :term:`filter` or :term:`decision tree<decision tree code>` is 
        a :doc:`named solution item<../concepts/sol_work>`, and content of receipt itself
        might be different to content of current state of solution item. By default, the content
        of solution item has priority over content of receipt, use option **--plainreceipt** 
        to change priority to content of receipt itself

    * **--mode** Two modes are supported:
    
        * **scan** is default, it detects status of all datasets in :term:`vault` and print
            this as list, see status explanations and example below 
        
        * **update** updates dataset(s)
        
            * if option **--force** is off, the utility mode updates a dataset if its base 
                dataset has  been updated, dependency logic is taken in account as in "make"
                utilities
                
            * if option **--force** is on, there should be explicit list of dataset name(s)
                to perform update operation
                
Status of dataset
-----------------

    * ``OK`` - dataset is OK, no update needs
    
    * ``UPDATE`` - dataset needs to be updated because its base dataset was updated or recreated
    
    * ``UPDATE+`` - dataset needs to be updated but only after update of its base dataset 
            
    * ``NO-SOURCE`` - the source of primary dataset is absent, 
            might appear only with **--dir** option

    * ``PRIMARY-OUT-OF-DATE`` - the source of primary dataset newer than dataset,
            use :doc:`storage` to re-create it with fresh data,
            might appear only with **--dir** option
            
    * ``BLOCKED`` - there is no possibility to update dataset properly, possibly 
            intermediate dataset between it and root has been removed
            
    * ``HEAVY-BLOCK`` - some kind of heavy problems of dependencies between datasets
            
    * ``BAD`` - dataset state is bad (just remove it from the vault, it is out of use)
            
Example of list output
----------------------
The output contains:

    * status of dataset
    
    * information for receipt: in case of filter it is number of conditions in filter,
        in case of decision tree number of instructions in decision tree code; 
        name of receipt, if receipt is a named solution
        
    * dependency path between dataset and its root, contains ``?`` symbols if 
        some dataset in this path has been removed

::

    $ python -m app.adm_update 
    *       OK      PGP3140_panel_hl
                            [ PGP3140_panel_hl ]
    *       OK      PGP3140_panel_hl_1
                            [ PGP3140_panel_hl/PGP3140_panel_hl_1 ]
                            >receipt kind: filter c-count: 1
    *       OK      PGP3140_panel_hl_1_1
                            [ PGP3140_panel_hl/PGP3140_panel_hl_1_1 ]
                            >receipt kind: filter c-count: 1
    *       BLOCKED ws_BGM_RSRCH_PGP3140_WGS_NIST_3_3_2
                            [ XL_PGP3140_WGS_NIST_3_3_2/?/ws_BGM_RSRCH_PGP3140_WGS_NIST_3_3_2 ]
                            >receipt kind: dtree name: ⏚BGM Research d-count: 34

