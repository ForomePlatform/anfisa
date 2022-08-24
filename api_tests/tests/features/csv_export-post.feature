@api
Feature: Check csv_export [POST] request

    @progress
    Scenario: Export any ws dataset as csv
      Given "ws Dataset" is uploaded and processed by the system
      When csv_export request with "ds" and "schema" parameters is send
      Then response status should be "200" OK
      And response body schema should be valid by "csv_export_schema"

    @progresssProblemWithcode
    Scenario Outline: Export specific ws dataset as csv
      Given "xl_PGP3140_wgs_NIST-3_3_2" is uploaded and processed by the system
      And ws Dataset, derived by "<code>", is prepared
      When csv_export request with "schema" and "ds" parameters is send
      Then response status should be "200" OK
      And response body should match expected data for "csv_export" request

      Examples:
      | code                                                            |
      | if Callers in {GATK_HOMOZYGOUS}:\n    return True\nreturn False |


    @progress
    Scenario: Fail to export xl dataset with more than 9000 records
      Given "ws Dataset" is uploaded and processed by the system
      When csv_export request with "ds" and "schema" parameters is send
      Then response status should be "200" OK
      And response body schema should be valid by "csv_export_schema"