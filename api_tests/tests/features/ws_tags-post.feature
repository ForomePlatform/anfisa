@api
Feature: Check ws_tags [POST] request

    @progress
    Scenario Outline: Return a list of tags for ws dataset
    Given xl Dataset is uploaded and processed by the system
    And ws Dataset with < 9000 records is derived from it
    When ws_tags request with "<ws>" and "<rec>" is send
    Then response status should be 200 OK
    And response body schema should be valid by "ws_tags_schema"

        Examples:
        | ws            | rec |
        | generated ws  | 0   |


    @progresss
    Scenario Outline: Return a list of tags for ws dataset
    Given xl Dataset is uploaded and processed by the system
    And ws Dataset with < 9000 records is derived from it
    When ws_tags request with "<ws>" and "<rec>" is send
    Then response status should be 403 Forbidden
    And response body should contain "<error>"

        Examples:
        | ws                              | rec                    | error                          |
        | generated empty string          | 0                      | Missing request argument "ds"  |
        | generated ws                    | generated empty string | Missing request argument "rec" |
        | generated random literal string | 0                      | No dataset                     |
        | xl Dataset                      | 0                      | DS kinds conflicts: xl vs. ws  |
