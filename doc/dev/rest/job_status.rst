job_status
==========
        **Job status**

Synopsis
--------

.. index:: 
    job_status; request

**job_status** 

    **Argument**: 

        .. index:: 
            task; argument of job_status
        
        **task** task ID

    **Return value**: 

        | ``null`` *or* ``[`` *list*:
        |    **[0]**: ``false`` *or* task result
        |    **[1]**: task status, *string* ``]``


Description
-----------

The request returns status of evaluation of a :term:`task<background task>` identified by task ID.
If task is unknown return value is null. Format of task result depends on task type.

Comment
-------
TRF:

    * In case of /xl2ws task, the proper result is dictionary {"ws": <name of workspace created>}
    * In case of /ds_list, the proper result is dictionary, see /ds_list
    
