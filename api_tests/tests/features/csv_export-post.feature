@api
Feature: Check csv_export [POST] request

    @progress
    Scenario: Export any ws dataset as csv
      Given ws Dataset is uploaded and processed by the system
      When csv export with "ds" and "schema" parameters is send
      Then response status should be 200 OK
      And response body schema should be valid by "csv_export_schema"

    @progress
    Scenario: Export specific ws dataset as csv
      Given ws Dataset is uploaded and processed by the system
      When csv export with "ds" and "schema" parameters is send
      Then response status should be 200 OK
      And response body schema should be valid by "csv_export_schema"

    @progress
    Scenario: Fail to export xl dataset with more than 9000 records
      Given ws Dataset is uploaded and processed by the system
      When csv export with "ds" and "schema" parameters is send
      Then response status should be 200 OK
      And response body schema should be valid by "csv_export_schema"