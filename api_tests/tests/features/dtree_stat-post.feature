@api
@dtree_stat
Feature: Check dtree_stat [POST] request

    @any
    @positive
    Scenario Outline: Get attributes for any xl dataset's dtree by code
        Given "xl Dataset" is uploaded and processed by the system
        When dtree_stat request with "<ds>", "<code>", "<no>" and "<tm>" parameters is send
        Then response status should be "200" OK
        And response body schema should be valid by "dtree_stat_schema"
        And response body "stat-list" property_status schemas should be valid
        And response body "functions" property_status schemas should be valid

        Examples:
            | ds         | code         | no | tm |
            | xl Dataset | return False | 0  | 0  |

    @specific
    @positive
    Scenario Outline: Get attributes for specific "wgs_PGP3140_nist_3_3_2" xl dataset's dtree by code
        Given "wgs_PGP3140_nist_3_3_2" is uploaded and processed by the system
        When dtree_stat request with "<ds>", "<code>", "<no>" and "<tm>" parameters is send
        Then response status should be "200" OK
        And response body json should match expected data for "dtree_stat" request

        Examples:
            | ds                     | code         | no | tm |
            | wgs_PGP3140_nist_3_3_2 | return False | 0  | 0  |

    @any
    @negative
    Scenario Outline: Fail to get attributes for any xl dataset's dtree
        Given "xl Dataset" is uploaded and processed by the system
        When dtree_stat request with "<ds>", "<code>", "<no>" and "<tm>" parameters is send
        Then response status should be "403" Forbidden
        And response body should contain "<error>"

        Examples:
            | ds                 | no                | tm | code             | error                                       |
            | gen. empty string  | 0                 | 0  | return False     | Missing request argument "ds"               |
            | xl Dataset         | gen. empty string | 0  | return False     | Missing request argument "no"               |
            | xl Dataset         | 0                 | 0  | gen. empty string| Missing request argument: "dtree" or "code" |
            | gen. random string | 0                 | 0  | return False     | No dataset                                  |
