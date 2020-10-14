Filtering regime
================

User logic
----------

Filtering regime is supported in main :term:`dataset` pages:
    
- for :term:`workspaces<workspace>` in :doc:`ws_pg` 

- for :term:`XL-datasets<xl-dataset>` in :doc:`xl_pg`.

The principal scenario of this regime is to build :term:`filter`, i.e. sequence of :term:`conditions`.

The principal feature of the regime is as follows: 

    On each stage the user has complete information for all filtering properties values distributions. 
    
This feature is complex one and rather heavy to support, however it is very important part of functionality, since it essentially helps the user in understanding what is happening in current selection and in keeping control over the filtering procedure. 

In simple scenario the user adds conditions to filter one by one in an interactive way, and the user interface can guarantee that the resulting filter is built is consistent, i.e. it select nonempty set of :term:`variants<variant>` (:term:`transcripts<transcript>`).

Also the user can modify (update) conditions in sequence, and under these circumstances there can not be a guaranty in keeping filter consistent. So the user needs to do this updates more responsively.

The regime uses :doc:`status_report`. It is critical in case of large dataset, since the user can work with data without long delays, in situation where the complete list of results of required data evaluations take long time. 

Interface logic
---------------

Here is discussion of user interface requirements for the filtering regime. 

Control areas
^^^^^^^^^^^^^

There are 4 areas on filtering panel:

* Units (filtering properties) area
    
    The area is split onto blocks representing one :term:`filtering property` or :term:`filtering function`. Blocks are grouped thematically with common title for group. 

    Filtering property block is being rendered with name, title(optional), and information of values distribution from property status descriptor (see :doc:`../rest/s_prop_stat`). It is visible if property status is incomplete.

* Current condition area
    
    This area is used for create or update condition for a filtering property and function. It looks and behave different for different kind of filtering property or function: for numeric properties it is small, for enumerated ones it contains possibly large control for variants of values, for functions it might be even more wide if parameter settings are complex.
    
* Conditions area
    
    Split on blocks for each condition in current filter. Empty if current filter is empty.
    
* Naming area
    
    The area needs to support load, create, update and delete named filters (see :doc:`sol_work` for details)
    
Not-ready controls
^^^^^^^^^^^^^^^^^^
    
There are controls needed to work out various not-ready situations:

* Shadow for the whole Units area
    
    In use until request :doc:`../rest/ds_stat` is not complete. The user sees some shadowed previous content of the area but the interface is not responsible for it. (It is possible to clear the area, but it might be uncomfortable for the user)
        
* State "Loading information..." for Current condition area
    
    In use until the client is waiting for status report of the current property. 
        
* Shadow for list of values for current filtering function.
    
    In use until request :doc:`../rest/statfunc` is not complete.

All these features are important only in case of :term:`XL-datasets<XL-dataset>` where request evaluation might take long time.

Technical details 
~~~~~~~~~~~~~~~~~

Priority of properties in status report mechanism
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
    Priority of properties can be controlled in request :doc:`../rest/statunits` by reordering items in **units** argument. If the user clicks on some property, it should be loaded with top priority. Next priority have properties that are visible by the user (if the user can scroll Units area). All other properties might be loaded later.
    
Current selection
^^^^^^^^^^^^^^^^^
Current selection in filtering panel is a synchronized complex of selections:

- filtering property in Current Condition area

- the same filtering property is selected in Units area

- if Conditions area contain conditions using the same filtering property, one of them is selected; otherwise selection in Conditions area is empty

To change selection the user can pick units (filtering properties) as well as conditions. If unit is selected, the first condition with this property should be selected automatically.

There is essential difference in setting up Current Condition area by a property without existing condition, or by existing condition. In the first case the interface can use status property descriptors to guarantee nonempty result of condition being created, otherwise only update logic is possible without any guarantee.

If the user selects a filtering property, and the client does not have its status descriptor yet, the Current Condition area needs to keep state "Loading information..." until the request :doc:`../rest/statunits` with the required descriptor is being completed.
    
Enumerated properties in Current Condition area 
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
    (see :doc:`../rest/s_condition`)

- Join mode. There are 3 possible variant of join mode for enumerated condition: 

    join mode: ``"OR"`` *or* ``"AND"`` *or* ``"NOT"``

    Mode ``"OR"`` is common for most part of conditions, it needs to be either pre selected or even hidden to choice. 

    Note also that in case of :term:`status property` operation AND is out of sense. 

- Values with zero counts. There can be many variants in list of values that are absent in current filtering selection, and property status descriptor contains these values with zero counts. These values should be hidden for the user in normal situation. 

    But in case where condition over property uses these values, they needs to be visible. So checkbox "Show zeros" needs to be provided in the user interface to resolve this coincidence. 
    
    One more problem: condition might use variant of value that does not present in property status descriptor at all. To work out this situation accurately these values need to be added to the rendering list of values, with zero counts. 
    
- Long lists. Length of value variants can be very long, especially in case of :term:`XL-datasets<XL-dataset>`. It might cause heavy but worthless traffic between the server and client. In future releases we are planning to comlexify API for these cases to provide more effective and useful solution.
        
REST API requests 
-----------------
For support filtering regime:

- :doc:`../rest/ds_stat`
    Principal request to support the regime

- :doc:`../rest/statunits`
    Delayed evaluations for filtering property status data

- :doc:`../rest/statfunc`
    Function filtering support
