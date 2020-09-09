ws_tags
=======
        **Tagging variant information retrieval and modifications**

Synopsis
--------

    .. index:: 
        ws_tags; request


    **Arguments**: 

        **ds**: dataset name
        
        .. index:: 
            rec; argument of ws_tags

        **rec**: variant record ordering number, *int*
    
        .. index:: 
            tags; argument of ws_tags

        **tags**: *optional modifier* :doc:`s_tags`
             *in JSON string representation*
            
    **Return value**: 
    
    |  ``{`` *dictionary*
    |       "**filters**":  filters active for variant
    |           ``[`` *list of strings* ``]``
    |       "**check-tags**": all available "check-box" tags
    |           ``[`` *list of strings* ``]``
    |       "**op-tags**": all available "text" tags
    |           ``[`` *list of strings* ``]``
    |       "**rec-tags**": tags of variant, :doc:`s_tags`
    |       "**upd-time**: *optional* time of last tags update, 
    |                        *string, time in ISO format*
    |       "**upd-from**: *optional* dataset name of last tags update, 
    |                        *string*
    |       "**tags-state**": indicator of tags update state
    | ``}``

Description
-----------

The request affects only :term:`workspaces<workspace>` and is principal one 
for rendering and modifications of variant tagging.

Tagging mechanism in the system organized by the following principles

    * The user can mark any variant in :term:`workspace` with tags
    
    * Any tag is identified by its name and probably has some value
    
    * Preset list of tags are interpreted as check-box tags, value for such 
        tags is *boolean*, by default *false*
        
      (The client receives this information in returning property **check-tags**)
        
    * Special tag has name ``"_note"``. This tag is associated with variant 
        if and only if value of it is nonempty text
        
    * Other tags are interpreted as "text" tags, he user can mark variants
        by this tag of this kind with text value, and text value can be empty
        
    * Name of any tag (but ``"_note"``) must start with any letter ("alpha") 
        symbol (any alphabet) and must not contain spaces; in terms of Java Script 
        the criterium is as follows:
    
        ::
        
            /^\S+$/u.test(name) && (name[0].toLowerCase() != name[0].toUpperCase())

    * Tags of variant is common between presences of variant in all datasets produced 
        from the same :term:`root dataset`. So the system controls state of tagging values 
        for all variants of root dataset, and traces where and when last modification of 
        this common state was made. Information about this state can be changed outside
        the client session. The client receives this information in properties:

            .. _tags_state:
        
            * **tags-state**
                Is some internal indicator value, *int* or *string*; if tag state 
                is changing this indicator changes with it
                
            * **upd-time**, **upd-from**
                Information when and from what workspace the tag state changed
            
            * **op-tags** 
                is just list of all "text" tags available; this information can also 
                change with tag state

    Tag structure modifications are performed by the following scenario: 
    
        - The client receives tags structure for variant in **rec_tags** property
        
        - The client modifies this structure
        
        - The client sends the modified copy as argument **tags** of the request
                
See also
--------
:doc:`tag_select`, :doc:`macro_tagging`
