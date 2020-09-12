Administration file formats reference
=====================================

.. index:: 
    administration file formats
    
Configuration of the service
****************************

The main control file of the service is :doc:`anfisa.json<configuration>`.


Primary dataset information
***************************

Any :term:`primary dataset` is set up based on data prepared in preliminary 
:term:`annotation pipeline` process. So annotation pipeline is the necessary part
of the whole Anfisa project but it's proper description is not a part of this 
documentation: Anfisa service uses only results of this pipeline, in form of 
:term:`annotated json files`, usually in the following formats: 
``*.json``, ``*.json.gz``, ``*.json.bz2``

    * The most simple and primitive way of single dataset creation uses 
        only this file: just run :doc:`storage` with **--source** option 
        (**--config** option is required)
        
    * More extended way of single dataset creation uses :doc:`a_inventory`: run
        :doc:`storage` with **--inv** option (**--config** option is required)
        
    * But the recommended way of datasets creation is another one:
    
        * the service administrator can create a file :doc:`a_storage_dir` 
            (in manual regime, just in a text editor)
        
        * put there path to :doc:`configuration` (i.e. **--config** option)
        
        * describe there all primary datasets needed for support (**--source** 
            or **--inv** option, and also **--kind** per each of datasets)
            
        * create all datasets using :doc:`storage` using the same option **--dir**
        
        * and support :doc:`a_storage_dir` in good state in advance
        
        * :doc:`storage` supports special mode **register** to add a new dataset 
            to :doc:`a_storage_dir` automatically, the system administrator
            can use this mode for further automation
