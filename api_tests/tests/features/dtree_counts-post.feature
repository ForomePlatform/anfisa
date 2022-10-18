@api
@dtree_counts
Feature: Check dtree_counts [POST] request

    @any
    @positive
    Scenario: Check dtree_counts response
    Given "xl Dataset" is uploaded and processed by the system
    And "dtree_set" request with "xl Dataset" and "code" parameters is send
    When "dtree_counts" request with correct parameters is send
    Then response status should be "200" OK
    And response body schema should be valid by "dtree_counts_schema"