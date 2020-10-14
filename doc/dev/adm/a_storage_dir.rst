storage.dir file format
=======================

.. index:: 
    storage.dir, file format
    
The file storage.dir presents some variant of integration solution: the system administrator can form this file in JSON format manually, with use of any text editor, put here all information about maintained datasets, and use path to this file in option **--dir** in administration tools: :doc:`storage` and :doc:`adm_update`. 

If configuration of datasets changes, the user administrator needs to fix changes in storage.dir manually. On shell level, there is also the regime **register** in :doc:`storage`, it allows to register new dataset in storage.dir automatically. 

There is no strong need in this file in current state of the project, the system administrator can perform all administrative actions without it.
    
The file includes:
    
    * reference to the principal configuration file of the system :doc:`configuration`
    
    * for each dataset to be created, currently or in future:
    
        * name of dataset, as a key
        
        * **"kind"** of dataset, either `ws` or `xl`
        
        * either reference path to `annotation json file` **"a-json"**,
        
        * or reference path to :doc:`a_inventory` file **"inv"**
        
Example of file
---------------

::
 
    {
        "anfisa.json": "/data/projects/anfisa/anfisa/anfisa.json",
        "datasets": {
            "PGP3140_panel_hl": {
                "kind": "ws",
                "a-json": "/data/projects/anfisa/a-setup/data/pgp3140_anfisa.json.gz"
            },
            "xl_PGP3140_panel_hl": {
                "kind": "xl",
                "inv": "/data/projects/anfisa/a-setup/data/examples/pgp3140_panel_hl/pgp3140_wgs.cfg"
            }
        }
    }

Comment
-------

The discussed solution is intermediate one: in future the project will require a dashboard integration module for control all processes of data preparation and annotation. Up to this moment the project does not include such a dashboard, thus the storage.dir solution in an integration helper tool with minimal level of comfort in usage. 
    
See also
--------
:doc:`a_adm_formats`
