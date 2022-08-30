@api
Feature: Check ws_list [POST] request

    @progress
    Scenario: Return current list of Dataset variants for any ws dataset
    Given "xl Dataset with filter" is uploaded and processed by the system
    And ws Dataset with < 9000 records is derived from it
    When ws_list request with correct "ds" parameter is send
    Then response status should be "200" OK
    And response body schema should be valid by "ws_list_schema"
    And response body "records" "descriptor" schemas should be valid


    @progress
    Scenario: Return current list of Dataset variants for any ws dataset
    Given "xl Dataset with filter" is uploaded and processed by the system
    And ws Dataset with < 9000 records is derived from it
    When ws_list request with correct "ds" parameter is send
    Then response status should be "200" OK
    And response body schema should be valid by "ws_list_schema"
    And response body "records" "descriptor" schemas should be valid