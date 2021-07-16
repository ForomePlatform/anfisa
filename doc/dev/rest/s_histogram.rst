Histogram descriptor for numeric fields
=======================================

.. index:: 
    Histogram descriptor; data structure

Format
------

| ``[`` 
|       **[0]**: histogram type: ``"LIN"`` or ``"LOG"``
|       **[1]**: minimal bound, *numeric*
|       **[2]**: maximal bound, *numeric*
|       **[3]**: *list of numeric* counts
| ``]``

Description
-----------

Histogram is evaluated for any numeric field as a part of :doc:`s_prop_stat`. The structure is optional: it is replaced by null if there is no meaningful histogram in evaluation.

The meaning of histogram: diapason of values is split onto series of intervals, and the integer count for interval corresponds to counts of values that are located in this interval. In case of :term:`XL-datasets<XL-dataset>` histograms are some approximation of strict values distribution, so this value can be not an integer but float. 

In a generic case, histogram splits interval of values onto 10 intervals (count of "bins"): 8 intermediate are of "equal length", and two sided are "infinite" . 

By definition, sum of counts in list equals (in case of :term:`XL-datasets<XL-dataset>` approximately) to count of records in selected set of :term:`variants<variant>`, see :doc:`../concepts/ws_pg` for details). 

Features of histogram for a :term:`numeric property` depends on settings for this property: 

    * if this property has either "logarithmic" or "linear" meaning: ``"LOG"`` or ``"LIN"`` mode is used

    * if this property is based on either integer or or float type, it determines details of histogram evaluation
    
    
* In case of ``"LIN"`` mode, linear scale for values is used:

    - Minimal and maximal bounds are equal to minimal and maximal values in :doc:`s_prop_stat`
    
    - All intermediate intervals of histogram have equal width

    - Histogram can be short in case of integer field and low difference between minimal and maximal bounds
    
* In case of ``"LOG"`` mode, base-10 logarithmic scale is used:

    - Minimal and maximal bounds in descriptor are integers and have meaning of 10-power for field values: power bound *p* corresponds to interval [10\ :sup:`p`, 10\ :sup:`p+1`)
    
    - Any intermediate (and upper final) interval counts values with the same integer power of 10:
    
    |              0: [1, 10),  2: [100, 1000), -2: [.01, .1), etc.
    
    - Histogram is not evaluated (set to null) if there is only one interval in it
    
    - In pure mathematical interpretation there is no place for "too low values" in the logarithmic scale: for 0 or even -1 values. But the data does contain these values, so the first low count on the histogram registers all these exceptional values below 10\ :sup:`p+1` where *p* is low power bound of histogram. 
    
    - Presence of exceptional, "too low" values is an important issue for the final user understanding of histogram, so it should be visible in the User Interface. This presence can be detected by comparison of the low bound of values from :doc:`s_prop_stat` with 10\ :sup:`p`, where *p* is low power bound in histogram descriptor(**[1]**, second item in the descriptor). 
    
    - In case of integer field the low power bound can be -1, it means that exceptional "too low" values happen. Otherwise low power bound is 0 or more.
    
    - In case of float field,  exceptional "too low" value is any one lower than 10\ :sup:`-15`, and in case of presence of these values the low power bound is set to -16. It is common in this case that histogram count list starts with positive first count and then a series of zero counts follows. The User Interface can visualize somehow count of exceptional values, mark them as exceptional, and ignore visualization of the following zeros. 
