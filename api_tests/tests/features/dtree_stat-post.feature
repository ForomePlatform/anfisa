@api
Feature: Check dtree_stat [POST] request

    @progress
    Scenario Outline: Get attributes for any xl dataset's dtree by code
    Given xl Dataset is uploaded and processed by the system


        Examples:
        | ds         | code | no | tm |
        | xl Dataset |      |    |    |