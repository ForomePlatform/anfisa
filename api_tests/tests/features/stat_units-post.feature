@api
Feature: Check stat_units [POST] request

    @positive
    Scenario: Return first attribute data, marked as incomplete by ds_stat for any dataset
    Given "xl Dataset" is uploaded and processed by the system
    And dtree_stat response with incomplete units is returned
    When stat_units request is send
    Then response status should be "200" OK
    And response body schema should be valid by "stat_units_schema"
    And response body "units" property_status schemas should be valid
    And response body "rq-id" should match the one in request


    @positive
    Scenario: Return first attribute data, marked as incomplete by ds_stat for any dataset
    Given "xl Dataset" is uploaded and processed by the system
    And ds_stat response with incomplete units is returned
    When stat_units request is send
    Then response status should be "200" OK
    And response body schema should be valid by "stat_units_schema"
    And response body "units" property_status schemas should be valid
    And response body "rq-id" should match the one in request


    @negative
    Scenario Outline: Fail to return attribute data, marked as incomplete
    Given "xl Dataset" is uploaded and processed by the system
    And dtree_stat response with incomplete units is returned
    When stat_units request with "<ds>", "rq" and "<units>" parameters is send
    Then response status should be "<code>" <status>
    And response body should contain "<error>"

    Examples:
    | ds                 | units              | error                            | code| status         |
    | gen. empty string  | prepared unit      | Missing request argument "ds"    | 403 | Forbidden      |
    | xl Dataset         | gen. empty string  | Missing request argument "units" | 403 | Forbidden      |
    | gen. random string | prepared unit      | No dataset                       | 403 | Forbidden      |
    | xl Dataset         | gen. random string | Exception on evaluation          | 500 | Internal Error |