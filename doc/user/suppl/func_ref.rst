.. _func_ref:

*******************
Filtering functions
*******************

Discussion
----------

Up to now all functions behave as multiset property: even if the result is ``True`` value,
there is no reason to keep ``False`` value of the rest of variants in the dataset.

The list and format of function parameters are specific to the function.
Each parameter value must be a data structure in JSON format, usually it is just a single *string* or *int* value,
but some complex functions require complex structures as parameters.
The Front End application helps the user to fill it up in forms,
however the formal definition of function call requires JSON-formatted parameters.

Since work with functions is a complex one, there might be additional requirements for Front End application
to provide support of necessary "shortcuts":

- function environment should be used to set "standard" configurations of function parameters
- in cases when the list of function values is expected (for example if value is single ``True``),
  these values should be pre-selected in the interface without extra user click
        
Most part of the currently available functions implement functionality dealing with zygosity properties of variants.
See :ref:`zygosity_notes` for explanations.

Examples are given in form of Python dialect used in :ref:`decision_tree_syntax`.

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
        
The function allows the user to define simple string representation for the following options:

    - chromosome
    
    - position or diapason of positions
    
    - *optional* gene or list of genes
    
These options are put into a string with ``':``` as a separator. (Separator for list of genes is ``','``).

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
    
The function selects variants with :ref:`standard_zygosity_scenarios` if the problem group is defined.

**Examples**

    ::
    
        Inheritance_mode() in {"Homozygous Recessive", "X-linked"}
        Inheritance_mode(problem_group = ["bgm9001a1", "bgm9001u2"]) in {"Compensational"}

Notes:
    
    - :ref:`default_problem_group` is preset
    
    - function value ``X-linked`` is actual only if case includes a male sample
    
Facts useful for understanding  
    
    - for fixed problem group variant sets of types ``"Homozygous Recessive"`` and ``"X-linked"`` never intersect;
      variants from chromosome X present in the first set only if there is no male sample in case
    
    - for different problem groups variant sets of type ``"Autosomal Dominant"`` never intersect;
      the same is true for type ``"Compensational"``

.. _Custom_Inheritance:

.. index:: 
    Custom_Inheritance; function

Custom_Inheritance()
^^^^^^^^^^^^^^^^^^^^
    **sub-type**: ``"custom-inheritance-z"``
    
    **Parameters**: 
        
        **scenario**, :ref:`zygosity_scenario` *structure*
    
    **Values**: ``["True"]``
    
The function selects variants by a fixed :ref:`zygosity_scenario`.

In terms of functionality it is an extension of :ref:`Inheritance_Mode()<Inheritance_Mode>` function.

**Example**

    ::
    
        Custom_Inheritance(scenario =
            {“2”: ["bgm9001a1", "bgm9001u2"], “1-0”: ["bgm9001u1"]}}) in {True}
    
.. _Compound_Heterozygous:

Compound_Heterozygous()
^^^^^^^^^^^^^^^^^^^^^^^

    **sub-type**: ``"comp-hets"``
    
    **Parameters**: 
        
    |   **approx**, *optional* :ref:`gene_approximations`, *string*
    |   **state**, *optional* decision tree state label, *string*
    
    **Values**: 
        *list* equals to **trio-variants** environment property
            
The function detects :ref:`compound heterozygous<compound-heterozygous>` variants for all trios
presenting in the case of dataset.
The function is available only if (at least one, usually one) trio is included in the case,
i.e. environment property **trio-variants** is nonempty.

Special notation: if proband is subject of the trio, ``"Proband"`` is used as an identifier of the trio,
otherwise trio is identified by the id of its subject.

Default value for **approx** parameter is ``"transcript"`` for WS-datasets and ``"rough"`` for XL-datasets
(only ``"rough"`` is available in XL-datasets).

The parameter **state** can be either ``null`` or value from the **labels** environment property.

In common context **labels** is empty, and **state** parameter can be only ``null`` or undefined.
So the detection procedure is run on the current state of the variants filtering process.

Different situation can happen only in case of the decision tree,
and only if there is а definition of the label in code *before* function evaluation.
In this case detection procedure is run on the labeled state of the filtering process.

**Examples**

    ::
    
        Compound_Heterozygous() in {Proband}
        Compound_Heterozygous(approx = "rough", state = "label1") in {Proband, bgm4321u3}
            
.. _Compound_Request:

Compound_Request()
^^^^^^^^^^^^^^^^^^

    **sub-type**: ``"comp-request"``
    
    **Parameters**: 
        
    |   **request**, :ref:`compound_request` *structure*
    |   **approx**, *optional* :ref:`gene_approximations`, *string*
    |   **state**, *optional* decision tree state label, *string*
    
    **Values**: ``["True"]``

The function evaluates :ref:`Compound_Request`.

In terms of functionality it is a wide extension of :ref:`Compound_Heterozygous` function

All comments on parameters **approx** and **state**, environment properties **approx-modes** and **labels**
from function :ref:`Compound_Heterozygous` are actual in this context.

**Example** 

    ::
    
        Compound_Request(request = [
            [1, {“2-1”: ["bgm9001a1", "bgm9001u2"], “0”: ["bgm9001u1"]],
            [1, {“2-1”: ["bgm9001a1", "bgm9001u1"], “0”: ["bgm9001u2"]]]) in {True}

The example demonstrates realization of Compound_Heterozygous() functionality for trio
``["bgm9001a1", "bgm9001u1", "bgm9001u2"]``.

The user interface provides an easy way to build any of :ref:`standard_zygosity_scenarios`
applied to :ref:`default_problem_group` of the case.
Then the user can modify these scenarios to perform more complex conditions.
