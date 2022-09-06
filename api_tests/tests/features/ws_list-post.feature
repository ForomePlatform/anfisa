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


    @123
    Scenario: Return current list of Dataset variants for specific ws dataset
    Given "xl_PGP3140_wgs_NIST-3_3_2" is uploaded and processed by the system
    And ws Dataset with < 9000 records is derived from it
    When ws_list request with correct "ds" parameter is send
    Then response status should be "200" OK
    And response body json should match expected data for "ws_list" request


    @progress
    Scenario Outline: Return current list of Dataset variants for any ws dataset
    Given "xl Dataset with filter" is uploaded and processed by the system
    And ws Dataset with < 9000 records is derived from it
    When ws_list request with incorrect "<ds>" parameter is send
    Then response status should be "403" Forbidden
    And response body should contain "<error>"

        Examples:
        | ds                              | error                          |
        | generated empty string          | Missing request argument "ds"  |
        | generated random literal string | No dataset                     |
        | xl Dataset                      | DS kinds conflicts: xl vs. ws  |