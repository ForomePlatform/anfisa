@api
Feature: Check job_status [POST] request

    @any
    @positive
    Scenario: Positive job_status request
      Given "xl Dataset with > 9000 records" is uploaded and processed by the system
      And unique "ws" Dataset name is generated
      And ws dataset is derived from it
      When job_status request is send
      Then response status should be "200" OK
      And response body schema should be valid by "job_status_schema"


    @any
    @negative
    Scenario Outline: Send job_status request without parameter
      When job_status request with "<task>" is send
      Then response status should be "<code>" <status>
      And response body should contain "<error>"

      Examples:
      | task                            | error                           | code | status         |
      | generated empty string          | Missing request argument "task" | 403  | Forbidden      |
      | generated random literal string | invalid literal for int()       | 500  | Internal Error |


    @any
    @negative
    Scenario Outline: Send job_status request with incorrect parameter
      When job_status request with "<task>" is send
      Then response status should be "200" OK
      And response body should be "null"

     Examples:
      | task                          |
      | generated numbers only string |



