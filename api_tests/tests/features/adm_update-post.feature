@api
@adm_update
Feature: Check adm_update [POST] request

    @any
    @positive
    Scenario: Force update vault state
        When adm_update request is send
        Then response status should be "200" OK
        And response body should be equal "Updated"
