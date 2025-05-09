@api
@ws_tags
Feature: Check ws_tags [POST] request

    @any
    @positive
    Scenario Outline: Return a list of tags for any ws dataset
        Given "xl Dataset with code filter" is uploaded and processed by the system
        And "ws Dataset with < 9000" records is derived from it
        When ws_tags request with "<ws>" and "<rec>" is send
        Then response status should be "200" OK
        And response body schema should be valid by "ws_tags_schema"

        Examples:
            | ws            | rec |
            | ws Dataset    | 0   |


    @specific
    @positive
    Scenario Outline: Return a list of tags for specific "wgs_PGP3140_nist_3_3_2" ws dataset
        Given "wgs_PGP3140_nist_3_3_2" is uploaded and processed by the system
        And "ws Dataset with < 9000" records is derived from it
        When ws_tags request with "<ws>" and "<rec>" is send
        Then response body json should match expected data for "ws_tags" request

            Examples:
            | ws            | rec |
            | ws Dataset    | 0   |


    @any
    @positive
    Scenario Outline: Create a new tag for any ws dataset
        Given "xl Dataset with code filter" is uploaded and processed by the system
        And "ws Dataset with < 9000" records is derived from it
        And unique "tag" is generated
        When ws_tags request with correct "<ws>", "<rec>", "<tag_type>" is send
        Then response status should be "200" OK
        And response body "op-tags" tag list should include "<tag_type>"
        And response body "rec-tags" should include "<tag_type>"
        And tag_select response should include "<tag_type>"

        Examples:
        | ws         | rec | tag_type            |
        | ws Dataset | 0   | generated true Tag  |
        | ws Dataset | 0   | generated _note Tag |


    @any
    @negative
    Scenario Outline: Fail to return a list of tags for any ws dataset
        Given "xl Dataset with code filter" is uploaded and processed by the system
        And "ws Dataset with < 9000" records is derived from it
        When ws_tags request with "<ws>" and "<rec>" is send
        Then response status should be "403" Forbidden
        And response body should contain "<error>"

        Examples:
        | ws                              | rec                    | error                          |
        | generated empty string          | 0                      | Missing request argument "ds"  |
        | ws Dataset                      | generated empty string | Missing request argument "rec" |
        | generated random literal string | 0                      | No dataset                     |
        | xl Dataset                      | 0                      | DS kinds conflicts: xl vs. ws  |
