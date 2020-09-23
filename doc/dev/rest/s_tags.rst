Tags descriptor
===============

.. index:: 
    Tags descriptor; data structure

Format
------

| ``[`` *list* of tag` descriptors
|      ``[``
|           **[0]**: tag name
|           **[1]**: value, **string** or ``true``
|       ``]``, ...
| ``]``

Description
-----------

The structure is just list of :term:`tags<tagging>` set for a variant.

For "text" tags (and special tag ``_note``) the value is **string**.

For "check-box" tags value is *boolean* but if this value is ``false`` just drop this descriptor out of list.

The structure is used in request :doc:`ws_tags` as return property. The same structure (in string JSON representation) can be used as modifying argument of request.

See also
--------
:doc:`ws_tags`
