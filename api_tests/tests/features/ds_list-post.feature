@api
@ds_list
Feature: Check ds_list [POST] request

    @any
    @positive
    Scenario: Return a list samples for any dataset
    Given "xl Dataset with > 150 records" is uploaded and processed by the system
    When ds_list request is send
    Then response status should be "200" OK
    And response body schema should be valid by "ds_list_schema"
    And job_status should be "Done"
    And job_status response body records schema should be valid

    @any
    @positive
    Scenario Outline: Return a list of N samples for any dataset
    Given "xl Dataset with > 150 records" is uploaded and processed by the system
    When ds_list request with "<smpcnt>" parameter is send
    Then response status should be "200" OK
    And response body schema should be valid by "ds_list_schema"
    And job_status should be "Done"
    And job_status response body records schema should be valid
    And number of samples should be equal "<N>"

        Examples:
        | smpcnt | N   |
        | 9      | 10  |
        | 10     | 10  |
        | 11     | 11  |
        | 149    | 149 |
        | 150    | 150 |
        | 151    | 150 |

    @any
    @negative
    Scenario Outline: Fail to return a list samples for any dataset
    When ds_list request with incorrect "<ds>" parameter is send
    Then response status should be "403" Forbidden
    And response body should contain "<error>"

        Examples:
        | ds                     | error                         |
        | generated empty string | Missing request argument "ds" |
        | random literal string  | No dataset                    |

