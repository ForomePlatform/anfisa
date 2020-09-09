Variant data presentations and aspects
======================================

The system provides wide amount of different properties concerning a 
:term:`variant`. Moreover, for different :term:`datasets<dataset>` list of properties 
and their formats can vary. So in generic context the support for accurate rendering
of the whole information about variant is heavy.

REST API supports two ways for rendering data concerning :term:`variants<variant>`:
    
* :doc:`../rest/reccnt` 
    request prepares most portion of details of rendering on the server side. 
    
    The whole variant data is split onto fixed collection of :term:`aspects<aspect>`, 
    each one is a portion of correct HTML document presentation. 
    
    The request does not have serial form of call, since information on a single variant 
    might be wide enough.
    
    HTML representation for some aspects contain active elements that might be used in 
    the Front End application for user needs. As a result, the user can hide and restore 
    columns in wide tables for transcripts and cohorts.
    
* :doc:`../rest/tab_report` 
    request has only serial form, and provides selected
    comparatively small information on variants in tabular form; 
    selection scenario are configured on 
    the server side.
    
