@api
Feature: Check csv_export [POST] request

    @progress
    Scenario: Export any ws dataset as csv
      Given ws Dataset is uploaded and processed by the system
      When csv export with "ds" and "schema" parameters is send
      Then response status should be 200 OK
      And response body schema should be valid by "csv_schema"