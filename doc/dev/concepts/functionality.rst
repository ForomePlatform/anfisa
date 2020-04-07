Functionality structure
=======================

Work pages of the system
------------------------
    
    The system supports four type of work pages with the following 
    functionality block distribution

.. _work_pages:

    * :term:`Workspace` main work page, see :doc:`ws_pg` for details:
    
        - :ref:`Full viewing regime<full_viewing_regime>`
 
        - :doc:`filters_reg`

            - :doc:`status_report`
            
            - support :term:`filters<filter>` as :doc:`sol_work`
            
        - :term:`zone` panel
        
        - :term:`tagging`
        
        - :term:`secondary workspace` creation, :term:`export`
        
    * :term:`XL-dataset` main work page:
    
        - :term:`filtering<filter>` regime (as main regime of the page)
        
            - :doc:`status_report`
            
            - support :term:`filters<filter>` as :doc:`sol_work`
            
        - :ref:`auxiliary viewing regime<auxiliary_viewing_regime>`
        
        - :term:`secondary workspace` creation, :term:`export`

        
    * :doc:`dtree_pg` (for both :term:`workspaces<workspace>` 
        and :term:`XL-datasets<xl-dataset>`):

        - decision tree representation
        
        - interactive decision tree modification
        
        - :term:`decision tree code` modification
        
        - :doc:`status_report` and :ref:`Decision tree points report<dtree_points_report>`
        
        - support :term:`decision trees<decision tree>` as :doc:`sol_work`
        
        - :ref:`auxiliary viewing regime<auxiliary_viewing_regime>`
        
        - :term:`secondary workspace` creation
        
    * :term:`Dataset documentation` page


Discussion
----------

The user interface in system system provides currently 4 types of pages.
Each kind of page provides specific part of the whole functionality
of the system.

:doc:`ws_pg` is the most complex type of pages. It supports 
:ref:`full variant of viewing regime<full_viewing_regime>`, complete panel for 
:term:`filters<filter>` works, and all the functionality 
specific for workspaces: :term:`zones<zone>` and :term:`tagging`.

:term:`XL-dataset` main page is essentially simpler than workspace 
one. Base regime here is :term:`filters<filter>` works. :term:`Viewing regime`
here is :ref:`auxiliary one<auxiliary_viewing_regime>`: the user can view only 
small selections of variants. 

:doc:`dtree_pg` maintain complex functionality in a special 
way: modification of decision tree can be made by various ways, in interactive
scenario as well as in direct code edit process. 

    :doc:`status_report` in this page applies to a bunch of different selections, 
    since decision tree have many selection points.

    :ref:`Auxiliary viewing regime<auxiliary_viewing_regime>` is supported here
    as well for all selection points.

All main and decision tree pages for dataset support creation of 
:term:`secondary workspaces<secondary workspace>`. Only main pages for dataset
support export functionality.

:term:`Dataset documentation` is available in separate documentation page.
It includes report for loading or creation of dataset and possibly bunch of
documents in different formats come from annotation process.

For :term:`secondary workspace` it includes reference to documentation on
base dataset. 

