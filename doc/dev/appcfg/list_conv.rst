List conversion mechanism
=========================

The mechanism discussed here supports conversions of data objects in JSON presentation. The description of conversion itself has JSON representation in form of array. Items of this array is either strings or list of strings. So in this form one can describe an extended variety of transformations.

Conversion is realized as chain of transformations, any transformation gets an object as input and returns transformed data, and so on.

Input object for any transformation functions listed below is a list. It is natural, since the mechanism is used with integration with :ref:`path selection<json_path_loc>` Ordinary transformation function returns list also, but some final transformations can return other type of objects, fro example **min**, **max** and **len** return numeric values.

Conversion mechanism can use registry of named functions, instance of class ``FilterPrepareSetH`` used in :doc:`flt_schema_py` is such a registry.

*Comment*. This proprietary mechanism was developed for the following useful universal feature. Using it, one can define logic of conversions, store them in JSON format, and reactivate this logic later in other environment (up to the same functions in function registry). In context of the system, this feature is used on :doc:`derivation of dataset<../rest/ds2ws>` operation.

Tranformations without parameters
---------------------------------

Transformation function can have no parameter, and its JSON representation is just *string* with name of transformation.

* **len** - return length of list

* **min** / **max** 
    return minimum/maximum of values in list
    input list should consist of numeric values

* **values** / **keys** 
    return joined list of values/keys of dictionaries
    input list should consist of dictionaries

* **clear**
    return clear variant of input list, without empty entries, all items are stripped of leading and trailing spaces 
    input list should be list of strings

* **uniq**
    return sorted list of values without duplication
    input list should be list of strings
    
* **positive** / **negative**
    return filtered list, for **positive** all null/zero/empty values are filtered out, reverse for **negative** 

* <named function>
    any named function from function registry can be used as transformation, make sure this function has one input parameter of list type

Transformations with parameters
-------------------------------

Transformation function can have parameters, and its JSON representation is list: the first item is  *string* with name of transformation, then parameter(s) follow. In the current version of the system only single parameter transformations are supported.
    
* ``[`` **property**, *name* ``]``
    the transformation retrieves property *name* from each item in input list, and so forms output list
    input list should consist of dictionaries
    
* ``[`` **skip**, *delta* ``]``
    the transformation drops leading *delta* items from input list
    
* ``[`` **split**, *separator* ``]``
    the transformation splits each input item by *separator* string on chunks, and forms output list as collection of all chunks
    input list should consist of dictionaries

* ``[`` **split_re**, *pattern* ``]``
    the same as previous, but *pattern* is interpreted as regular expression definition

* ``[`` **filter**, *named function name* ``]``
    the transformation filers input list and keeps only items that are positive for function that is registered in function registry; make sure this function returns boolean
    
* ``[`` **max**, *default* ``]`` /  ``[`` **min**, *default* ``]``
    variants of transformations **min** / **max** but with default value if list is empty or null.

Examples
--------
    
Simple evaluation of length of list: ::

    conversion = ["len"]  # evaluates length of list
    
Evaluation of count for items in list having property "genotype_quality", with skip of first item: ::

    conversion = [
        ["skip", 1],
        ["property", "genotype_quality"],
        "negative", "len"]

Split input text fragments by comma, clear empty entries and duplication: ::

    conversion = ["values", ["split", ','], "clear", "uniq"]        
    
See also
--------

:doc:`flt_schema_py`
