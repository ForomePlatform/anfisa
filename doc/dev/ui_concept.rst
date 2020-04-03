User interface concepts
=======================

Functionality structure
-----------------------

The user interface in system system provides currently 4 types of pages.
Each kind of page provides specific part of the whole functionality
of the system.

:term:`Workspace` main page is the most complex type of pages. It supports 
:ref:`full variant of viewing regime<full_viewing_regime>`, complete panel for 
:term:`filters<filter>` works, and all the functionality 
specific for workspaces: :term:`zones<zone>` and :term:`tagging`.

:term:`XL-dataset` main page is essentially simpler than workspace 
one. Base regime here is :term:`filters<filter>` works. :term:`Viewing regime`
here is :ref:`auxiliary one<auxiliary_viewing_regime>`: the user can view only 
small selections of variants. 

:term:`Decision tree` page maintain complex functionality in a special 
way: modification of decision tree can be made by various ways, in interactive
scenario as well as in direct code edit process. 

:ref:`Status report filtering mechanism<status_report>` in this page
applies to a bunch of different selections, since decision tree have many 
selection points.

:ref:`Auxiliary viewing regime<auxiliary_viewing_regime>` is supported here
as well for all selection points.

All main and decision tree pages for dataset support creation of 
:term:`secondary workspaces<secondary workspace>`. Only main pages for dataset
support export functionality.

:term:`Dataset documentation` is available in separate documentation page.
It includes report for loading or creation of dataset and possibly bunch of
documents in different formats come from annotation process.

For :term:`secondary workspace` it includes reference to documentation on
base dataset. 

Thus we have the following distribution of functionality

.. _work_pages:


    * :term:`Workspace` main work page:
        - :ref:`Full viewing regime<full_viewing_regime>`
        - :term:`filtering<filter>` regime
            - :term:`filtered properties status regime`
        - :term:`zone` panel
        - :term:`tagging`
        - :term:`secondary workspace` creation, :term:`export`
        
    * :term:`XL-dataset` main work page:
        - :term:`filtering<filter>` regime
            - :term:`filtered properties status regime`
        - :ref:`auxiliary viewing regime<auxiliary_viewing_regime>`
        - :term:`secondary workspace` creation, :term:`export`

        
    * :term:`Decision tree` work page (for both 
        :term:`workspaces<workspace>` and :term:`XL-datasets<xl-dataset>`):
        
        - :ref:`auxiliary viewing regime<auxiliary_viewing_regime>`
        - :term:`decision tree` regime:
            - interactive decision tree modification
            - :term:`filtered properties status regime`
            - :term:`decision tree code<Code of decision tree>` modification
        - :term:`secondary workspace` creation
        
    * :term:`Dataset documentation` page
        

Viewing regimes
---------------
.. index:: 
        Viewing regimes; interface principle

.. _viewing_regimes:

Since :term:`variants<variant>` have variety of properties the system provides 
full functionality for view and study these properties. In this regime the main control 
structure is list of variants. Usually they are :term:`filtered<filtration>`: variants in 
the list are selected from the whole :term:`dataset` by :term:`filters<filter>`, 
:term:`decision trees<decision tree>` and :term:`zones<zone>`.

The user can select any of variant form the list, and view and study the whole information about 
this variant. See also details :ref:`below<variant_data_presentation>`.

On different pages the system provides two variants of viewing regime

    .. _full_viewing_regime:
    
    * Full viewing regime
        In context of comparatively small :term:`workspace` user can see all selected variants. 
        Features of workspace functionality, :term:`tagging` and :term:`zone` mechanisms are 
        integrated with this regime. 
        
    .. _auxiliary_viewing_regime:
        
    Auxiliary viewing regime
        In contexts of :term:`XL-dataset` or :term:`decision tree` viewing regime looks simpler - 
        no integration with tagging and zones. But in these contexts there is no guarantee 
        that selection is small enough, so the system makes special preparations to restrict list 
        of visible variants:

        * If list is comparatively small (less than 300 variants), visible list if full one 
            (property **records** is used in request :doc:`rest/ds_list`)
            
        * If list is comparatively large (more than 50 variants), only 25 randomly selected
            samples are visible (property **samples** is used in request :doc:`rest/ds_list`)
        
        
Variant data presentations and aspects
--------------------------------------
.. index:: 
    Variant data presentations; interface principle

.. _variant_data_presentation:

