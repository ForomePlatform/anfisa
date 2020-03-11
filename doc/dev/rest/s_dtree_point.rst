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


