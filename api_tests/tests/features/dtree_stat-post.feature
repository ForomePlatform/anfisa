@api
Feature: Check dtree_stat [POST] request

    @positive
    Scenario Outline: Get attributes for any xl dataset's dtree by code
    Given xl Dataset is uploaded and processed by the system
    When dtree_stat request with <ds>, <code>, <no> and <tm> parameters is send
    Then response status should be 200 OK
    And response body schema should be valid by "dtree_stat_schema"
    And response body stat-list schemas should be valid
    And response body functions schemas should be valid

        Examples:
        | ds         | code         | no | tm |
        | xl Dataset | return False | 0  | 0  |


    @progress
    Scenario Outline: Get attributes for specific xl dataset's dtree by code
    Given xl_PGP3140_wgs_NIST-3_3_2 is uploaded and processed by the system
    When dtree_stat request with <ds>, <code>, <no> and <tm> parameters is send
    Then response status should be 200 OK
    And response body json should match expected data for dtree_stat request


        Examples:
        | ds         | code         | no | tm |
        | xl Dataset | return False | 0  | 0  |


    @negative
    Scenario Outline: Fail to get attributes for any xl dataset's dtree by code
    Given xl Dataset is uploaded and processed by the system
    When dtree_stat request with <ds>, <no> and <tm> parameters is send
    Then response status should be 403 Forbidden

        Examples:
        | ds                     | no                     | tm |
        | generated empty string | 0                      | 0  |
        | xl Dataset             | generated empty string | 0  |