@api
@vsetup
Feature: Check vsetup [POST] request

    @any
    @positive
    Scenario: Check vsetup response
    Given "xl Dataset" is uploaded and processed by the system
    When "vsetup" request with "ds" parameter is send
    Then response status should be "200" OK
    And response body schema should be valid by "vsetup_schema"