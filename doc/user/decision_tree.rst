**************
Decision Tree
**************

The Decision tree is an advances method of variations filtering.
It allows very powerful and flexible way to refine variations set and create new derives sets.

How Decision Tree works
=======================
On the first glance, the Decision Tree is very similar to **Filter Refiner** functionality.
This if a sequence of a filters, each of them filters variation by the specific condition.
each filter separates variations in two groups:

* Variations which pass filter
* Variations which not pass filter

However, the **Filter Refiner** has very straightforward hardcoded logic:

* Variations, *not passing* the filter are *excluded* from the analysis
* Variations, *passing* the filter goes to subsequent filters

In **Decision tree** we have more flexible options:

* For variations, *passing* the filter we can select what we can do:
    * Exclude variations form the subsequent analysis
    * Include variations in the final data set
* Variations, *not passing* the filter goes to subsequent analysis.

At the final step we can decide what to do with rest of variations.

In fact, the  **Filter Refiner** is in fact just a simple version of a decision tree,
where at each step we exclude variations, not passing the filter,
and on the final step including all variations to final data set.


Decision tree interface usage
=============================

To start variations filtering by Decision Tree* user should select **Whole genome/exome** and then
**Build inclusion/exclusion criteria** option.
After this, the Decision tree window opens.
Alternatively, user can switch between **Decision tree** and **Filter Refiner** modes
by the combo box, next to Forome logo.

.. image:: pics/decision-tree.png
  :width: 800
  :alt: Decision tree main window

The **Decision tree** main window is similar to **Filter Refiner**.
On the left panel user can see the list of the filters, same as for **Filter Refiner**.
By clicking on the filter user can see the filter properties in the pop-up window.

After pressing the *Add attribute* button the variations is added to the **Results** panel.

