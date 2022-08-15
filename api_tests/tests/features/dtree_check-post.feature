@api
Feature: Check dtree_check [POST] request

    @positive
    Scenario Outline: Submit correct Python code
        Given xl Dataset is uploaded and processed by the system
        When dtree_check request with <code> and <ds> is send
        Then response status should be 200 OK
        And response body schema should be valid
        And response body code should be equal <code>

        Examples:
        | ds         | code                                                     |
        | xl dataset | return True                                              |
        | xl dataset | if anything in {something}:\n\treturn True\nreturn False |

    @negative
    Scenario Outline: Submit incorrect Python code
        Given xl Dataset is uploaded and processed by the system
        When dtree_check request with <code> and <ds> is send
        Then response status should be 200 OK
        And response body schema should be valid
        And response body error should be equal <error>

        Examples:
        | ds         | code          | error                         |
        | xl dataset | retur True    | Improper instruction          |
        | xl dataset | True          | Instructon must be of if-type |

    @negative
    Scenario Outline: Submit dtree_check request without a parameter
        Given xl Dataset is uploaded and processed by the system
        When dtree_check request with <code> and <ds> is send
        Then response status should be 403 OK
        And response body should contain <error>

        Examples:
        | ds           | code         | error                                       |
        | xl dataset   | Empty string | Missing request argument: "dtree" or "code" |
        | Empty string | return False | Missing request argument "ds"               |


