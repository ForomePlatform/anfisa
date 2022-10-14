@api
@after_all_hook
Feature: Remove test-data after automation test run

    @any
    @specific
    @positive
    @negative
    Scenario: Delete test-data created automatically
      Given "ws datasets" should be deleted
      And "dtrees" should be deleted