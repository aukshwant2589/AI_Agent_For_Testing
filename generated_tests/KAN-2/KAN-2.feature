Feature: Response validation for getScore - Agentic AI

  As a tester
  I want to test Response validation for getScore - Agentic AI
  So that I can ensure quality and reliability


  Background:
    Given the system is running
    And I have required access rights


  Scenario: TC_GETSCORE_01: Retrieve score for a valid student and assessment
    Then The API returns a 200 OK status. The response body's 'data' object contains the 'getScore' field with the correct score information, matching the database record. The response structure and data types are correct.


  Scenario: TC_GETSCORE_02: Attempt to retrieve score with an invalid authentication token
    Then The API returns a 401 Unauthorized or 403 Forbidden status code. The response body contains an appropriate error message indicating an authentication failure.


  Scenario: TC_GETSCORE_03: Request score for a non-existent student
    Then The API returns a 200 OK status. The response body contains an 'errors' array detailing that the student could not be found, or the 'data.getScore' field is null.


  Scenario: TC_GETSCORE_04: Request score for a student who has not taken the assessment
    Then The API returns a 200 OK status. The 'data.getScore' field in the response is null, indicating no score record was found for that student/assessment combination.


  Scenario: TC_GETSCORE_05: Request score for a student with a score of zero
    Then The API returns a 200 OK status. The response body's 'data.getScore.score' field has a value of 0 (integer or float), not null.


  Scenario: TC_GETSCORE_06: Request score using a malformed assessment ID
    Then The API returns a 400 Bad Request status, or a 200 OK with a GraphQL 'errors' array indicating a validation failure for the 'assessmentId' argument.


  Scenario: TC_GETSCORE_07: Basic functionality check without providing required arguments
    Then The API returns a 400 Bad Request status or a 200 OK with a GraphQL validation error in the 'errors' array. The error message should clearly state that a required argument is missing.


  Scenario: TC_GETSCORE_01: Retrieve score for a valid student and assessment
    Then The API returns a 200 OK status. The response body's 'data' object contains the 'getScore' field with the correct score information, matching the database record. The response structure and data types are correct.


  Scenario: TC_GETSCORE_02: Attempt to retrieve score with an invalid authentication token
    Then The API returns a 401 Unauthorized or 403 Forbidden status code. The response body contains an appropriate error message indicating an authentication failure.


  Scenario: TC_GETSCORE_03: Request score for a non-existent student
    Then The API returns a 200 OK status. The response body contains an 'errors' array detailing that the student could not be found, or the 'data.getScore' field is null.


  Scenario: TC_GETSCORE_04: Request score for a student who has not taken the assessment
    Then The API returns a 200 OK status. The 'data.getScore' field in the response is null, indicating no score record was found for that student/assessment combination.


  Scenario: TC_GETSCORE_05: Request score for a student with a score of zero
    Then The API returns a 200 OK status. The response body's 'data.getScore.score' field has a value of 0 (integer or float), not null.


  Scenario: TC_GETSCORE_06: Request score using a malformed assessment ID
    Then The API returns a 400 Bad Request status, or a 200 OK with a GraphQL 'errors' array indicating a validation failure for the 'assessmentId' argument.


  Scenario: TC_GETSCORE_07: Basic functionality check without providing required arguments
    Then The API returns a 400 Bad Request status or a 200 OK with a GraphQL validation error in the 'errors' array. The error message should clearly state that a required argument is missing.
