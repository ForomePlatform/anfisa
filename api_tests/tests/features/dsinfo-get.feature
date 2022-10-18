@api
Feature: Check Dsinfo[GET] request

  @positive
  Scenario Outline: Send Dsinfo request with parameters: "<parameters>" (successful)
    When I send get dsinfo request with parameters: "<parameters>" (successful)
    Then response body schema should be valid by "dsinfo_schema"
    And response body "name" should be equal "<name>"

    Examples:
      | parameters                          | name                    |
      | { "ds": "xl_PGP3140_wgs_panel_hl" } | xl_PGP3140_wgs_panel_hl |
      | { "ds": "PGP3140_wgs_panel_hl" }    | PGP3140_wgs_panel_hl    |
      | { "ds": "bgm_red_button" }          | bgm_red_button          |


  @negative
  Scenario Outline: Send Dsinfo request with parameters: "<parameters>" (unsuccessful)
    When I send get dsinfo request with parameters: "<parameters>" (unsuccessful)
    Then response body should contain "<error>"

    Examples:
      | parameters   | error                                |
      | { "ds": "" } | Error: Missing request argument "ds" |
      | { "aa": "" } | Error: Missing request argument "ds" |
      | {  }         | Error: Missing request argument "ds" |
