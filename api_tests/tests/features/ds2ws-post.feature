@api
@ds2ws
Feature: Check ds2ws [POST] request

    @any
    @positive
    Scenario: Derive ws dataset with code attribute
        Given "xl Dataset" is uploaded and processed by the system
        And unique "ws Dataset name" is generated
        And "valid" Python code is constructed
        When ds2ws request with "ds", "code" and "unique_ws_Dataset_name" parameters is send
        Then response status should be "200" OK
        And response body schema should be valid by "ds2ws_schema"
        And job status should be "Done"
        And derived dataset can be found in the dirinfo response
        And "code" is present in dsinfo response for derived dataset


    @any
    @negative
    Scenario Outline: Fail to derive ws dataset with incorrect "<ws>" parameters
        Given "xl Dataset" is uploaded and processed by the system
        And "valid" Python code is constructed
        When ds2ws request with "ds", "code" and "<ws>" parameters is send
        Then response status should be "200" OK
        And response body schema should be valid by "ds2ws_schema"
        And job status should be "<error>"

        Examples:
            | ws                                | error                                                           |
            | generated one space string        | Incorrect derived dataset: Improper name for dataset:           |
            | generated space separated string  | Incorrect derived dataset: Improper name for dataset: Autotest- |
            | generated duplicated ws name      | Dataset already exists                                          |
            | generated 251 literal string      | Failed, ask tech support                                        |


    @any
    @negative
    Scenario: Fail to derive ws dataset without attributes (>9000 records)
        Given "xl Dataset with > 9000 records" is uploaded and processed by the system
        And unique "ws Dataset name" is generated
        When ds2ws request with "xl Dataset with > 9000 records" and "unique_ws_Dataset_name" parameters is send
        Then response status should be "200" OK
        And response body schema should be valid by "ds2ws_schema"
        And job status should be "Size is incorrect"


    @any
    @negative
    Scenario Outline: Fail to derive ws dataset with missing "<ws>" parameters
        Given "xl Dataset" is uploaded and processed by the system
        When ds2ws request with "<ds>" and "<ws>" parameters is send
        Then response status should be "403" Forbidden
        And response body should contain "<error>"

        Examples:
            | ds                     | ws                       | error                             |
            | xl Dataset             | generated empty string   | Missing request argument "ws"     |
            | generated empty string | generated unique ws name | Missing request argument "ds"     |
