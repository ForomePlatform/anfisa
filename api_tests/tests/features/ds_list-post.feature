@api
Feature: Check ds_list [POST] request

    @progress
    Scenario: Should create a task to prepare a list of N variants for any dataset
    Given "xl Dataset" is uploaded and processed by the system
    When ds_list request is send
    Then response status should be "200" OK
    And response body schema should be valid by "ds_list_schema"

    @progress
    Scenario: Should create a task to prepare a list of N variants for any dataset
    Given "xl Dataset" is uploaded and processed by the system
    When ds_list request is send
    Then response status should be "200" OK
    And response body schema should be valid by "ds_list_schema"
