@api
Feature: Check stat_units [POST] request

    @positive
    Scenario: Return attribute data, marked as incomplete by ds_stat for any dataset
    Given "xl Dataset" is uploaded and processed by the system
    And ds_stat response with incomplete units is returned
    When stat_units request is send
    Then response status should be "200" OK