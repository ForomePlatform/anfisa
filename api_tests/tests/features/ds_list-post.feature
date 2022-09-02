@api
Feature: Check ds_list [POST] request

    @positive
    Scenario: Return a list samples for any dataset
    Given "xl Dataset with > 150 records" is uploaded and processed by the system
    When ds_list request is send
    Then response status should be "200" OK
    And response body schema should be valid by "ds_list_schema"
    And job_status should be "Done"
    And job_status response body schema should be valid by "<string>"


    @progress
    Scenario Outline: Return a list of N samples for any dataset
    Given "xl Dataset with > 150 records" is uploaded and processed by the system
    When ds_list request with "<smpcnt>" parameter is send
    Then response status should be "200" OK
    And response body schema should be valid by "ds_list_schema"
    And job_status should be "Done"
    And number of samples should be equal "<N>"

        Examples:
        | smpcnt | N   |
        | 9      | 10  |
        | 10     | 10  |
        | 11     | 11  |
        | 149    | 149 |
        | 150    | 150 |
        | 151    | 150 |

