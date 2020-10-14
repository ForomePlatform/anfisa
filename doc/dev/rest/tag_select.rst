tag_select
==========
        **Tag navigation support**

.. index:: 
    tag_select; request

Synopsis
--------

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
        |       "**tags-state**": indicator of tags update state
        |       "**tag-rec-list**": *optional* affected variants, ``[`` *list of int* ``]``
        |       "**tags-rec-list**": all tagged variants, ``[`` *list of int* ``]``
        | ``}``
        
Description
-----------
The request affects only :term:`workspaces<workspace>` and is principal one for: 

* marking variant records having tags

* tag navigation

Property **tags-state** is the same as in request :doc:ws_tags, see discussion :ref:`here<tags_state>`.

**tags-list** contains all tags available in dataset, both "check-box" and "text" ones (in :term:`root dataset`), see details in description of :doc:`ws_tags`. 
    
If **tag** is set, **tag-rec-list** contains ordering numbers for variants having this tag.

**tags-rec-list** contains ordering numbers of all variants having any tag, ant this information is useful for marking these variants. (Note that marking information can change outside the client session)

See also
--------
:doc:`ws_tags`

:doc:`../concepts/ws_pg`