The system provides wide amount of different properties concerning a 
:term:`variant`. Moreover, for different :term:`datasets<dataset>` list of properties 
and their formats can vary. So in generic context the support for accurate rendering
of the whole information about variant is heavy.

REST API supports two ways for rendering data concerning :term:`variants<variant>`:
    
* :doc:`rest/reccnt` 
    request prepares most portion of details of rendering on the 
    server side. 
    
    The whole variant data is split onto fixed collection of :term:`aspects<aspect>`, 
    each one is a portion of HTML-correct document. This request does not have serial 
    variant of call, since information on a single variant might be wide enough.

* :doc:`rest/tab_report` 
    request has only serial form, and provides selected
    comparatively small information on variants; selection scenario are configured on 
    the server side.

Filtering regime
----------------

.. index::
    Filtering regime; interface principle

.. _filtering_regime:


Filtering regime is supported in main :term:`dataset` pages, for 
:term:`workspaces<workspace>` as well as for :term:`XL-datasets<xl-dataset>`.

The principal scenario of this regime is to build :term:`filter`, i.e. sequence
of :term:`conditions` one by one. :ref:`Status report mechanism<status_report>`
is used here in effective way and guarantees that resulting filter is
consistent, i.e. it selects nonempty set of variants. Really, on each stage
the user get complete information what properties can be selected and restricted
by condition on next stage.

However, the user can modify (update) conditions in sequence, and in this case 
there can not be a guaranty to keep filter consistent. So the user needs to do it
more responsively.
    
Status report with delays
-------------------------

.. index::
    Status reports with delays; interface principle

.. _status_report:

If a set of :term:`variants<variant>` (or :term:`transcripts<transcript>`) is selected,
it is possible to prepare and render a report for all filtering properties status.

Status report for a filtering property is information about distribution of values 
of this property on selected variants (transcripts). For numeric property it is diapason 
of values, for enumerated one it is list of actual values with counts of variants having it.

The system evaluates and renders status reports for filtering properties in context 
of any filtered set made by the user. The user can use this information for advances in 
:term:`filtration` process. In practice this mechanism appears to be effective and very 
helpful. It is  intuitively clear for the user and might be used in (informal as well 
as formal) understanding of objects and their properties. 

Status report mechanism is used in two contexts:

- in :ref:`filtering regime<filtering_regime>` it applies to a single selection determined by 
    current working :term:`filter`, i.e. sequence of :term:`conditions`

- in :term:`decision tree` page it can be applied to any of selection points of 
    working tree.

Evaluation of status reports requires heavy processing on the server side, so 
REST API implements logic of :term:`delayed requests<delayed request>` for this 
functionality:
    
- evaluation starts by requests :doc:`rest/ds_stat` or :doc:`rest/dtree_stat` 
    
- argument **tm** in these requests (it is float value in seconds, recommended value: 1) 
    controls time period of evaluation of request; if time is over, requests fill 
    returning list of descriptors with structures without actual status report; the 
    returning value also contains property **rq-id** with unique identifier for next 
    series of delayed requests
    
- the client receives information from the server and uses it for rendering 
    status report controls; some of them are rendered in "undetermined" state
    
- then the client starts series of delayed requests :doc:`rest/statunits` to fill up
    undetermined properties; these requests also have argument **tm** to control
    time period, so in generic case only part of all requested properties are being 
    evaluated in request; however at least one status report should be complete
    
- the client is free to reorder these properties to get in account activity of the 
    user: the user can select properties of interest, or just scroll status 
    report panel to make interesting properties visible, these are the first candidates 
    for evaluation
    
- the client receives result of delayed request (:doc:`rest/statunits`) and re-renders
    information on stat report for evaluated properties; argument **rq-id** helps 
    the client to distinguish proper server responses from other ones: there can happen
    responses from previous inactive series of delayed requests

- in case of heavy evaluations series of delayed requests can be long, so the whole 
    process of evaluation of status reports may take a long time - the user 
    does not need to wait for its final and can continue activity without long delay.
    
Functions support
^^^^^^^^^^^^^^^^^
.. _functions_support:

    Full list of properties status reports contains not only actual properties but also 
    references to functions available for dataset. For this full list the correspondent 
    status report structure is always in incomplete state. 
    
    Functions are additional information items that can be used to build a condition, 
    so it is natural to list them in the same list as properties. But functions require
    their special settings (and UI works to support these settings separately for 
    each function) to make them applicable for making condition. If these settings 
    are well defined, a function behaves in the user interface just as enumerated 
    filtering property. 
    
    Available functions for current version are documented in :doc:`rest/functions`
    
    Use request :doc:`rest/statfunc` to evaluate proper status report for 
    functions (but not :doc:`rest/statunits`!).

