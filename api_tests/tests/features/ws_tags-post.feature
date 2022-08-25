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
