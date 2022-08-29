@api
Feature: Check DsStat [POST] request

    @progress
    Scenario: Return full information about any xl dataset (no filters applied)
    Given "xl Dataset" is uploaded and processed by the system
    When ds_stat request with correct "ds" parameter is send
    Then response status should be "200" OK
    And response body schema should be valid by "ds_stat_schema"
    And response body "stat-list" property_status schemas should be valid
    And response body "functions" property_status schemas should be valid
    And response body "filter-list" solution_entry schemas should be valid
    And response body "total-counts" should be equal "filtered-counts"