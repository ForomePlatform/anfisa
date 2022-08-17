@api
Feature: Check ds2ws [POST] request

    @progress
    Scenario: Create job to derive ws dataset
    Given xl Dataset is uploaded and processed by the system
    And unique ws Dataset name is generated
    When ds2ws request with <ds> and <ws> parameters is send
    Then response status should be 200 OK
    And response body schema should be valid
    And job status should be "Done"
    And derived dataset can be found in the dirinfo response

    @progress
    Scenario: Create job to derive ws dataset with code attribute
    Given xl Dataset is uploaded and processed by the system
    And unique ws Dataset name is generated
    And valid Python code is constructed
    When ds2ws request with <ds>, <ws> and <code> parameters is send
    Then response status should be 200 OK
    And response body schema should be valid
    And job status should be "Done"
    And derived dataset can be found in the dirinfo response
    And <code> is present in dsinfo response for this dataset
