Anfisa REST API
===============

Requests
--------

  ==================== =============================================================
  \ 
  *Vault level*    
   :doc:`dirinfo`       Vault information
   :doc:`single_cnt`    Single variant full JSON data
   :doc:`job_status`    Job status
   :doc:`adm_update`    Force vault state update
  -------------------- ------------------------------------------------------------- 
  \ 
  *Dataset level*
  \ 
   :doc:`dsinfo`        Dataset information
   :doc:`ds_list`       List of variants in auxiliary viewing regime
   :doc:`reccnt`        Aspect-based full view presentation of variant
   :doc:`recdata`       Variant full JSON data
   :doc:`tab_report`    Viewing data in tabulated form
   :doc:`vsetup`        View data schema information
   :doc:`solutions`     Solution items information
  -------------------- -------------------------------------------------------------
    \ 
  *Filtering regime*
  \ 
   :doc:`ds_stat`       Filtering regime support
   :doc:`statunits`     Delayed evaluations for filtering property status data
   :doc:`statfunc`      Function filtering support
  -------------------- -------------------------------------------------------------
    \ 
  *Decision trees*
  \ 
   :doc:`dtree_set`     Decision tree page setup
   :doc:`dtree_counts`  Delayed evaluations of item counts for decision tree points
   :doc:`dtree_stat`    Filtering properties status report for decision tree page
   :doc:`dtree_check`   Decision tree code check
   :doc:`dtree_cmp`     Comparison of decision trees
  -------------------- -------------------------------------------------------------
  \ 
  *Operations*
  \ 
   :doc:`export`        Export operation
   :doc:`ds2ws`         Creation of secondary workspace
  -------------------- -------------------------------------------------------------
  \ 
  *WS-dataset support*
  \ 
   :doc:`ws_list`       Current list of variants
   :doc:`zone_list`     Zone support information
   :doc:`ws_tags`       Tagging variant information retrieval and modifications
   :doc:`tag_select`    Tag navigation support
  ==================== =============================================================


.. toctree::
   :maxdepth: 1
   :hidden:

   dirinfo
   single_cnt
   job_status
   adm_update

   dsinfo 
   ds_list
   reccnt
   recdata
   tab_report
   vsetup   
   solutions
   
   ds_stat
   statunits
   statfunc
   
   dtree_set
   dtree_counts
   dtree_stat
   dtree_check
   dtree_cmp
   
   export
   ds2ws
   
   ws_list
   zone_list
   ws_tags
   tag_select
   
Structures
----------

.. toctree::
   :maxdepth: 1
   
   s_ds_descr
   s_doc_descr
   s_view_rec
   s_condition
   s_prop_stat
   s_dtree_point
   s_point_count
   s_record
   s_sol_entry
   s_zone
   s_tags

References
----------

.. toctree::
   :maxdepth: 1

   func_ref
   s_dtree_instr
   
