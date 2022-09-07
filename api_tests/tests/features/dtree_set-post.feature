@api
Feature: Check dtree_set [POST] request

    @any
    @positive
    Scenario Outline: Set dtree for any dataset by code
    Given "<ds>" is uploaded and processed by the system
    When dtree_set request with "<ds>" and "<code>" parameters is send
    Then response status should be "200" OK
    And response body "kind" should be equal "<type>"
    And response body "code" should be equal "<code>"
    And response body "eval-status" should be equal "ok"
    And response body schema should be valid by "dtree_set_schema"
    And response body "dtree-list" "solution_entry" schemas should be valid
    And response body "points" "dtree_point_descriptor" schemas should be valid
    And response body "cond-atoms" condition_descriptor schemas should be valid

    Examples:
    | ds         | code              | type |
    | xl Dataset | return False      | xl   |
    | xl Dataset | gen. complex code | xl   |
    | ws Dataset | return False      | ws   |
    | ws Dataset | gen. complex code | ws   |


    @specific
    @positive
    Scenario Outline: Set dtree for specific dataset by code
    Given "xl_PGP3140_wgs_NIST-3_3_2" is uploaded and processed by the system
    When dtree_set request with "<ds>" and "<code>" parameters is send
    Then response status should be "200" OK
    And response body json should match expected data for "dtree-set" request

    Examples:
    | ds         | code              |
    | xl Dataset | gen. complex code |


    @any
    @positive
    Scenario Outline: Create dtree for any dataset
    Given "<ds>" is uploaded and processed by the system
    And unique Dtree name is generated
    When dtree_set request with correct "<ds>", "<code>" and "<instr>" parameters is send
    Then response status should be "200" OK
    And created dtree should be present in dtree list for selected dataset

    Examples:
    | ds         | code            | instr  |
    | xl Dataset | gen. valid code | UPDATE |
    | ws Dataset | gen. valid code | UPDATE |


    @any
    @negative
    Scenario Outline: Create dtree for any xl dataset
    Given "xl Dataset" is uploaded and processed by the system
    When dtree_set request with "<ds>" and "<code>" parameters is send
    Then response status should be "403" Forbidden
    And response body should contain "<error>"

    Examples:
    | ds                | code              | error                                       |
    | gen. empty string | gen. valid code   | Missing request argument "ds"               |
    | xl Dataset        | gen. empty string | Missing request argument: "dtree" or "code" |