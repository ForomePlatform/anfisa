@api
Feature: Check adm_reload_ds [POST] request

    @positive
    Scenario: Force reload xl dataset in memory
    Given xl Dataset is uploaded and processed by the system
    When adm_reload_ds request with ds parameter is send
    Then response status should be 200 OK
    And response body should be equal "Reloaded DatasetName"

    @positive
    Scenario: Force reload ws dataset in memory
    Given ws Dataset is uploaded and processed by the system
    When adm_reload_ds request with ds parameter is send
    Then response status should be 200 OK
    And response body should be equal "Reloaded DatasetName"

    @progress
    Scenario Outline: adm_reload_ds with incorrect ds parameter
    When adm_reload_ds request with inccorrect ds parameter is send
    Then response status should be 403 Forbidden
    And response body should be equal "Reloaded DatasetName"

        Examples:
        | ds            |
        | Empty string  |




