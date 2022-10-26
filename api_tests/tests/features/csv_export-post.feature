@api
@csv_export
Feature: Check csv_export [POST] request

    @any
    @positive
    Scenario: Export any ws dataset as csv
        Given "ws Dataset" is uploaded and processed by the system
        When csv_export request with "ws Dataset" and "csv" parameters is send
        Then response status should be "200" OK
        And response body schema should be valid by "csv_export_schema"


    @specific
    @positive
    Scenario: Export specific "wgs_PGP3140_nist_3_3_2" ws dataset as csv
        Given "wgs_PGP3140_nist_3_3_2" is uploaded and processed by the system
        And "ws Dataset with < 9000" records is derived from it
        When csv_export request with "ws with < 9000 records" and "csv" parameters is send
        Then response status should be "200" OK
        And response body should match expected data for "csv_export" request


    @any
    @negative
    Scenario Outline: Fail to export xl dataset with more than 9000 records
        Given "xl Dataset" is uploaded and processed by the system
        And "ws Dataset with < 9000" records is derived from it
        When csv_export request with "<ds>" and "<schema>" parameters is send
        Then response status should be "403" Forbidden
        And response body should contain "<error>"

        Examples:
            | ds                     | schema                 | error                             |
            | xl Dataset             | csv                    | Too many records for export       |
            | generated empty string | csv                    | Missing request argument "ds"     |
            | ws with < 9000 records | generated empty string | Missing request argument "schema" |