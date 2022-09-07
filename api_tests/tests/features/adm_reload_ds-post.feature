@api
Feature: Check adm_reload_ds [POST] request

    @any
    @positive
    Scenario Outline: Force reload xl dataset in memory
    Given "<dsType>" is uploaded and processed by the system
    When adm_reload_ds request with "ds" parameter is send
    Then response status should be "200" OK
    And response body should be equal "Reloaded" DatasetName

        Examples:
        | dsType     |
        | xl Dataset |
        | ws Dataset |


    @any
    @negative
    Scenario Outline: adm_reload_ds with empty parameter
    When adm_reload_ds request with incorrect "<ds>" parameter is send
    Then response status should be "403" Forbidden
    And response body should contain "<error>"

        Examples:
        | ds                               | error                         |
        | generated empty string           | Missing request argument "ds" |
        | generated random literal string  | No dataset                    |
        | generated space separated string | No dataset                    |
