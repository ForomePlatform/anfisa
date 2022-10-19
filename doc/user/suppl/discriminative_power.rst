.. _discriminative_power:

Discriminative Power specification
==================================

This document describes an algorithm of Discriminative Power calculation.

Formulation of the problem
--------------------------
As was said in the filters description, the **Discriminative power** is a special numeric characteristic
use to indicate the “Effectivity” of a filter.
This means that "Effective" filter can split the current set of variants
on the the most strongly differing groups, e.g. with loss maximum of “entropy”.

As a possibility, we can use here evaluation of plain proper entropy, but it is not so helpful if the set of
variants is wide (up to millions). So we evaluate some entropy-like product instead of proper entropy,
and below is the description of the procedure.

Procedure of evaluation
-----------------------
For each property we start from property status data, and form list of numeric (positive integer) values,
one integer for each of “choices”:

* For numeric property we have histogram of values, use this as “list of choices”

* For enumerated property we have count of each value - use this as base list for “list of choices”, and take in account “total count”, that equals to the filtered-counts of variants (or transcripts, in some cases)
    * For status property the sum of values in the base list equals to the total count, the base list is the final
    * If the sum of values in the base list is less than total count, append the difference to the base list, otherwise use the base one as it

**Note**: The procedure is rough, so we ignore (up to now) specifics of multivalued enumerated properties with wide overlap.
With use of “list of choices” we evaluate Discriminative Power by the following procedure (in JavaScript language):


..  code-block:: JavaScript
    :caption: Discriminative power calculation

    function entropyReport(counts) {
        var total = 0.;
        for (j = 0; j < counts.length; j++) {
            total += counts[j]
        }
        if (total < 3)
                return -1;
        var sum_e = 0.;
        var cnt = 0;
        for (j = 0; j < counts.length; j++) {
                if (counts[j] == 0)
                    continue;
                cnt++;
                quote = counts[j] /total
                sum_e -= quote * Math.log2(quote);
        }
        var norm_e = sum_e / Math.log2 (total);
        var divisor = reduceTotal(counts.length)
        var pp = norm_e / divisor;
        return Math.min(1.0, pp);
    }
    /*************************************/
    function reduceTotal(total) {
        if (total < 10)
            // for N < 10; easy to select
            return 0.3 + 0.02 * (total);
        if (total < 25)
            // for N < 25; still possible to view all values together on one page
            return 0.5 + (total - 10) / 15;
        if (total < 125)
            // for N < 125; easy to scroll
            return 2 + Math.sqrt(total - 25) / 5;
        if (total < 625)
            // for N < 625; still possible to scroll
            return 4 + (total - 125) / 100;
        if (total < 3125)
            // for N < 3125; difficult to scroll, exact N no longer matters
            return 9 + (total - 625) / 200;
        // for N >= 3125; visual selection
        return 21.5;
    }
