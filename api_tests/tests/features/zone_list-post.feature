@api
@zone_list
Feature: Check zone_list [POST] request

    @any
    @positive
    Scenario: Should return a list of zones for any ws dataset
        Given "ws Dataset" is uploaded and processed by the system
        When zone_list request with "ds" parameter is send
        Then response status should be "200" OK
        And response body schema should be valid by "zone_descriptor_serial"


    @any
    @positive
    Scenario: Should return zone variants for any ws dataset
        Given "xl Dataset with code filter" is uploaded and processed by the system
        And ws Dataset with < 9000 records is derived from it
        And "random" zone is selected
        When zone_list request with correct "ds" and "zone" parameters is send
        Then response status should be "200" OK
        And response body schema should be valid by "zone_descriptor_single"


    @specific
    @positive
    Scenario: Should return zone variants for specific ws dataset
        Given "xl_PGP3140_wgs_NIST-3_3_2" is uploaded and processed by the system
        And ws Dataset with < 9000 records is derived from it
        And "first" zone is selected
        When zone_list request with "ds" parameter is send
        Then response status should be "200" OK
        And response body json should match expected data for "zone_list_serial" request


    @specific
    @positive
    Scenario: Should return a list of zones for specific ws dataset
        Given "xl_PGP3140_wgs_NIST-3_3_2" is uploaded and processed by the system
        And ws Dataset with < 9000 records is derived from it
        And "first" zone is selected
        When zone_list request with correct "ds" and "zone" parameters is send
        Then response status should be "200" OK
        And response body json should match expected data for "zone_list_single" request


    @any
    @negative
    Scenario Outline: Should return a list of zones for any ws dataset
        Given "xl Dataset" is uploaded and processed by the system
        And ws Dataset with < 9000 records is derived from it
        When zone_list request with "<ds>" parameter is send
        Then response status should be "403" Forbidden
        And response body should contain "<error>"

        Examples:
            | ds                     | error                         |
            | xl Dataset             | DS kinds conflicts: xl vs. ws |
            | generated empty string | Missing request argument "ds" |

