@api
@export_ws
Feature: Check export_ws [POST] request

    @any
    @positive
    Scenario: Check export_ws response
        Given "ws Dataset" is uploaded and processed by the system
        When "export_ws" request with "ws Dataset" parameter is send
        Then response status should be "200" OK
        And response body schema should be valid by "export_ws_schema"