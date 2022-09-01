@api
Feature: Check stat_units [POST] request

    @progress
    Scenario: Return first attribute data, marked as incomplete by ds_stat for any dataset
    Given "xl_PGP3140_wgs_NIST-3_3_2" is uploaded and processed by the system
    And ds_stat response with incomplete units is returned
    When stat_units request is send
    Then response status should be "200" OK
    And response body schema should be valid by "stat_units_schema"
    And response body "units" property_status schemas should be valid
    And response body "rq-id" should match the one in request