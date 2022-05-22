symbol_info
===========
        **Symbol information**

.. index:: 
    symbol_info; request

Synopsis
--------

**symbol_info** 

    **Arguments**: 

        **ds**: dataset name
        
        **tp**: symbol type (only ``Symbol`` is supported currently)
        
        **symbol**: symbol
        
    **Return value**: 


| ``{`` *dictionary* 
|       "**_id**":  *string*, name of symbol
|       "**hgnc**": *optional dictionary of strings*, information from HGNC
|       "**gtf**": *optional dictionary of strings*, information from GTF/Ensembl
|       "**gtf-refs**": *optional list of strings*, recommended replacement from GTF nomenclature
| ``}``


Description
-----------

The request returns information on symbol known to the system. The information obtained from two sources: HGNC and Ensembl. (Versions of sources for symbol database can be learn by :doc:`symbols` request)


**gtf-refs** is summary of aliases and previous namings that correspond to the symbol according to HGNC information and present in GTF/Ensembl nomenclature


See also
--------
:doc:`symbols`
