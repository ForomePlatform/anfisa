dtree_counts
============
        **Delayed evaluations of item counts for decision tree points**

Synopsis
--------

.. index:: 
    dtree_counts; request

**dtree_counts** 

    **Arguments**: 

        **ds**: dataset name
        
        **tm**: *optional* time delay control option, in seconds, *float as string*

        **rq_id**: ID of request series
        
        **dtree**: *optional* name of applying decision tree

        **code**: *optional* code of applying decision tree
        
        **points**: list of indexes of required points
                *list of integers in JSON string representation*
        
    **Return value**: 
    
    | ``{`` *dictionary*
    |      "**rq-id**": ID of request series, *string*
    |      "**point-counts**": point counts of items
    |           ``[`` *list of* :doc:`s_point_count` ``]``
    | ``}``

Description
-----------

The request supports mechanism of delayed evaluation of :ref:`decision tree point counters<dtree_points_report>` in case when the main request :doc:`dtree_set`
has returned point counts in incomplete state.

**rq_id** argument should be get from result of initiation request.
Arguments **dtree**, **code**, **no** should be the same as in initiation 
request :doc:`dtree_set`. 

**points** argument is list of point indexes that are required to be evaluated.
Ordering of indexes in list are responsible for priorities of evaluation: first 
entry has highest priority. 

Returning property **point-count** is list of length equal to count of all points 
in tree, and it might contain entries for points not requested by **points** argument.
On another side, the request can return no new data at all, if evaluation process
on server continues too long. However, after numerous requests all count descriptors 
will be evaluated in a final time. And the same input argument **rq_id** is 
important for this mechanism. 

See also
--------
:doc:`dtree_set` 

:ref:`Decision tree points counters evaluation with delays<dtree_points_report>`
