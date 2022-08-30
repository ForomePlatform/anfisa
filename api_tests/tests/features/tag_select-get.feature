@api
Feature: Check tag_select [GET] request

    @progress
    Scenario: Should return tags of any ws dataset
    Given "xl Dataset" is uploaded and processed by the system
    And unique "ws" Dataset name is generated
    When tag_select request with correct "ds" parameter is send
    Then response status should be "200" OK
    And response body schema should be valid by "tag_select_schema"