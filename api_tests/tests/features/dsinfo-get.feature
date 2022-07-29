@api
Feature: Check Dsinfo[GET] request

  @positive
  Scenario Outline: Send Dsinfo request (successful)
    When I send get dsinfo request with parameters: "<Parameters>" (successful)
#    Then I validate the response by schema
    Then I see a "<Text>" text in response

    Examples:
      | Parameters                          | Text                              |
      | { "ds": "xl_PGP3140_wgs_panel_hl" } | "name": "xl_PGP3140_wgs_panel_hl" |
      | { "ds": "1658095799" }              | "name": "1658095799"              |


  @negative
  Scenario Outline: Send Dsinfo request (unsuccessful)
    When I send get dsinfo request with parameters: "<Parameters>" (unsuccessful)
    Then I see a "<Error>" error message in response

    Examples:
      | Parameters   | Error                                |
      | { "ds": "" } | Error: Missing request argument "ds" |
      | { "aa": "" } | Error: Missing request argument "ds" |
      | {  }         | Error: Missing request argument "ds" |
