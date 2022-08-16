@api
Feature: Check ds2ws [POST] request

    @positive
    Scenario: Create job to derive ws dataset
    Given xl Dataset is uploaded and processed by the system
    And unique ws Dataset name is generated
    When ds2ws request with ds and ws parameters is send
    Then response status should be 200 OK
    And response body schema should be valid 

