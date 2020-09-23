Variant data presentations and aspects
======================================

The system provides wide amount of different properties concerning a :term:`variant`. Moreover, for different :term:`datasets<dataset>` list of properties and their formats can vary. So in generic context the support for accurate rendering of the whole information about variant is heavy.

REST API supports two ways for rendering data concerning :term:`variants<variant>`:
    
* **Full data view presentation**: :doc:`../rest/reccnt` request prepares most portion of details of rendering on the server side. 
    
    The whole variant data is split onto fixed collection of :term:`aspects<aspect>`, each one is a portion of correct HTML document presentation. 
    
    The request does not have serial form of call, since information on a single variant might be wide enough.
    
    HTML representation for some aspects contain active elements that might be used in the Front End application for user needs. As a result, the user can hide and restore columns in wide tables for transcripts and cohorts.

.. _accurate_vs_technical:
                
    In informal way presentation of data in viewing regime is split onto two parts: "accurate" and "technical". Data from the first "accurate" part is represented in a fotm that is (comparatively) good for read and understand. Data from "technical" part might be represented with technical markup in a form difficult to read.

    Both accurate and technical parts of data are split onto :term:`aspects<aspect>`. Each aspect (but very technical one "VCF") has representation form of table. Most aspects represent in two column table: one for name, one for value. Other aspects are multicolumn: one column for name and numerous columns for values.    
    
    For more details about aspects see :doc:`../appcfg/view_schema_py`
    
.. _tabular_view:
    
* **Tabular partial view presentation**: :doc:`../rest/tab_report` 

    Request has only serial form, and provides selected comparatively small information on variants in tabular form; selection scenario are configured on the server side.
    
