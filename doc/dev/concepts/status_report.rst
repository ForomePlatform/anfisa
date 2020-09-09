Status report mechanism with delays
===================================

If a set of :term:`variants<variant>` (or :term:`transcripts<transcript>`) is selected 
in process of  :doc:`filtration`, it is actual to prepare and render a report for all 
filtering properties status applied to this set.

Status report for a filtering property is information about distribution of values 
of this property on selected :term:`variants<variant>` (:term:`transcripts<transcript>`). 

For numeric property it is diapason of values, for enumerated one it is list of actual 
values with counts of variants having it.

In practice this mechanism appears to be effective and very helpful. It is 
intuitively clear for the user and might be used in (informal as well 
as formal) understanding of objects and their properties. 

Status report mechanism uses two options:

    - argument of requests **tm** (it is float value in seconds, recommended value: 1) 
        controls time period of evaluation of request; in case of timeout requests return
        incomplete result
    
    - returning property **"rq-id"** and argument of delayed requests **rq_id** 
        with the same value allows to organize series of requests in single evaluation context 
 
Status report mechanism starts by initiation request: 
 
- in :doc:`filters_reg` it applies to a single selection determined by current working 
    :term:`filter`, i.e. sequence of :term:`conditions`
    
    Initiation REST API request: :doc:`../rest/ds_stat` 

- in :doc:`dtree_pg` it can be applied in context of any :term:`decision tree point`.

    Initiation REST API request: :doc:`../rest/dtree_stat` 

Evaluation of status reports requires heavy processing on the server side, so 
REST API implements logic of :term:`delayed requests<delayed request>` for this 
functionality:
    
- the client receives information from the server and uses it for rendering 
    status report controls; some of them are rendered in "undetermined" state
    
- in case if undetermined cases happen, the client renders all information (including 
    information on incomplete status data), and starts series of delayed 
    requests :doc:`../rest/statunits` to fix up undetermined properties 
    
- the client is free to reorder these properties to place properties of most priority 
    at the beginning of property list; so the Front End application can get in
    account the user activity: the user can select properties of interest, or just 
    scroll status report panel to make interesting properties visible
    
- the client receives result of delayed request (:doc:`../rest/statunits`) -  
    even  if timeout happens, at least one status report should be complete during request -
    and re-renders information on stat report for evaluated properties

- in case of heavy evaluations series of delayed requests can be long, so the whole 
    process of evaluation of status reports may take a long time - the user 
    does not need to wait for its final and can continue activity without long delay.
    
Decision tree points report with delays
---------------------------------------

.. _dtree_points_report:

If decision tree is set, it is important to evaluate number of variants (and transcripts)
that correspond to each :term:`point<decision tree point>` in decision tree. 
This evaluation might be heavy, so it is organized in analogy with mechanism for status 
reports, using :term:`delayed requests<delayed request>`:
    
- evaluation starts by request :doc:`../rest/dtree_set`
    
- argument **tm** in this request (it is float value in seconds, recommended value: 1) 
    controls time period of evaluation of request; if time is over, request 
    stops evaluation and returns ``null`` values in list of :term:`point<decision tree point>`
    count reports; the 
    returning value also contains property **rq-id** with unique identifier for next 
    series of delayed requests
    
- the client receives information from the server and uses it for rendering 
    point counts; some of them are rendered in "undetermined" state
    
- then the client starts series of delayed requests :doc:`../rest/dtree_counts` to fill up
    undetermined counts; these requests also have argument **tm** to control
    time period; the request might return nothing new evaluated, however it keeps 
    evaluation process run, so after some series of requests the complete
    count list will be set up, and using **rq-id** argument is important for this purpose
    
- the client receives result of delayed request (:doc:`../rest/dtree_counts`) and 
    re-renders evaluated count information for points
