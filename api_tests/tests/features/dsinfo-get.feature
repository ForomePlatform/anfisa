@api
@dsinfo
Feature: Check Dsinfo[GET] request

    @any
    @positive
    Scenario Outline: Send Dsinfo request with parameters: "<parameters>" correct
        When dsinfo request is send with parameters: "<parameters>"
        Then response status should be "200" OK
        And response body schema should be valid by "dsinfo_schema"
        And response body "name" should be equal "<name>"

        Examples:
            | parameters                          | name                    |
            | { "ds": "xl_PGP3140_wgs_panel_hl" } | xl_PGP3140_wgs_panel_hl |
            | { "ds": "1658095799" }              | 1658095799              |


    @any
    @negative
    Scenario Outline: Send Dsinfo request with parameters: "<parameters>" incorrect
        When dsinfo request is send with parameters: "<parameters>"
        Then response status should be "403" Forbidden
        And response body should contain "<error>"

    Examples:
      | parameters   | error                                |
      | { "ds": "" } | Error: Missing request argument "ds" |
      | { "aa": "" } | Error: Missing request argument "ds" |
      | {  }         | Error: Missing request argument "ds" |
