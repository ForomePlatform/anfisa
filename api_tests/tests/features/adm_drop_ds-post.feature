@api
Feature: Check adm_drop_ds [POST] request

    @positive
    Scenario: Delete ws Dataset from the database
    Given xl Dataset is uploaded and processed by the system
    And unique ws Dataset with appropriate name is derived from it
    When adm_drop_ds requests with correct "ds" parameter is send
    Then response status should be 200 OK
    And response body should be equal "Dropped DatasetName"


    @negative
    Scenario Outline: Send adm_drop_ds with incorrect parameters
    When adm_drop_ds requests with incorrect <ds> parameter is send
    Then response status should be 403 Forbidden
    And response body should include <error>

    Examples:
        | ds                              | error                                                        |
        | generated empty string          | Missing request argument "ds"                                |
        | generated random literal string | no appropriate pattern in 'auto-drop-datasets' config option |
        | generated random registered ws  | no appropriate pattern in 'auto-drop-datasets' config option |
