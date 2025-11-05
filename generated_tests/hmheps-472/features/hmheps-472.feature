Feature: Ed Leader Dashboard | Welcome screen Implementation

  As a tester
  I want to test the Welcome screen implementation for Ed Leader Dashboard
  So that I can ensure all user flows and edge cases are properly handled

  Background:
    Given the system is running
    And the welcome-screen feature flag is enabled by default
    And test users with different permission levels exist


  # Positive Test Scenarios
  Scenario: TC001_P01: First-time Login Flow for Admin with Rostering Rights - Configure Settings
    Given I am an Ed administrator with rostering rights
    And I have never logged into the application before
    When I log into the application
    Then I should see a "Welcome {Name}" message for 1000ms
    And the screen transitions to "Let's Get Started" view
    When I click the "Configure Settings" button
    Then I am redirected to the "My schools → Roster" page

  Scenario: TC002_P02: First-time Login Flow - Go to Home Option
    Given I am an Ed administrator with rostering rights
    And I have never logged into the application before
    When I log into the application
    And I wait for the welcome message to transition
    And I click the "Go to Home" button
    Then I am redirected to the Home page

  Scenario: TC003_P03: Subsequent Login After Using Go to Home
    Given I am an Ed administrator with rostering rights
    And I have previously completed the welcome flow
    When I log into the application
    Then I am taken directly to the Home page
    And no welcome screen is displayed

  # Negative Test Scenarios
  Scenario: TC004_N01: Admin Without Rostering Rights Access
    Given I am an Ed administrator without rostering rights
    When I log into the application for the first time
    Then I am taken directly to the Home page
    And no welcome screen is displayed

  Scenario: TC005_N02: Invalid Permission Level Access
    Given I am a user with invalid permission levels
    When I attempt to log into the application
    Then I should see an appropriate error message
    And I should not see the welcome screen

  Scenario: TC006_N03: Session Timeout During Welcome Flow
    Given I am an Ed administrator with rostering rights
    And I am on the "Let's Get Started" screen
    When my session times out
    And I refresh the page
    Then I should be redirected to the login page
    And after logging in again, I should see the "Let's Get Started" screen

  # Functional Test Scenarios
  Scenario: TC007_F01: Welcome Message Display Timing
    Given I am an Ed administrator with rostering rights
    When I log into the application for the first time
    Then the "Welcome {Name}" message is displayed
    And the message remains visible for exactly 1000ms
    And the message smoothly transitions to "Let's Get Started" screen

  Scenario: TC008_F02: Button States and Interactions
    Given I am on the "Let's Get Started" screen
    Then both "Go to Home" and "Configure Settings" buttons are visible
    And both buttons are enabled and clickable
    And both buttons have the correct styling as per design
    When I hover over each button
    Then the appropriate hover state is displayed

  Scenario: TC009_F03: Welcome Screen State Persistence
    Given I am an Ed administrator with rostering rights
    And I am on the "Let's Get Started" screen
    When I refresh the browser
    Then I should still see the "Let's Get Started" screen
    And both navigation options should be available

  # Non-Functional Test Scenarios
  Scenario: TC010_NF01: Performance - Welcome Screen Load Time
    Given I am an Ed administrator with rostering rights
    When I log into the application
    Then the welcome screen should load within 2 seconds
    And the transition animation should be smooth without frame drops

  Scenario: TC011_NF02: Accessibility Testing
    Given I am on the "Let's Get Started" screen
    Then all elements should be keyboard navigable
    And screen readers should properly announce all elements
    And color contrast ratios should meet WCAG 2.1 standards
    And both buttons should be usable with keyboard shortcuts

  Scenario Outline: TC012_NF03: Multi-browser Compatibility
    Given I am an Ed administrator with rostering rights
    When I access the application on "<browser>"
    Then the welcome flow should work consistently
    Examples:
      | browser           |
      | Chrome           |
      | Firefox          |
      | Safari           |
      | Edge             |

  # Edge Cases
  Scenario: TC013_E01: Network Interruption During Transition
    Given I am an Ed administrator with rostering rights
    And I am seeing the welcome message
    When the network connection is interrupted
    Then the transition should either complete or gracefully fail
    And the system should retain my first-login status

  Scenario: TC014_E02: Multiple Rapid Logins
    Given I am an Ed administrator with rostering rights
    When I log in and out 5 times in rapid succession
    Then each login should correctly respect the welcome flow status
    And no duplicate welcome screens should appear

  Scenario: TC015_E03: Feature Flag Toggle During Session
    Given I am on the "Let's Get Started" screen
    When the welcome-screen feature flag is disabled
    And I refresh the page
    Then I should be redirected to the Home page
    And subsequent logins should bypass the welcome flow

  # Security Test Scenarios
  Scenario: TC016_S01: Welcome Flow URL Direct Access
    Given I am not logged in
    When I try to directly access the welcome screen URL
    Then I should be redirected to the login page
    And after logging in, the correct flow should be followed

  Scenario: TC017_S02: Cross-Site Scripting Protection
    Given I am an Ed administrator with rostering rights
    And my name contains potentially malicious characters
    When I log in to see the welcome message
    Then the name should be properly escaped
    And no script injection should be possible

  Scenario: TC018_S03: Permission Elevation Attempt
    Given I am an Ed administrator without rostering rights
    When I attempt to modify my permissions during the session
    Then I should still bypass the welcome screen
    And be directed to the Home page
