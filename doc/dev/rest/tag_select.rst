tag_select
==========

Synopsis
--------

.. index:: 
    tag_select; request

**tag_select** 

    **Arguments**: 

        **ds**: dataset name
        
        .. index:: 
            tag; argument of tag_select
            
        **tag**: *optional* tag name
        
    **Return value**: 

        | ``{`` *dictionary*
        |       "**tag-list**": all tags available, ``[`` *list of string* ``]``
        |       "**tag**": value of **tag** argument , *optional string*
        |       "**tags-version**": indicator of tags update state
        |       "**records**": affected variants, ``[`` *list of int* ``]``
        | ``}``
        
Description
-----------

The request affects only :term:`workspaces<workspace>` and is principal one 
for: 

    * marking variant records having tags
    
    * tag navigation

Property **tags-version** is the same as in request :doc:ws_tags, see 
discussion :ref:`here<tags_version>`.

**tags-list** contains all tags available in dataset, both "check-box" and "text" ones 
(in :term:`root dataset`), see details in description of :doc:`ws_tags`. 
    
If **tag** is set, **records** contains ordering numbers for variants having this tag.

Otherwise **records** contains ordering numbers of all variants having any tag, 
ant this information is useful for marking these variants. (Note that marking information
can change outside the client session)

See also
--------
:doc:`ws_tags`
