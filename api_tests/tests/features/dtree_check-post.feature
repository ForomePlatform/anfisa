@api
Feature: Check dtree_check [POST] request

    @positive
    Scenario Outline: Submit Python code without conditions
        Given xl Dataset is uploaded and processed by the system
        When dtree_check request with <code> is send
        Then response status should be 200 OK
        And response body schema should be valid
        And response body code should be equal <code>

        Examples:
        | code          |
        | return True   |

    @negative
    Scenario Outline: Submit dtree_check request incorrectly
        Given xl Dataset is uploaded and processed by the system
        When dtree_check request with <code> is send
        Then response status should be 200 OK
        And response body schema should be valid
        And response body error should be equal <error>

        Examples:
        | code          | error                         |
        | retur True    | Improper instruction          |
        | True          | Instructon must be of if-type |

    @negative
    Scenario Outline: Submit dtree_check request without a code
        Given xl Dataset is uploaded and processed by the system
        When dtree_check request with <code> is send
        Then response status should be 403 OK
        And response body should contain <error>

        Examples:
        | code          | error                                         |
        | Empty string  | Missing request argument: "dtree" or "code    |


