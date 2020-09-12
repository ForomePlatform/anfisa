Anfisa glossary
===============

.. glossary::

    Variant
        Variant is the base object of the system. It corresponds to a difference 
        (mutation) in genome code between of some fixed person and "standard" genomics sequence. 
    
    
    Dataset
        is a collection of variants; the system supports two kinds of datasets: 
        XL-datasets and workspaces, or WS-datasets

    Case
        is group of persons - samples - with family connections between each other whose genomics
        information is registered in dataset.
        
    Cohort
        is group of persons, possibly large, collected for scientific purposes
        
    Sample
        person in :term:`case`, may be affected or unaffected. Proband sample in medical cases 
        is always affected
    
    Trio
        tree persons: child and two parents, child is subject of trio; 
        in practice :term:`cases<case>` are often trio
    
    Vault
        Storage for all :term:`datasets<dataset>` represented in the system
        
    XL-dataset
        eXtra Large :term:`dataset`, may contain arbitrary many variants

    Workspace
    WS-dataset
        comparatively small dataset (less than 9000 variants); object of :doc:`concepts/ws_pg`
        
        :term:`Filtration` in this case applies to :term:`transcripts<transcript>`
        
        :term:`Tagging` and :term:`zone` selection mechanisms are available for workspaces.
        
    Transcript
        there are two meanings for this term in context of the system:
        
        * transcript is a variant of gene transcription scenario; there are protein coding transcript as well as transcripts of other types
        
        * for filtering variants in :term:`workspace` datasets, the system makes distinction between applications of a variant to different affected protein coding transcripts, so a pair (variant, transcript) we call as "transcript"
        
    Viewing regime
        The user can view and study all properties of selected variants in this regime. See 
        :doc:`concepts/view` for details.
        
    Filtration
        is the main analytic mechanism providing by the system; the user determines rules of selection variants (and their transcripts) satisfying conditions for variety of properties. The subset of variants (transcripts) can be used for detailed study in :term:`viewing regime`. The user also can create :term:`secondary workspace` and continue studies of data inside it.
        
        Two filtration mechanisms are supported in the system: using :term:`filters<filter>` or 
        :term:`decision tree`
        
    Filter
        implementation of :term:`filtration` mechanism where sequence of :term:`conditions` are applied to  
        :term:`variants<variant>` (:term:`transcripts<transcript>`) one by one, in conjunctional way.
        Filters are :term:`solution items<solution item>`
        
    Filtering regime
        Regime for work with :term:`filters<filter>`, see :doc:`concepts/filters_reg`
        
    Decision tree
        implementation of :term:`filtration` where :term:`conditions` are applied to 
        :term:`variants<variant>` (:term:`transcripts<transcript>`) in form of decision tree. 
        See :doc:`concepts/dtree_syntax` for definitions.
        Decision trees are :term:`solution items<solution item>`
        
    Decision tree code
        Internal representation of decision tree is portion of code in Python dialect. 
        See :doc:`concepts/dtree_syntax`
        
    Decision tree point
        Single instruction of decision tree. Points of main types have state: set of items 
        (variants and transcripts) that correspond to this point. See :doc:`concepts/dtree_syntax`

    Decision tree state label
        Name of state for a :term:`decision tree point`. See :doc:`concepts/dtree_syntax`.
        The purpose of labels is setting proper parameters to some of complex :term:`functions`
        
    Tagging
        In :term:`workspace` context, where number of variants is not so large, the user can tag them manually. Tags are stored on the server side. See details in :doc:`rest/ws_tags`
        
    Zone
        In :term:`workspace` the user can use zone selection as an additional mechanism of filtration. 
    
    Primary dataset
        Dataset that was loaded in :term:`vault` directly. Usually it is :term:`XL-dataset` with wide variety of variants.
    
    Secondary workspace
        The user can create :term:`workspace` datasets as result of :term:`filtration` process. The typical scenario in the system is as follows. The user starts with :term:`primary dataset`, selects comparatively small subset of variants and put into secondary workspace, 
        and then this subset is ready for careful detailed manual study. The user can repeat selection procedure more than one time. 
        
    Root dataset
        For :term:`secondary workspace` it is original dataset that was loaded in :term:`vault` directly
        
    Viewing property
        Property of variant shown in :term:`viewing regime`
        
    Conditions
        Conditions on various :term:`filtering properties<filtering property>`, 
        see :doc:`rest/s_condition`.
    
    Decision tree atomic condition
    Atom
        Atomic condition for :term:`filtering property` used in :term:`decision tree point`,
        see :doc:`concepts/dtree_syntax`
        
    Filtering property
    Unit
        Property of :term:`variants<variant>` used for :doc:`concepts/filtration` purposes. 
        
    Numeric property
        :term:`Filtering property` with numeric values
    
    Enumerated property
        :term:`Filtering property` with values from a enumerated list of strings
    
    Status property
        :term:`Enumerated property` with single value
        
    Multiset property
        :term:`Enumerated property` with single value
        
    Functions
    Filtering function
        Aggregated information items that can be used in :doc:`concepts/filtration` as well
        as :term:`filtering properties<filtering property>`, in case if parameter data 
        is defined. See :doc:`rest/func_ref`.
        
    Dataset documentation
        Collection of documents in various formats attached to dataset or produced by the system
        on dataset loading or creation. Documentation on :term:`secondary workspace`
        includes references to documentation on base one.
        
    Aspect
        Representation of part of data on :term:`variant` in context of full view representation. See :doc:`concepts/view`
        
    Solution item
        Item representing some application solution useful for the user. Generalization name
        for :term:`filter`, :term:`decision tree` and some others.
        See the discussions :doc:`concepts/sol_pack` and :doc:`concepts/sol_work`.
        
    Rules
        Aggregated :term:`multiset property` that detects what :term:`decision trees<decision tree>`
        are positive on the variant. Available only in :term:`filtering regime` in 
        :doc:`concepts/ws_pg`. 
        
    Gene list
        List of genes registered in the system as :term:`solution item`
        
    Export
        Operation of creation (external) Excel document for selected variants. Selection 
        should be limited (up to 300 entries). Document is stored on server side, see
        :ref:`configuration settings<export_cfg>`.
        
    Delayed request    
        A request that needs to be complete only if the main request has returned incomplete
        information. Forms series. See details in :doc:`concepts/status_report`
    
    Background task
        The system cannot perform immediately some of tasks, so it evaluate them with some delay. Once such a tasks initiates, the client periodically call the server request :doc:`rest/job_status` whether the task is done. 
    
    Internal UI
        Is a variant of Front-End of the system that is used for deep development process of the system. It is more "primitive" than NextGen UI, however it covers the whole functionality supported by REST UI. Only Chrome and Firefox browsers are supported by Internal UI, and there are more inconveniences in usage of it. However, it is a palliative while NextGen Front-End is being developed to its proper state
    
    Anti-cache mechanism
        The internal UI uses some files (with extensions ``*.js`` and ``*.css``), and these files are
        checked out from the repository. So after a push from the repository these files can change. If
        these files were used by the UI directly, there would be a possibility that the user’s browser will
        ignore changes in such a file and use some outdated cached copy of its previous version
        instead of the fresh version of it. The workaround for this problem is to create a mirror directory,
        copy into it all the necessary files but slightly modify their names in such a way that different
        versions of the same file will have different names. See :ref:`mirror-ui configuration setting<mirror_ui>`.
        
    Annotation pipeline
        A process of preparation of :term:`primary dataset` information that thould be evaluated 
        before creation if dataset in the system. See :doc:`adm/a_adm_formats` for details.
        
    Annotated JSON files
        Result of :term:`annotation pipeline`, usually in the following formats: 
        ``*.json``, ``*.json.gz``, ``*.json.bz2``
