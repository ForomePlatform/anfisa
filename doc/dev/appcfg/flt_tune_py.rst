Tuning filtration schema API
============================

.. index:: 
    Tuning of filtration schema API
    
:term:`Filtration` functionality uses not only :term:`filtering properties<filtering property>` but :term:`filtering functions<filtering function>` also. So main part of filtering schema is configured in terms of :doc:`flt_schema_py`, and then on tuning stage one needs to insert function :term:`units<unit>` into it, and configure these functions. 

For full reference of functions used in the current version of the system see :doc:`../rest/func_ref`. 

Unfortunately, this part of configuration API is deeply connected with the system kernel: most part of functions are features of :doc:`zygosity complex<../zygosity>` and have heavy implementation. So it is not possible to describe this API independently of system kernel API, as it was declared in :doc:`code_config`. 

Here we superficially explain application of tuning API in the source file

``app/config/view_tune.py``
    
* Main objects of tuning are instances of classes for :term:`filtering functions<filtering function>`. Each of these classes has method ``makeIt()``:  

::

        class <Function>Unit:
            @staticmethod
            def makeIt(ds_h, descr, before = None, after = None):
                ...

..
    with the following arguments:

    * **ds_h** - is reference to dataset instance (insertion of unit happens after filtering schema preparation, on stage of dataset creation)
    
    * **descr** - dictionary with three properties: "name", "title", "vgroup"; the first two are similar to options of :ref:`unit definition<unit_definition>`; "vgroup" determines *existing* visual group in filtering schema
    
    * **before** / **after** - optional arguments, only one can be used; name of *existing* unit in visual group (determined by "vgroup" property of **descr**) that is used as neighbor of the function unit; if both options are not set, the unit is appended to visual group
    
    Before creation of a filtering unit, one needs to determine if it is actual for the specific dataset
    
* Zygosity Support complex should be configured here: 

    - It is required to setup data for X-chromosome in terms of units of filtering schema: ::
    
        zyg_support.setupX(x_unit = "Chromosome", x_values = ["chrX"])

    - It is required to setup :ref:`gene approximations<gene_aproximations>` available for the dataset: ::

        zyg_support.regGeneApprox("rough",
            "Symbol", "non-intersecting transcripts")
        ...

* ``GeneRegion()`` function unit is not a part of zygosity complex, so is comparatively light in implementation, and configurable. To create instance of this function unit one needs to define references to units from filtering schema in a single dictionary with properties ``chrom/start/end/symbol``   

See also
--------

:doc:`flt_schema_py`

:doc:`code_config`

:doc:`../rest/func_ref`
