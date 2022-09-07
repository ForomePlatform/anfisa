# because there is no after all hook in pytest-bdd

@api
Feature: Remove test-data after automation test cases

    @any
    @specific
    @positive
    @negative
    Scenario: Delete test-data created automatically
      Then "ws datasets" should be deleted
      And "dtrees" should be deleted