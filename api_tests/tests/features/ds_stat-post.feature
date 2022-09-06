@api
Feature: Check DsStat [POST] request

    @positive
    Scenario Outline: Return full information about any dataset (no filters applied)
    Given "<dataset>" is uploaded and processed by the system
    When ds_stat request with correct "ds" parameter is send
    Then response status should be "200" OK
    And response body schema should be valid by "ds_stat_schema"
    And response body "stat-list" property_status schemas should be valid
    And response body "functions" property_status schemas should be valid
    And response body "filter-list" "solution_entry" schemas should be valid
    And response body "total-counts" value should be equal "filtered-counts"

        Examples:
        | dataset    |
        | ws Dataset |
        | xl Dataset |


    @negative
    Scenario Outline: Fail to return information about any xl dataset
    Given "xl Dataset" is uploaded and processed by the system
    When ds_stat request with incorrect "<ds>" parameter is send
    Then response status should be "403" Forbidden
    And response body should contain "<error>"

        Examples:
    | ds                           | error                         |
    | generated empty string       | Missing request argument "ds" |
    | generated random string      | No dataset                    |
