**************
Filter refiner
**************

To start variations filtering by *Filter* refiner user should select **Whole genome/exome** and then
**Explore data or build new filter** option.
After this, the filter refiner window opens.

.. image:: pics/filter-refiner.png
  :width: 800
  :alt: Filter refiner main window

Main Filter refiner window
==========================

The Anfisa Filter refiner provides for the user the large set of available filters, defined by different
variation properties in ibintial VCF file.
It allows to apply to a dataser combinations of filters,
and each additional filter operates on the result output of the previous filtering.
The consequent application of different filters results only in conjunctions of the conditions.
By clicking on the each filter user can see the filter settings and details

All list of available filters with descriptions are available on the separate page:
TODO:add link

By operation types all filters can be divided into two groups:

* Categorical
* Numeric

Categorical filters
-------------------
Categorical data entries are presented by list of filtering categories.
On the filter details page AnFiSA shows histogram or pie chart of categories distribution
User can select/deselect categories from the list.

.. image:: pics/filter-refinement_filter-zygosity.png
  :width: 800
  :alt: Categorical filter example

Only variants from selected categories will go to subsequent analysis.
The **Not Mode** inverts the variations selection.

Numeric filters
-------------------
The numeric filters allows user to filter variations by the value of some numerical parameter.
On the filter details page AnFiSA shows histogram of value distribution.
The distribution histogram is displayed in linear or logarithmic scale.
The display mode is pre-configured for filter and can't be changed by user.

.. image:: pics/filter-refinement_filter-AF.png
  :width: 800
  :alt: Numeric filter example

User can select value range to pass visually on the histogram or by typing the numeric values.
The buttons "<" and "<=" next to data entry edits controls incluson/exclusion of the border values.

Filter chain creation
=====================
After setting filtering options for the filter user applies it by pressing the **Add condition** button
on th filter details page.
After pressing this button, new filter will be added to the list of filters on the right panel **Results**.

Also AnFiSA displays the number of variants passing filter chain next to the panel caption:
"*Variants: 837*"

On the **Results** panel user can see all active filters, view and change filter settings.
After filter settings change user need to press **Save changes** button to apply it.
User can continue refinement process and add new filter to narrow the variations set.

Filtering notes
---------------
Each new filter is applied to the **already filtered** variations set.
Therefore adding each new filter will lead to narrowing of the variation set.
To achieve more flexible filtering one should use **Decision tree** capability.

All charts in the filter details panel also displays the statistics for variations filed by previous filters,
no for original variations set.

All "regular" filters available in the filter refinement page are commutative:
they can be applied in any order and will produce the same result.
This is the requirement of all OLAP data analysis platforms.
Support of non-commutative operations is much more complicated and described in the separate section
"Notes on Zygosity"