Decision tree points report with delays
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. _dtree_points_report:

If decision tree is set, it is important to evaluate number of variants (and transcripts)
that correspond to each point in decision tree. This evaluation might be heavy, so 
it is organized in analogy with mechanism for status reports, using 
:term:`delayed requests<delayed request>`:
    
- evaluation starts by request :doc:`rest/dtree_set`
    
- argument **tm** in this request (it is float value in seconds, recommended value: 1) 
    controls time period of evaluation of request; if time is over, request 
    stops evaluation and returns ``null`` values in list of point count reports; the 
    returning value also contains property **rq-id** with unique identifier for next 
    series of delayed requests
    
- the client receives information from the server and uses it for rendering 
    point counts; some of them are rendered in "undetermined" state
    
- then the client starts series of delayed requests :doc:`rest/dtree_counts` to fill up
    undetermined counts; these requests also have argument **tm** to control
    time period; the request might return nothing new evaluated, however it keeps 
    evaluation process run, so after some serie of requests the complete
    count list will be set up, and using **rq-id** argument is important for this purpose
    
- the client receives result of delayed request (:doc:`rest/dtree_counts`) and 
    re-renders evaluated count information for points

    
Solution items
--------------

.. index::
    Solution items; interface principle

.. _solution_items:

Solution items are configurable objects that used by the user in work with system. 
In the current version of the system we support the following kinds of them:
    
    * items with open control, can be preset or dynamical
        
        - :term:`filters<filter>`
        
        - :term:`decision trees<decision tree>`

    * preset items with hidden control
    
        - :term:`gene lists<gene list>`
        
        - configuration of :term:`zones<zone>` and :term:`tags<tagging>`
        
Not all preset items are visible in context of any dataset: there exists internal 
configuration mechanism that hides preset items if applied dataset does not satisfy
required modes. 
        
Items with open control satisfy the following logic:

    - There are preset items: they are set up in the system configuration, the 
        user can use them and derive operative items starting from them. But the user 
        can not modify these items. 
    
        Preset item always have name, and its name starts with special symbol ``⏚``,
    
    - Dynamical items: the user can fix a working item (filter, decision tree) as 
        solution one by just setting its name. It is possible also to rename or delete 
        dynamical solution item.
    
        Dynamical items are supported common for all datasets derived from the 
        same :term:`root dataset`.   
    
        Note: not all dynamical items are visible in all datasets in the same root node, 
        since some of them created for an :term:`XL-dataset` are 
        not good in context of :term:`workspace`, so they are invisible there.
    
There are plans to extend this spectrum in the future versions by the following ways:

    - extend spectrum of kinds
    
    - extend control level of existing item kinds from hidden to open one
    
    - form "Solution Pool" as autonomous repository with wide spectrum of different 
        solution items useful in wide spectrum of contexts
        

Solution and working items support
----------------------------------

.. index::
    Solution/working items support; interface principle

.. _solution_work_items:

Here we discuss usage of two kinds of items: :term:`filters<filter>` and 
:term:`decision trees<decision tree>`.

Item of such kinds is some complex object, and in practice it has one of 
three status states (note that the user can use item always):

    * preset solution
        The user can not modify it
    
    * dynamical solution
        The user can create, modify, rename and delete it. This item is persistent 
        object, so the user can use it in next sessions.
        
    * working solution
        Item in this state is editable but temporary. It can be stored as solution one 
        (by setting its name). 

If request in REST API uses :term:`filter` item, it can be determined in argument:

.. _fiter_conditions:

    - **filter** *either* as name of filter solution item
    
    - **conditions** *or* list of :term:`condition<conditions>` descriptors, 
        as working copy of item
        
If request in REST API uses :term:`decision tree` item, it can be determined in argument:

.. _dtree_code:

    - **dtree** *either* as name of decision tree solution item
    
    - **code** *or* as :term:`code<code of decision tree>`, as working copy of item
 
Names of filters and decision trees must start with any letter ("alpha") 
symbol (any alphabet) and must not contain spaces; in terms of js the criterium is as follows:
    
    ::
        
        /^\S+$/u.test(name) && (name[0].toLowerCase() != name[0].toUpperCase())

    
