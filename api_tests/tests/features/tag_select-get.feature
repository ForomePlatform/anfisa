@api
@tag_select
Feature: Check tag_select [GET] request

    @any
    @positive
    Scenario Outline: Should return tags of any ws dataset
        Given "ws Dataset" is uploaded and processed by the system
        When tag_select request with "<ds>" parameter is send
        Then response status should be "200" OK
        And response body schema should be valid by "tag_select_schema"

        Examples:
            | ds         |
            | ws Dataset |


    @specific
    @positive
    Scenario: Should return tags of specific "wgs_PGP3140_nist_3_3_2" ws dataset
        Given "wgs_PGP3140_nist_3_3_2" is uploaded and processed by the system
        And ws Dataset is derived from it
        When tag_select request with specified "ds" parameter is send
        Then response status should be "200" OK
        And response body json should match expected data for "tag_select" request


    @any
    @positive
    Scenario Outline: Should return tag, created by another ws dataset
        Given "xl Dataset with code filter" is uploaded and processed by the system
        And ws Dataset with < 9000 records is derived from it
        And unique "tag" is generated
        And "<tag>" is created for "<rec>" record of ws dataset
        And another ws Dataset with < 9000 records is derived
        When tag_select request with second ws dataset as "ds" is send
        Then response status should be "200" OK
        And response body "tag-list" tag list should include "<tag>"

        Examples:
            | rec | tag                 |
            | 0   | generated _note Tag |


    @any
    @negative
    Scenario Outline: Should fail to return tags
        Given "xl Dataset" is uploaded and processed by the system
        When tag_select request with "<ds>" parameter is send
        Then response status should be "403" Forbidden
        And response body should contain "<error>"

        Examples:
            | ds                              | error                          |
            | generated empty string          | Missing request argument "ds"  |
            | generated random literal string | No dataset                     |
            | xl Dataset                      | DS kinds conflicts: xl vs. ws  |