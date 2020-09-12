storage.dir file format
=======================

.. index:: 
    storage.dir, file format
    
The purpose of file storage.dir is to integrate and control information about assembly of 
:term:`primary datasets<primary dataset>` that are available on a single instance of 
Anfisa system. The format of file is plain JSON, and the system administrator can 
maintain this file with use of any text editor. There is no strong requirement on the 
current stage of project to create this file and maintain this : the system administrator 
is free to use more atomic ways to perform any action.
    
The solution is intermediate one: in future the project will require  
a dashboard integration tool for control all processes of data preparation and annotation  
automatically and with proper user interface. Up to this moment the project does not 
include such a dashboard, and this file technique provides some minimal level of 
integration support for datasets. 
    
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
    
See also
--------
:doc:`a_adm_formats`
