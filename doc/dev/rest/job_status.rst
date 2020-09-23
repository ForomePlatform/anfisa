job_status
==========
        **Job status**

.. index:: 
    job_status; request

Synopsis
--------

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

The request returns status of evaluation of a :term:`task<background task>` identified by task ID. If task is unknown return value is null. Format of task result depends on task type.

Comment
-------
* In case of :doc:`/ds2ws<ds2ws>` task, the proper result is dictionary: ``{"ws": <name of workspace created>}``

* In case of :doc:`/ds_list<ds_list>`, the proper result is dictionary, see :doc:`ds_list`
    
