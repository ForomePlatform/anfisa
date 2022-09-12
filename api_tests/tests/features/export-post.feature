@api
@export
Feature: Check export [POST] request

    @any
    @positive
    Scenario: Check export response
    Given "ws Dataset" is uploaded and processed by the system
    When "export" request with ds and empty conditions parameters is send
    Then response status should be "200" OK
    And response body schema should be valid by "export_schema"