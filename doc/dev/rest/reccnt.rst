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

        .. index:: 
            details; argument of reccnt        
        
    **Return value**: :doc:`s_view_rec`

Description
-----------
The request prepares view presentation of :term:`variant` record by its order number in :term:`dataset`.

In context of :term:`workspace` filtering :term:`transcripts<transcript>` rendering logic can highlight selected transcripts if **details** argument is set. Value of **details** argument the client receives in :doc:`ws_list` response in structure :doc:`s_record`.
