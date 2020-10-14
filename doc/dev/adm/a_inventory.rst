Inventory (\*.CFG) file format
==============================

.. index:: 
    inventory (*.CFG); file format

The detailed description of inventory file format is a part of :term:`annotation pipeline`
project, so here is a short description covering details important for Anfisa project:

* Main principle of inventory files usage: these files are the same for almost all datasets, so there is a generic variant of such a file. But in reality some cases might differ to each other, so there is an option to slightly modify prototype of such a file in particular case.

* Most part of information in inventory file is part of `annotation pipeline` process. The only two information portion is used in Anfisa itself: 
    
    * location of `annotation json file<annotation json files>` as main result of annotation process, as well as a main source file for dataset in Anfisa
        
    * supporting documentation for the case, in human readable formats: HTML and PNG, see the example (i.e. generic content) of inventory file, section "doc" for details. 

* Format of inventory is a JSON format with some advanced features:

    * ``//`` comments are available
    
    * macro replacement schema is supported: 
    
        * the macros ``${DIR}`` and ``${NAME}`` are  predefined, as directory path and name of inventory file itself (without extension \*.cfg) 
            
        * more macro can be defined in "aliases" section
        
        * there is special construction ``split()`` in "aliases" section that allows to split alias `${NAME}` to series of other aliases
            
        * this logic allows us to have just the same content of inventory files for all datasets, and vary only names of inventory files 
        
Example of inventory file
*************************

::

 {
    "aliases": {
        "CASE,PLATFORM,PROJECT": "split('${NAME}', '_')"
    },
    "name": "${NAME}",
    "case": "${CASE}",
    "assembly": "GRCh37",
    "platform": "${PLATFORM}",
    "config": "${DIR}/config.json",
    "fam": "${DIR}/${CASE}.fam",
    "patient-ids": "${DIR}/samples-${CASE}.csv",
    "vcf": "${DIR}/${NAME}.vcf",
    "vep-json": "${DIR}/${NAME}.vep.json",    
    "anno-log": "${DIR}/annotations-${TS}.log",
    "a-json": "${DIR}/${CASE}_anfisa.json.gz",
    "docs": [
        {
            "source": "${DIR}/docs/notes.html",
            "kind": "html", 
            "title": "Anamnesis"
        },
        {
            "source": "${DIR}/docs/pedigree.png",
                    "kind": "png",
            "dest": "pedigree.html",
                    "title": "Pedigree"

        },
        {
            "source": "${DIR}/docs/fulldoc.html",
            "kind": "html", 
            "title": "Full documentation"
        }
    ]    
 }

See also
--------
:doc:`a_adm_formats`
