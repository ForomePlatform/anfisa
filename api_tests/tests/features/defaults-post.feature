@api
@defaults
Feature: Check defaults [POST] request

    @any
    @positive
    Scenario Outline: Check defaults response
        Given "<ds>" is uploaded and processed by the system
        When "defaults" request with "<ds>" parameter is send
        Then response status should be "200" OK
        And response body schema should be valid by "defaults_schema"

        Examples:
            | ds         |
            | xl Dataset |
            | ws Dataset |