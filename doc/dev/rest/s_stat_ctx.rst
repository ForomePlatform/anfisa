Property status context descriptor
==================================

.. index:: 
    Property status context descriptor; data structure

Format
------

| ``{`` *dictionary of options*
| ``}``

Description
-----------
The descriptor is used as parameter **ctx** in requests that :doc:`collect statistics<../concepts/status_report>` for filtering properties. 

Variety context options:
------------------------
The following options affect behavior for :doc:`variety/panel units<../concepts/variety>`.

|   **max-rest-size**: *integer*

The default limit is set to 300. Using this option the Front-End can change it.

|   *unit_name.* **base-panel**: *string*
|   *unit_name.* **sym-list**: [*list of strings*]
|   *unit_name.* **sym-pattern**: *string*

For example: ``"Symbol.base-panel": "ACMG59"``

These options are three ways to define list of :term:`active symbols`. Options have variety unit name as prefix. 

    - *unit_name.* **base-panel** defines active list by by name of existing panel

    - *unit_name.* **sym-list**: defines active list directly
    
    - *unit_name.* **sym-pattern** defines name pattern for symbols (see **pattern** argument of :doc:`symbols` for details)
    
Use not more than one of these options in request. If one of these options is set, the request does not generate **panels** information in response.

Druid presentation option
-------------------------

In context of :term:`XL-dataset` :doc:`statistic data<../concepts/status_report>` for any filtering property is collected on the low level by direct request to :ref:`Druid<Druid_in_Anfisa>` OLAP system. 
The option supports the way to retrieve this request in JSON format, for demonstration purposes only: 

|   **druid-rq**: ``1`` 

Use this option in for :doc:`statunits` request with single unit name in list as **units** argument, and only in :term:`XL-dataset` context. With this option the return value of the request is the Druid requsts (in JSON format)

See also
--------
:doc:`../concepts/status_report`

:doc:`../concepts/variety`

:doc:`ds_stat`  
:doc:`dtree_stat`  
:doc:`statunits`  
:doc:`statfunc`  
