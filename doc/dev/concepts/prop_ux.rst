UX settings of filtration properties
======================================

:term:`Filtering properties<filtering property>` are very important objects of the system, so the handling of this objects in the Front-End UX logic requires wide spectrum of settings. They form essential part of :doc:`../rest/s_prop_stat`, their congiguration is discussed in :doc:`../appcfg/flt_schema_py`. 

The settings are:

* **title**, *optional string* - human readable description of unit, can be not defined if **name** is sufficient

* **render_mode** - *optional string*; used in UI to represent values of unit, see details below

* **tooltip** - *optional string*; explanation of unit meaning to render in UI as tooltip (title in HTML terms)

* **classes** - *list of integers* 
    
    Integers in the list are index values in descriptor structurr **unit-classes** from :doc:`../rest/s_ds_descr`. 
    
    The last setting requires an extended explanation.
    
.. _properties_classification:
    
Properties classification
-------------------------
    
    Since there are too many various filtering properties in the system, we make an attempt to classify properties by their "universal meanings". The classification is not so clear and distinct, however it is possible to use it to separate properties for use them in different contexts.
    
    The classification has two layers:
    
        - domain (facet) layer: there are numerous domains of classification, each property needs to be classified in each domain
        - low layer: in context of each domain there is list of of types
    
    The classification applied to the dataset forms **unit-classes** field of :doc:`../rest/s_ds_descr` that is return value of :doc:`../rest/dsinfo`.
    
    The facet indexes of concrete filtering property form **classes** field of :doc:`../rest/s_prop_stat`.
    
    In terms of :ref:`variable_registry` facet classification is defined in terms of parameters **facet1, facet2, facet3** - *optional strings*.
    
    The Front End can use this classification to help the user to keep unneccessary properties hidden in the :term:`filtration` process. 
        
    The current version of the system provides the following classification:
    
    +----------------------+-------------------------------------+-------------------+
    |   *facet*            |        *Title*                      |  *Technical name* |
    +======================+=====================================+===================+
    | **Knowledge Domain** |                                     |  **facet1**       |
    +                      +-------------------------------------+-------------------+
    |                      |    Call Annotations                 |  call             |
    +                      +-------------------------------------+-------------------+
    |                      |     Phenotypic Data                 |  phenotype        |
    +                      +-------------------------------------+-------------------+
    |                      |     Compound Rules                  |  rules            |
    +                      +-------------------------------------+-------------------+
    |                      |     Population Genetics             |  popgen           |
    +                      +-------------------------------------+-------------------+
    |                      |     Functional                      |  function         |
    +                      +-------------------------------------+-------------------+
    |                      |     Animal Genetics                 |  animal           |
    +                      +-------------------------------------+-------------------+
    |                      |     Human Genetics                  |  human            |
    +                      +-------------------------------------+-------------------+
    |                      |     Epigenetics                     |  epigenetics      |
    +                      +-------------------------------------+-------------------+
    |                      |     N/A                             |  na1              |
    +----------------------+-------------------------------------+-------------------+
    | **Scale**            |                                     |  **facet2**       |
    +                      +-------------------------------------+-------------------+
    |                      |    Transcript                       | transcript        |
    +                      +-------------------------------------+-------------------+
    |                      |    Variant                          |   variant         |
    +                      +-------------------------------------+-------------------+
    |                      |    Position                         |   position        |
    +                      +-------------------------------------+-------------------+
    |                      |    Window                           |   window          |
    +                      +-------------------------------------+-------------------+
    |                      |    Gene                             |   gene            |
    +                      +-------------------------------------+-------------------+
    |                      |    N/A                              |    na2            |                 
    +----------------------+-------------------------------------+-------------------+
    | **Method**           |                                     |     **facet3**    |
    +                      +-------------------------------------+-------------------+
    |                      |    Statistical Genetics Evidence    |   statgen         |
    +                      +-------------------------------------+-------------------+
    |                      |    Bioinformatics Inference         |   bioinf          |
    +                      +-------------------------------------+-------------------+
    |                      |    Experimental, in Vivo            |   in-vivo         |
    +                      +-------------------------------------+-------------------+
    |                      |    Experimental, in Vitro           |   in-vitro        |
    +                      +-------------------------------------+-------------------+
    |                      |    Experimental, Other              |   explanation     |
    +                      +-------------------------------------+-------------------+
    |                      |    Clinical Evidence                |   clinical        |
    +                      +-------------------------------------+-------------------+
    |                      |    Raw Data                         |   raw             |
    +                      +-------------------------------------+-------------------+
    |                      |    N/A                              |   na3             |
    +----------------------+-------------------------------------+-------------------+

Render modes
------------

  * Render modes for :term:`numeric properties<numeric property>`
  
        - ``"`` *scale*, *bounds* ``"``
            
            *scale*:  ``linear``/``log`` - linear *or* logariphmic scale
            
            *bounds*:  ``<``/``>``/``=`` - meaningful bounds: 
                        ``<`` only upper/ ``>`` only lower / ``=`` both
            
          Examples: 
            
            - ``"linear,<"`` linear scale, only upper bound is meaningful
                
            - ``"log,>"`` logariphmic scale, only lower bound is meaningful
                
        - ``"neighborhood"`` needs center/radius to determine diapason (linear scale assumed)
            
  * Render modes for :term:`enumerated properties<enumerated property>`
    
        - ``"pie"`` used for :term:`status properties<status property>`
        
        - ``"bar"`` used for :term:`multiset properties<multiset property>`, with not too wide spectrum of values
        
        - ``"tree-map"`` used for :term:`variety properties<variety property>`, or for properties with wide spectrum of values
    
See also
--------
:doc:`../rest/s_prop_stat`

:doc:`../rest/dsinfo`

:doc:`../appcfg/flt_schema_py`
