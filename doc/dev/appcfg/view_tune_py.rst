Tuning viewing schema API
=========================

.. index:: 
    Tuning of viewing schema API

There is strong need to pre-process some data attributes that are originally stored in :term:`annotated JSON file` in runtime on stage of :doc:`data presentation<../concepts/view_pre>` in :term:`viewing regime`:

* it is subject of essential storage economy, since some extended technical fragments of a text may duplicate in million times for :term:`XL-datasets<xl-dataset>`

* there are plans in perspective to provide for the user graphical presentation and animation of some data portions 

So the system provides mechanism for such manipulations, and here we explain application of this API in the source file

``app/config/view_schema.py``
    
::

    def _resetupAttr(aspect_h, attr_h):
        ...
            
    class AttrH:
        def __init__(self, name, kind = None, title = None,
                is_seq = False, tooltip = None):
            ...
        def htmlRepr(self, obj, v_context):
            ...
    
The mechanism is as follows:

    * to define a sub-class over AttrH to redefine method ``htmlRepr()`` with some special logic:   
    
        * argument **obj** refers to top aspect data object
        
        * argument **v_context** refers to the whole annotation JSON variant record 
        
        * (so **obj** argument is not strongly necessary, since it is inside **v_context**, however **obj** is most convenient for the most part of application cases)
    
    * on tuning of view schema: to replace placeholder attribute to instance of attribute of the developed sub-class
    
The main rule of replacement: placeholder attribute name (identifier) must contain CAPITAL letters, and attribute instance to replace it must have name (identifier) as lowercase variant of the same name.
    
See also
--------

:doc:`view_schema_py`

:doc:`code_config`
