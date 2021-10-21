csv_export
==========
        **Export to CSV format operation**
        
.. index:: 
    csv_export; request
    
Synopsis
--------
**csv_export** 

    **Arguments**: 
    
        **ds**: dataset name
        
        **filter**: *optional* name of applying filter
        
        **conditions**: *optional* list of applying :doc:`condition descriptors<s_condition>`
            *in JSON string representation*

        **zone**: *optional* :
        
        | ``[`` list of zone settings
        |       ``[``
        |             **[0]**:  zone name, *string*
        |             **[1]**:  ``[`` variants ``]``, *list of strings*
        |             **[2]**:  false, *add it if negation of condition is required*
        |        ``]``, ...
        | ``]``  *in JSON string representation*

        **schema**: name of data schema
        
        .. index:: 
            schema; argument of csv_export        

    **Returns**: 
    
    Page in CSV format for download
    
Description
-----------
The request creates presentation of selected variants in CSV format. 

This method is not a proper REST API call: it does not return a JSON object but file in CSV format.

Selection is defined by:

    - :term:`filter` applies if either **filter** or **conditions** is set (see discussion :ref:`here<fiter_conditions>`)

    - :term:`zone` applies if **zone** is set - actual for :term:`workspaces<workspace>` only (see :doc:`ws_list` for details).

In current version of the system schemes are defined in source code of the server as :term:`solution items<solution item>`, so the list of it is fixed. The schema `csv` is supported for simple variant of export. 

Export operations, this and :doc:`export` evaluate properly only a limited lists of records. The upper limit of coumt is visible in :doc:`dataset descriptor<s_ds_descr>` as **export-max-count** property. In current settings this limit affects only for XL-datasets, since it equal to maximal size of WS-dataset. The User Interface needs to control this limit (or more low one) and disallow attemts of the final user to perform export operation over too long list of variants.

Available schemes in current version:

  =================    ==================================
   demo                 gene(s), variant, gnomAD_AF
  -----------------    ----------------------------------
   csv                  chromosome, variant:
                            (chromosome|start|ref|alt)
  -----------------    ----------------------------------
   xbr                  
                        ClinVar
                        HGMD
                        Coordinate
                        Change
                        MSQ
                        Protein Change
                        Polyphen2_HVAR
                        Polyphen2_HDIV
                        SIFT
                        MUT TASTER
                        FATHMM
                        gnomAD_Overall_AF
                        gnomAD_Overall_AF_Popmax
                        gnomAD_Genomes_AF
                        gnomAD_Exomes_AF
                        gnomAD_Overall_Hom
                        gnomAD_Overall_Hem
                        QD
                        FT
                        ColorCode
                        GTEx
                        IGV
                        gnomAD
                        Samples
                        GeneColored
  =================    ==================================

.. warning:: List of schemes: move it to user documentation 
  
See also
--------
:doc:`export`     

