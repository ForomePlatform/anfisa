reccnt
======
    **Aspect-based full view presentation of variant**

.. index:: 
    reccnt; request

Synopsis
--------

**reccnt** 

    **Arguments**: 

        **ds**: dataset name
        
        **rec**: record order number
    
        .. index:: 
            rec; argument of reccnt

        **details**: *optional* 0-1 bitmap representing selected transcripts

        **samples**: *optional* list of integers representing selected samples
        
        .. index:: 
            details; argument of reccnt        
        
    **Return value**: :doc:`s_view_rec`

Description
-----------
The request prepares view presentation of :term:`variant` record by its order number in :term:`dataset`.

In context of :term:`workspace` filtering :term:`transcript variants<transcript variant>` rendering logic can highlight selected transcript variants if **details** argument is set. Value of **details** argument the client receives in :doc:`ws_list` response in structure :doc:`s_record`.

.. _active_samples:

Some samples can be active in context of current filter or decision tree condition, and argument **samples** is used to transfer this selection. Value of **samples** argument the client receives in :doc:`ds_list` and :doc:`ws_list` responses in ``"active-samples"`` property.
