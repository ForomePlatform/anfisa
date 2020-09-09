Solution items
==============

Solution items are configurable objects that used by the user in work with system. 
In the current version of the system we support the following kinds of them:
    
    * items with open control, can be pre-set or dynamical
        
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

See also
--------
:doc:`sol_work`
