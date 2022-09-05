@api
Feature: Check dtree_set [POST] request

    @progress
    Scenario Outline: Set empty dtree for any xl dataset by code
    Given "xl Dataset" is uploaded and processed by the system
    When dtree_set request with correct "<ds>" and "<code>" parameters is send
    Then response status should be "200" OK
    #And response body schema should be valid by "dtree_set_schema"
    #And response body "point" dtree_point_descriptor schemas should be valid
    #And response body "dtree-list" solution_entry schemas should be valid
    #And response body "cond-atoms" condition_descriptor schemas should be valid

    Examples:
    | ds         | code                   |
    | xl Dataset | generated complex code |

