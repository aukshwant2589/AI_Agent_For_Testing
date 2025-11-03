Feature: Response validation for getScore - Agentic AI

  As a tester
  I want to test Response validation for getScore - Agentic AI
  So that I can ensure quality and reliability


  Background:
    Given the system is running
    And I have required access rights


  Scenario: TC1: Verify getScore for a valid student with an existing score
    Then The API returns a 200 OK status. The response body contains the correct score data, matching the expected schema (e.g., studentId, score, assessmentDate). The 'errors' field in the response is null or empty.


  Scenario: TC2: Verify API response with an invalid authentication token
    Then The API returns a 401 Unauthorized (or similar authentication error) status code. The response body contains a clear error message indicating authentication failure.


  Scenario: TC3: Verify getScore for a non-existent student ID
    Then The API returns a 200 OK status, as is standard for GraphQL. The 'data.getScore' field is null, and the 'errors' array contains a descriptive error message indicating the resource was not found.


  Scenario: TC4: Verify getScore for a valid student with no score data
    Then The API returns a 200 OK status. The response 'data.getScore' field is null, indicating no data is available. The 'errors' field is empty, as this is a valid state, not a technical error.


  Scenario: TC5: Verify getScore with a malformed GraphQL query
    Then The API returns a 400 Bad Request status code. The response 'errors' array clearly indicates a GraphQL syntax or validation error.


  Scenario: TC6: Verify the response schema and data types are correct
    Then The response contains all expected fields, and the data type for each field is correct (e.g., 'studentId' is a string, 'scoreValue' is a number).


  Scenario: TC7: Verify the API response time is within the acceptable SLA
    Then The total response time for the API call is less than the defined threshold (e.g., < 800ms).


  Scenario: TC1: Verify getScore for a valid student with an existing score
    Then The API returns a 200 OK status. The response body contains the correct score data, matching the expected schema (e.g., studentId, score, assessmentDate). The 'errors' field in the response is null or empty.


  Scenario: TC2: Verify API response with an invalid authentication token
    Then The API returns a 401 Unauthorized (or similar authentication error) status code. The response body contains a clear error message indicating authentication failure.


  Scenario: TC3: Verify getScore for a non-existent student ID
    Then The API returns a 200 OK status, as is standard for GraphQL. The 'data.getScore' field is null, and the 'errors' array contains a descriptive error message indicating the resource was not found.


  Scenario: TC4: Verify getScore for a valid student with no score data
    Then The API returns a 200 OK status. The response 'data.getScore' field is null, indicating no data is available. The 'errors' field is empty, as this is a valid state, not a technical error.


  Scenario: TC5: Verify getScore with a malformed GraphQL query
    Then The API returns a 400 Bad Request status code. The response 'errors' array clearly indicates a GraphQL syntax or validation error.


  Scenario: TC6: Verify the response schema and data types are correct
    Then The response contains all expected fields, and the data type for each field is correct (e.g., 'studentId' is a string, 'scoreValue' is a number).


  Scenario: TC7: Verify the API response time is within the acceptable SLA
    Then The total response time for the API call is less than the defined threshold (e.g., < 800ms).
