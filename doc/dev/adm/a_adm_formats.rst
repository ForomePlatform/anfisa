Administration file formats reference
=====================================

.. index:: 
    administration file formats
    
Configuration of the service
****************************

The main control file of the service is :doc:`anfisa.json<configuration>`.

Primary dataset information
***************************

Any :term:`primary dataset` is set up based on data prepared in preliminary :term:`annotation pipeline` process. So annotation pipeline is the necessary part of the whole Anfisa project but it's proper description is not a part of this documentation: Anfisa service uses only results of this pipeline, in form of :term:`annotated JSON files<annotated json file>`, usually in the following formats: 
``*.json``, ``*.json.gz``, ``*.json.bz2`` 
(see details of format here: :doc:`../appcfg/ajson`)

    * The most simple and primitive way of dataset creation uses only this file: just run :doc:`storage` with **--source** option (**--config** option is required, and **--kind** option is important in case of XL-dataset)
        
    * More extended way of dataset creation uses :doc:`a_inventory`: run :doc:`storage` with **--inv** option (**--config** and **--key** options play the same role as above)
        
    * Both ways above operate single dataset, but there is some integration solution. The system administrator can create a file :doc:`a_storage_dir`, collect there all information on primary datasets being maintained, and use path to this file as **--dir** option. 

    In this context options **--config**, **--source**, **--inv**, **--kind** are out of sense because all correspondent peaces of information are being retrieved from :doc:`a_storage_dir`.
        
