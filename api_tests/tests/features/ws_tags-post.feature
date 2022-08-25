@api
Feature: Check ws_tags [POST] request

    @progress
    Scenario Outline: Return a list of ws tags
    Given ws Dataset is uploaded and processed by the system
    When ws_tags request with "<ws>" and "<rec>" is send
    Then response status should be 200 OK
    And response body schema should be valid by "ws_tags_schema"

        Examples:
        | ws            | rec |
        | generated ws  | 0   |