Filtering functions
===================

Discussion
----------
Functions are aggregated information items that can be used in filtration as well as filtering property. Difference between application of an enumerated property and application of a function is in parameters: the function requires proper settings for them. 

Up to now all functions behave as multiset property: even if result is ``True`` value, there is no reason to keep ``False`` value of rest of variants in dataset.

The list and format of function parameters are specific for the function. Each parameter value must be data structure in JSON format, usually it means *string* or *int* value, but some complex functions require complex structures as parameters. The Front End application helps the user to fill it up in forms, however the formal definition of function call requires JSON-formatted parameters.

Since work with functions is a complex one, there might be additional requirements for Front End application to provide support of necessary "short cuts":

- function environment should be used to set "standard" configurations of function parameters;
    
- in cases when list of function values is expected (for example if value is single ``True``), these values should be pre-selected in interface without extra user click
        
Most part of currently available functions implement functionality dealing with zygosity properties of variants. See :doc:`../zygosity` for explanations

Examples are given in form of Python dialect used in :doc:`dtree_syntax`.

Function reference
------------------

.. _GeneRegion:

.. index:: 
    GeneRegion; function

GeneRegion()
^^^^^^^^^^^^
    **sub-type**: ``"region"``
    
    **Parameter**: 
        
        **locus**, location *string*
    
    **Values**: ``["True"]``
        
Function allows the user to define simple string representation for the following options:

    - chromosome
    
    - position or diapason of positions
    
    - *optional* gene or list of genes
    
These options are put into string with ``':``` as separator. (Separator for list of genes is ``','``).

**Examples**:

    ::
    
        GeneRegion(locus = "chr1:6424820") in {True}
        GeneRegion("chr1:6424820-6424920") in {True}
        GeneRegion("chr1::ESPN,HES2") in {True}
    
.. _Inheritance_mode:

.. index:: 
    Inheritance_mode; function

Inheritance_mode()
^^^^^^^^^^^^^^^^^^
    **sub-type**: ``"inheritance-z"``
    
    **Parameters**: 
        
        **problem_group**, *optional* ``[`` *list of* id for samples in case ``]``
    
    **Values**: 

        ``["Homozygous Recessive", "X-linked", "Autosomal Dominant", "Compensational"]``
    
Function selects variants with :ref:`Standard Zygosity Scenarios<standard-zygosity-scenarios>` if problem group is defined. 

**Examples**

    ::
    
        Inheritance_mode() in {"Homozygous Recessive", "X-linked"}
        Inheritance_mode(problem_group = ["bgm9001a1", "bgm9001u2"]) in {"Compensational"}

Notes:
    
    - :ref:`Default problem group<default-problem-group>` is preset
    
    - function value ``X-linked`` is actual only if case includes a male sample
    
Facts useful for understanding  
    
    - for fixed problem group variant sets of types ``"Homozygous Recessive"`` and ``"X-linked"`` never intersect; variants from chromosome X present in the first set only if there is no a male sample in case
    
    - for different problem groups variant sets of type ``"Autosomal Dominant"`` never intersect; the same is true for type ``"Compensational"``

.. _Custom_Inheritance:

.. index:: 
    Custom_Inheritance; function

Custom_Inheritance()
^^^^^^^^^^^^^^^^^^^^
    **sub-type**: ``"custom-inheritance-z"``
    
    **Parameters**: 
        
        **scenario**, :ref:`scenario<zygosity-scenario>` *structure*
    
    **Values**: ``["True"]``
    
The function selects variants by a fixed :ref:`Zygosity Scenario<zygosity-scenario>`.

In terms of functionality it is an extension of :ref:`Inheritance_Mode()<Inheritance_Mode>` function.

**Example**

    ::
    
        Custom_Inheritance(scenario =
            {“2”: ["bgm9001a1", "bgm9001u2"], “1-0”: ["bgm9001u1"]}}) in {True}
    
.. _Compound_Heterozygous:

.. index:: 
    Compound_Heterozygous; function

Compound_Heterozygous()
^^^^^^^^^^^^^^^^^^^^^^^
    **sub-type**: ``"comp-hets"``
    
    **Parameters**: 
        
    |   **approx**, *optional* :ref:`gene approximation variant<gene_aproximations>`, *string*
    |   **state**, *optional* decision tree state label, *string*
    
    **Values**: 
        *list* equals to **trio-variants** environment property
            
The function detects :ref:`compound heterozygous<compound-heterozygous>` variants for all trio presenting in the case of dataset. Function is available only if (at least one, usually one) trio is included in case, i.e. environment property **trio-variants** is nonempty.

Special notation: if proband is subject of trio, ``"Proband"`` is used as identifier of trio, otherwise trio is identified by id of its subject.

Default value for **approx** parameter is ``"transcript"`` for WS-datasets and ``"rough"`` for XL-datasets (only ``"rough"`` is available in XL-datasets).

The parameter **state** can be either ``null`` or value from **labels** environment property. 

In common context **labels** is empty, and **state** parameter can be only ``null`` or undefined. So the detection procedure is run on the current state of variants filtering process. 

Different situation can happen only in case of decision tree, and only if there is а definition of label in code *before* function evaluation. In this case detection procedure is run on labeled state of filtering process. 

**Examples**

    ::
    
        Compound_Heterozygous() in {Proband}
        Compound_Heterozygous(approx = "rough", state = "label1") in {Proband, bgm4321u3}
            
.. _Compound_Request:

.. index:: 
    Compound_Request; function

Compound_Request()
^^^^^^^^^^^^^^^^^^
    **sub-type**: ``"comp-request"``
    
    **Parameters**: 
        
    |   **request**, :ref:`compound request<compound-request>` *structure*
    |   **approx**, *optional* :ref:`gene approximation variant<gene_aproximations>`, *string*
    |   **state**, *optional* decision tree state label, *string*
    
    **Values**: ``["True"]``

The function evaluates :ref:`compound request<compound-request>`. 

In terms of functionality it is a wide extension of :ref:`Compound_Heterozygous()<Compound_Heterozygous>` function 

All comments on parameters **approx** and **state**, environment properties **approx-modes** and **labels** from function :ref:`Compound_Heterozygous()<Compound_Heterozygous>` are actual in this context.

**Example** 

    ::
    
        Compound_Request(request = [
            [1, {“2-1”: ["bgm9001a1", "bgm9001u2"], “0”: ["bgm9001u1"]],
            [1, {“2-1”: ["bgm9001a1", "bgm9001u1"], “0”: ["bgm9001u2"]]]) in {True}

The example demonstrates realization of Compound_Heterozygous() functionality for trio ``["bgm9001a1", "bgm9001u1", "bgm9001u2"]``.

The user interface provides an easy way to build any of :ref:`Standard Zygosity Scenarios<standard-zygosity-scenarios>` applied to :ref:`default problem group<default-problem-group>` of the case. Then the user can modify these scenarios to perform more complex conditions.
