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
-------------------------

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

Documentation block of inventory file
-------------------------------------

Property **docs** of inventory descriptor is list of objects that represent documentation items. 

Common properties of documentation items:

* **"kind"** - kind of item, see details below

* **"title"** - title of item visible for the user

* **"source"** - path to location of file/files corresponding to the item, can contain template control symbols ``*``, for some item kinds should match only one file

* **"dest"** - destination filename, for some item kinds is optional, in these cases base filename of **source** is used

*Common rule*: if there is no file / directory that is defined by **"source"** property, the documentation item is just ignored. 

Kinds of documentation items
****************************

* kind = **"group"**

    Represents group (folder) of documentation items located in subdirectory. Descriptor should contain property **"docs"** with recursive list of sub-items of variour kinds. It is not recommended to define **"dest"** property explicitly.

* kind = **"html"**

    Represents document in HTML format. (Use "support" documentation item to use images inside document, see below). 
    **"source"** should define a single document with ``.html`` extension. 
    It is not recommended to define **"dest"** property explicitly.
    
* kind = **"txt"**, kind = **"png"**, kind = **"jpg"**

    Represents HTML document visible for the user with contents of file of text or image format.
    **"source"** should define a single document with corresponding extension. 
    **"dest"** property should be explicitly defined as a filename with ``.html`` extension
    
    For image files the additional property **"tooltip"** can be used, with text description of the image
    
* kind = **"*.txt"**, kind = **"*.png"**, kind = **"*.jpg"**

    Represents single HTML document with contents of serie of files. 
    **"source"** should define this serie. 
    **"dest"** property should be explicitly defined as a filename with ``.html`` extension
    
* kind = **"support"**

    Represents subdirectory with supplementaty images. These images can be referenced inside HTML-documents and are invisible for the user on documentation tree. 
    For this special kind of documentation item only **"kind"** and **"source**" properties should be defined, and **"source"** should be path to a subdirectory

See also
--------
:doc:`a_adm_formats`
