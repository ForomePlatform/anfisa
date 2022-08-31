@api
Feature: Check tag_select [GET] request

    @progress
    Scenario Outline: Should return tags of any ws dataset
    Given "ws Dataset" is uploaded and processed by the system
    When tag_select request with "<ds>" parameter is send
    Then response status should be "200" OK
    And response body schema should be valid by "tag_select_schema"

        Examples:
        | ds         |
        | ws Dataset |


    @positive
    Scenario: Should return tags of specific ws dataset
    Given "xl_PGP3140_wgs_NIST-3_3_2" is uploaded and processed by the system
    And ws Dataset is derived from it
    When tag_select request with specified "ds" parameter is send
    Then response status should be "200" OK
    And response body json should match expected data for "tag_select" request


    @positive
    Scenario: Should return tags of specific ws dataset
    Given "xl Dataset with filter" is uploaded and processed by the system
    And ws Dataset with < 9000 records is derived from it
    And _note tag is created for variant 0 of ws dataset
    And another ws Dataset with < 9000 records is derived
    When tag_select request with second ws dataset as "ds" is send
    Then response status should be "200" OK
    And response body "op-tags" list should include "_note"
    And response body "rec-tags" should include
    And response body "upd-from" should be equal "first ws dataset"


    @progress
    Scenario Outline: Should return tags of specific ws dataset
    Given "xl Dataset" is uploaded and processed by the system
    When tag_select request with "<ds>" parameter is send
    Then response status should be "403" Forbidden
    And response body should contain "<error>"

        Examples:
        | ds                              | error                          |
        | generated empty string          | Missing request argument "ds"  |
        | generated random literal string | No dataset                     |
        | xl Dataset                      | DS kinds conflicts: xl vs. ws  |