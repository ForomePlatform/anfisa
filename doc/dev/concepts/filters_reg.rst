Filtering regime
================

Filtering regime is supported in main :term:`dataset` pages, for 
:term:`workspaces<workspace>` as well as for :term:`XL-datasets<xl-dataset>`.

The principal scenario of this regime is to build :term:`filter`, i.e. sequence
of :term:`conditions`.

The principal feature of the regime is as follows: 

    On each stage the user has complete information for all filtering properties 
    values distributions. 
    
This feature is complex one and rather heavy to support, however
it is very important part of functionality, since it essentially helps the user in
understanding what is happening in current selection and in keeping control over 
the filtering procedure. 

In simple scenario the user adds conditions to filter one by one in an interactive way, 
and the user interface can guarantee that the resulting filter is built is consistent, 
i.e. it select nonempty set of :term:`variants<variant>` (:term:`transcripts<transcript>`).

Also the user can modify (update) conditions in sequence, and under these circumstances
there can not be a guaranty in keeping filter consistent. So the user needs to do 
this updates more responsively.

The regime uses :doc:`status_report`. It is critical in case of large dataset, since
the user can work with data without long delays, in situation where the complete list 
of results of required data evaluations take long time. 

REST API requests for support filtering regime:

    - :doc:`../rest/ds_stat`
        Principal request to support the regime
    
    - :doc:`../rest/statunits`
        Delayed evaluations for filtering property status data
    
    - :doc:`../rest/statfunc`
        Function filtering support
