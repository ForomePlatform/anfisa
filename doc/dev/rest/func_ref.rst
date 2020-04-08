Filtering functions
===================

Discussion
----------

Functions are aggregated information items that can be used in :doc:`../concepts/filtration` as well
as :term:`filtering properties<filtering property>`. Difference between application of an
:term:`enumerated property` and application of a function is in parameters: the 
function requires proper settings for them. 

Up to now all functions behave as :term:`multiset property`: even if result is ``True`` value, 
there is no reason to keep ``False`` value of rest of items in dataset (variants or transcripts).

The list and format of function parameters are specific for the function. 
Each parameter value must be data structure in JSON format.
So the Front End application needs to handle each function in a specific way. 

The logic of function usage is as following:

    - API requests :doc:`ds_stat` and :doc:`dtree_stat` deliver on the client 
        :doc:`s_prop_stat` for all applicable functions. Thus the Front End gets information 
        of placement of functions in list of filtering properties, and so called 
        environment information for each function.
    
    - The user can select function and set its parameters to build condition; the Front End 
        needs to support this process with use of environment information
    
    - When parameters a set, the request :doc:`statfunc` delivers on the client
        :doc:`s_prop_stat` for this function, with information about available value
        variants. Thus the user can make proper selection of variants and complete
        the condition (see :doc:`s_condition` for details of condition format).
        
Since work with functions is a complex one, there might be additional requirements
for Front End application to provide support of necessary "short cuts":

    - function environment should be used to set "standard" configurations of function 
        parameters;
        
    - in cases when list of function values is expected (for example if value 
        is single ``True``), these values should be pre-selected in interface 
        without extra user click
        
Most part of currently available functions implement functionality dealing with 
zygocity properties of variants. See :doc:`../zygocity` for explanations

Examples are given in form of Python dialect used in :doc:`../concepts/dtree_syntax`.

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
    
    **Environment properties**: *none*
        
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
    
**Additional interface requirement**: 

    The user interface needs to keep check for ``"True"`` value selection on. 
    
    
.. _Inheritance_mode:

.. index:: 
    Inheritance_mode; function

Inheritance_mode()
^^^^^^^^^^^^^^^^^^
    **sub-type**: ``"inheritance-z"``
    
    **Parameters**: 
        
        **problem_group**, *optional* ``[`` *list of* id for samples in case ``]``
    
    **Environment properties**: 
    
   |    **“family”**:  ``[`` *list of* id for all samples in case, first is proband ``]``
   |    **“affected”**:  ``[`` *list of* id, default problem group ``]``
        
    **Values**: 

        ``["Homozygous Recessive", "X-linked", "Autosomal Dominant", "Compensational"]``
    
Function selects variants with :ref:`Standard Zygocity Scenarios<standard-zygocity-scenarios>`
if problem group is defined. 

**Examples**

    ::
    
        Inheritance_mode() in {"Homozygous Recessive", "X-linked"}
        Inheritance_mode(problem_group = ["bgm9001a1", "bgm9001u2"]) in {"Compensational"}

Notes:
    
    - default problem group is preset
    
    - function value ``X-linked`` is actual only if case includes a male sample
    
**Additional interface requirement**: 
    
    There should be an easy way to reset value of problem group to default one.

Facts useful for debug purposes 
    
    - for fixed problem group variant sets of types ``"Homozygous Recessive"`` and 
        ``"X-linked"`` never intersect; variants from chromosome X present in the first 
        set only if there is no a male sample in case
    
    - for different problem groups variant sets of type ``"Autosomal Dominant"`` never 
        intersect; the same is true for type ``"Compensational"``

.. _Custom_Inheritance:

.. index:: 
    Custom_Inheritance; function

Custom_Inheritance()
^^^^^^^^^^^^^^^^^^^^
    **sub-type**: ``"custom-inheritance-z"``
    
    **Parameters**: 
        
        **scenario**, :ref:`scenario<zygocity-scenario>` *structure*
    
    **Environment properties**:

   |    **“family”**:  ``[`` *list of* id for all samples in case, first is proband ``]``
   |    **“affected”**:  ``[`` *list of* id, default problem group ``]``

    **Values**: ``["True"]``
    
The function selects variants by a fixed :ref:`Zygocity Scenario<zygocity-scenario>`.

In terms of functionality it is an extension of :ref:`Inheritance_Mode()<Inheritance_Mode>` function.

**Example**

    ::
    
        Custom_Inheritance(scenario =
            {“2”: ["bgm9001a1", "bgm9001u2"], “1-0”: ["bgm9001u1"]}}) in {True}
    
