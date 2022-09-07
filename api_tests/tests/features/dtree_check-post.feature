@api
Feature: Check dtree_check [POST] request

    @any
    @positive
    Scenario Outline: Submit correct Python code
        Given "xl Dataset" is uploaded and processed by the system
        When dtree_check request with "<code>" and "<ds>" is send
        Then response status should be "200" OK
        And response body schema should be valid by "dtree_check_schema"
        And response body "code" should be equal "<code>"
        And error property is not present in response

        Examples:
        | ds         | code                   |
        | xl Dataset | return True            |
        | xl Dataset | generated complex code |


    @any
    @negative
    Scenario Outline: Submit incorrect Python code
        Given "xl Dataset" is uploaded and processed by the system
        When dtree_check request with "<code>" and "<ds>" is send
        Then response status should be "200" OK
        And response body schema should be valid by "dtree_check_schema"
        And response body "error" should be equal "<error>"

        Examples:
        | ds         | code          | error                         |
        | xl Dataset | retur True    | Improper instruction          |
        | xl Dataset | True          | Instructon must be of if-type |


    @any
    @negative
    Scenario Outline: Submit dtree_check request without a parameter
        Given "xl Dataset" is uploaded and processed by the system
        When dtree_check request with "<code>" and "<ds>" is send
        Then response status should be "403" Forbidden
        And response body should contain "<error>"

        Examples:
        | ds                        | code                      | error                                       |
        | xl Dataset                | generated empty string    | Missing request argument: "dtree" or "code" |
        | generated empty string    | return False              | Missing request argument "ds"               |


