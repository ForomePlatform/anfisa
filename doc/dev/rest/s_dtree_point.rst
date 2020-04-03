Decision Tree Point descriptor
==============================

Format
------

| ``{`` *dictionary*, 
|        "**kind**": kind of point, 
|                          ``"If"``, ``"Return"``, "``"Label"`` *or* ``"Error"``
|        "**level**": level of point, ``0`` *or* ``1``
|        "**decision**": decision of point, *boolean* or ``null``
|        "**code-frag**": HTML-presentation of code, *string*
|        "**actions**: actions applicable to point, ``[`` *list of strings* ``]``
| ``}`` 


Description
-----------

The data represents information for counts of :term:`variants<variant>`, and in case of
:term:`ws-dataset` of :term:`transcripts<transcript>` also.
        
If point is not applicable for counting, data is  ``0``.

If evaluation of counts is incomplete, data is ``null``.

See :ref:`list of INSTR actions<dtree_instr_actions>`

Used in request
----------------
:doc:`dtree_set`