**Additional interface requirements**: 
    
    There should be an easy way to reset **scenario** to one of 
    :ref:`standard scenarios<standard-zygocity-scenarios>` with default problem group. 

    The user interface needs to keep check for ``"True"`` value selection on. 

.. _Compound_Heterozygous:

.. index:: 
    Compound_Heterozygous; function

Compound_Heterozygous()
^^^^^^^^^^^^^^^^^^^^^^^
    **sub-type**: ``"comp-hets"``
    
    **Parameters**: 
        
    |   **approx**, *optional* :ref:`gene approximation variant<gene_aproximations>`, *string*
    |   **state**, *optional* :term:`decision tree state label`, *string*
    
    **Environment properties**:
    
    |   **"trio-variants"**: ``[`` *list of* id for subject samples of trio, *strings* ``]``
    |   **"approx-modes"**: ``[`` *list of* available :ref:`gene approximation variants<gene_aproximations>`, *strings* ``]``
    |   **labels**: ``[`` *list of* available :term:`decision tree state labels<decision tree state label>`, *strings* ``]``
 
    **Values**: 
        *list* equals to **trio-variants** environment property
            
The function detects :ref:`compound heterozygous<compound-heterozygous>` variants for all trio 
presenting in the :term:`case` of :term:`dataset`. Function is available only if 
(at least one, usually one) trio is included in case, i.e. environment property **trio-variants** 
is nonempty.

Special notation: if proband is subject of trio, ``"Proband"`` is used as identifier of trio, 
otherwise trio is identified by id of its subject.

Default value for **approx** parameter is the first item in **approx-modes** environment property.

The parameter **state** can be either ``null`` or value from **labels** environment property. 

In common context **labels** is empty, and **state** parameter can be only ``null`` or 
undefined. So the detection procedure is run on the current state of variants filtering 
process. 

Different situation can happen only in case of :term:`decision tree`, and only if there is 
а definition of label in code *before* function evaluation. In this case detection procedure
is run on labeled state (:term:`decision tree point`) of filtering process. 

**Examples**

    ::
    
        Compound_Heterozygous() in {Proband}
        Compound_Heterozygous(approx = "rough", state = "label1") in {Proband, bgm4321u3}
            
**Additional interface requirements**:

    In case if proband has trio in case, user interface needs to keep check for 
    ``"Proband"`` value selection on. 

.. _Compound_Request:

.. index:: 
    Compound_Request; function

Compound_Request()
^^^^^^^^^^^^^^^^^^
    **sub-type**: ``"comp-request"``
    
    **Parameters**: 
        
    |   **request**, :ref:`compound request<compound-request>` *structure*
    |   **approx**, *optional* :ref:`gene approximation variant<gene_aproximations>`, *string*
    |   **state**, *optional* :term:`decision tree state label`, *string*
    
    **Environment properties**: 
    
    |   **“family”**:  ``[`` *list of* id for all samples in case, first is proband ``]``
    |   **“affected”**:  ``[`` *list of* id, default problem group ``]``
    |   **"approx-modes"**: ``[`` *list of* available :ref:`gene approximation variants<gene_aproximations>`, *strings* ``]``
    |   **labels**: ``[`` *list of* available :term:`decision tree state labels<decision tree state label>`, *strings* ``]``
        
    **Values**: ``["True"]``

The function evaluates :ref:`compound request<compound-request>`. 

In terms of functionality it is a wide extension of 
:ref:`Compound_Heterozygous()<Compound_Heterozygous>` function 

All comments on parameters **approx** and **state**, environment properties 
**approx-modes** and **labels** from function 
:ref:`Compound_Heterozygous()<Compound_Heterozygous>` are actual in this context.

**Example** 

    ::
    
        Compound_Request(request = [
            [1, {“2-1”: ["bgm9001a1", "bgm9001u2"], “0”: ["bgm9001u1"]],
            [1, {“2-1”: ["bgm9001a1", "bgm9001u1"], “0”: ["bgm9001u2"]]]) in {True}

The example demonstrates realization of Compound_Heterozygous() functionality 
for trio ``["bgm9001a1", "bgm9001u1", "bgm9001u2"]``.


**Additional interface requirements**:

    There should be an easy way to setup any scenario in request sequence to 
    form of any of :ref:`Standard Zygocity Scenarios<standard-zygocity-scenarios>`
    applied to default problem group of the case. 
    (See details in discussion of :ref:`Inheritance_mode()<Inheritance_mode>`)

    The user interface needs to keep check for ``"True"`` value selection on. 
