defaults
========
        **Instance settings**
        
.. index:: 
    defaults; request
    
Synopsis
--------
**dirinfo** 

    **Arguments**: 

            **ds**: *optional* dataset name

    **Return value**: 
        | ``{`` *dictionary*
        |         various settings for the instance of Anfisa
        | ``}``


Description
-----------
The request returns "hardcoded" constants used by instance of Anfisa:

    * **ws.max.count** - maximal count of variants in :term:`WS-dataset`, *int*, 9000
    
    * **export.max.count** - maximal count of variants for :term:`export` process, *int*, 9000
    
    * **tab.max.count** - maximal count of variants for :doc:`tab_report`, *int*, 9000

    
    * **ds.name.max.length** - maximal length for :term:`dataset` name, *int*, 255
    
    * **tag.name.max.length** - maximal length for :term:`tag<tagging>` name, *int*, 255
    
    * **sol.name.max.length** - maximal length for :term:`solution item`, *int*, 255

    * **xl.view.count.full** - maximal count of variants for full :doc:`viewing regime<../concepts/view>` in :term:`XL-dataset`, *int*, 300
    
    * **xl.view.count.samples.default** - count of samples in sampling :doc:`viewing regime<../concepts/view>` in :term:`XL-dataset`, *int*, 25
    
    * **xl.view.count.samples.min** - minimal bound for variant count in sampling :doc:`viewing regime<../concepts/view>` in :term:`XL-dataset`, *int*, 10
    
    * **xl.view.count.samples.min** - maximal bound for variant count in sampling :doc:`viewing regime<../concepts/view>` in :term:`XL-dataset`, *int*, 150

    
    * **solution.std.mark** - mark for standard :doc:`solution items<../concepts/sol_pack>`, *str*, ``"@"``
    
    
    * **run-options** - instance run options, *list of strings*, []
    
    * **run-modes** - instance run modes, *list of strings*, []

    * **job-vault-check-period** - period of time for check for dataset appearing and changes, in seconds, *int*, 30
    
    * if **ds** argument is set:

        * **ds-name** - name off dataset (equals to input *ds* option)
        
        * **can-drop-ds** - if the dataset is applicable for :doc:`drop<adm_drop_ds>` operation, *boolean*
