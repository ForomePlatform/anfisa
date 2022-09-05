@api
Feature: Check dtree_set [POST] request

    @positive
    Scenario Outline: Set dtree for any xl dataset by code
    Given "xl Dataset" is uploaded and processed by the system
    When dtree_set request with correct "<ds>" and "<code>" parameters is send
    Then response status should be "200" OK
    And response body "kind" should be equal "xl"
    And response body "code" should be equal "<code>"
    And response body "eval-status" should be equal "ok"
    And response body schema should be valid by "dtree_set_schema"
    And response body "dtree-list" "solution_entry" schemas should be valid
    And response body "points" "dtree_point_descriptor" schemas should be valid
    And response body "cond-atoms" condition_descriptor schemas should be valid

    Examples:
    | ds         | code                   |
    | xl Dataset | return False           |
    | xl Dataset | generated complex code |


    @positive
    Scenario Outline: Set dtree for any xl dataset by code
    Given "xl_PGP3140_wgs_NIST-3_3_2" is uploaded and processed by the system
    When dtree_set request with correct "<ds>" and "<code>" parameters is send
    Then response status should be "200" OK
    And response body json should match expected data for "dtree-set" request

    Examples:
    | ds         | code                   |
    | xl Dataset | generated complex code |


    @progress
    Scenario: Create dtree for any xl dataset by code
    Given "xl Dataset" is uploaded and processed by the system
    When dtree_set request with correct "<ds>" and "<code>" parameters is send
    Then response status should be "200" OK
