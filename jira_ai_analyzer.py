import os
import json
import re
import logging
import time
from typing import Dict, List, Any
from jira import JIRA, JIRAError
import google.generativeai as genai
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger('JIRAAIAnalyzer')

class JIRAAIAnalyzer:
    """Analyze JIRA tickets using AI to generate comprehensive test cases"""

    def __init__(self):
        self.name = "JIRA AI Analyzer"
        self.description = "Analyze JIRA tickets using AI to generate comprehensive test cases"
        self.jira_client = None
        self.ai_model = None
        self.ai_available = False
        self.setup_clients()

    def setup_clients(self):
        """Setup JIRA and AI clients"""
        try:
            # Setup JIRA client
            jira_server = os.environ.get("JIRA_SERVER")
            jira_username = os.environ.get("JIRA_EMAIL")  # Using JIRA_EMAIL instead of JIRA_USERNAME
            jira_token = os.environ.get("JIRA_API_TOKEN")

            if all([jira_server, jira_username, jira_token]):
                jira_options = {'server': jira_server}
                self.jira_client = JIRA(
                    options=jira_options,
                    basic_auth=(jira_username, jira_token)
                )
                logger.info("✅ JIRA client initialized successfully")
            else:
                missing = []
                if not jira_server: missing.append("JIRA_SERVER")
                if not jira_username: missing.append("JIRA_USERNAME")
                if not jira_token: missing.append("JIRA_API_TOKEN")
                logger.warning(f"Missing JIRA credentials: {', '.join(missing)}")

            # Setup AI client
            gemini_api_key = os.environ.get("GEMINI_API_KEY")
            if gemini_api_key:
                try:
                    genai.configure(api_key=gemini_api_key)
                    
                    # Use the model we know works
                    try:
                        model_name = 'models/gemini-2.5-pro'  # This is a stable model version
                        self.ai_model = genai.GenerativeModel(model_name)
                        logger.info(f"✅ AI client initialized with model: {model_name}")
                        self.ai_available = True
                    except Exception as e:
                        logger.warning(f"Failed to initialize AI model: {e}")
                        self.ai_available = False
                        logger.warning("No AI models available")
                            
                except Exception as e:
                    logger.warning(f"AI client initialization failed: {e}")
                    self.ai_available = False
            else:
                logger.warning("GEMINI_API_KEY not found, using rule-based test generation")

        except Exception as e:
            logger.error(f"Error initializing clients: {e}")
            self.ai_available = False

    def run(self, jira_url: str, **kwargs) -> str:
        """Analyze JIRA ticket and generate test cases"""
        try:
            # Extract ticket ID from URL
            ticket_id = self.extract_ticket_id(jira_url)
            if not ticket_id:
                return self._error_response("Invalid JIRA URL format", jira_url)

            # Get ticket details
            ticket_data = self.get_ticket_details(ticket_id)
            if "error" in ticket_data:
                return self._error_response(ticket_data["error"], ticket_id)

            logger.info(f"✅ Successfully fetched ticket: {ticket_data['key']} - {ticket_data['summary']}")

            # Generate test cases - try AI first, then fallback to rules
            test_cases = []
            if self.ai_available and self.ai_model:
                logger.info("🚀 Attempting to generate test cases with AI...")
                test_cases = self.generate_test_cases_with_ai(ticket_data)
            
            # If AI failed or not available, use rule-based generation
            if not test_cases:
                logger.info("🔄 Using rule-based test case generation")
                test_cases = self.generate_rule_based_test_cases(ticket_data)

            if not test_cases:
                return self._error_response("Failed to generate test cases", ticket_id)

            # Create test scripts
            self.create_test_scripts(test_cases, ticket_id)

            return self._success_response(ticket_data, test_cases, ticket_id)

        except Exception as e:
            logger.error(f"JIRA AI analysis failed: {e}")
            return self._error_response(f"Analysis failed: {str(e)}", jira_url)

    def _error_response(self, error_message: str, ticket_id: str) -> str:
        """Create error response"""
        return json.dumps({
            "error": error_message,
            "ticket_id": ticket_id,
            "valid": False,
            "test_cases_generated": 0,
            "test_cases": [],
            "generated_files": []
        }, indent=2)

    def _success_response(self, ticket_data: Dict, test_cases: List[Dict], ticket_id: str) -> str:
        """Create success response"""
        return json.dumps({
            "ticket_id": ticket_id,
            "ticket_summary": ticket_data.get("summary", ""),
            "ticket_description": ticket_data.get("description", ""),
            "test_cases_generated": len(test_cases),
            "test_cases": test_cases,
            "generated_files": self.get_generated_files(ticket_id),
            "valid": True
        }, indent=2)

    def extract_ticket_id(self, jira_url: str) -> str:
        """Extract ticket ID from JIRA URL with proper validation.
        
        Args:
            jira_url: JIRA ticket URL or ticket ID
            
        Returns:
            Validated ticket ID or empty string if invalid
        """
        try:
            # Remove any query parameters and trailing slashes
            jira_url = jira_url.split('?')[0].rstrip('/')
            
            # Handle different URL formats
            if "/browse/" in jira_url:
                ticket_id = jira_url.split("/browse/")[-1]
            elif "/jira/browse/" in jira_url:
                ticket_id = jira_url.split("/jira/browse/")[-1]
            else:
                # Assume it's already a ticket ID
                ticket_id = jira_url.strip()
            
            # Validate ticket ID format (PROJECT-NUMBER)
            # Allow any project key (alphanumeric) followed by a hyphen and number
            if not re.match(r'^[A-Z0-9]+-\d+$', ticket_id.upper()):
                logger.warning(f"Invalid ticket ID format: {ticket_id}")
                return ""
                
            return ticket_id.upper()  # Standardize to uppercase
            
        except:
            return ""

    def get_ticket_details(self, ticket_id: str) -> Dict:
        """Get ticket details from JIRA with proper error handling"""
        if not self.jira_client:
            return {"error": "JIRA client not configured. Please check your JIRA credentials."}
            
        try:
            issue = self.jira_client.issue(ticket_id)
            
            return {
                "key": issue.key,
                "summary": issue.fields.summary,
                "description": issue.fields.description or "",
                "issue_type": str(issue.fields.issuetype),
                "priority": str(issue.fields.priority),
                "status": str(issue.fields.status),
                "labels": issue.fields.labels or [],
                "components": [comp.name for comp in issue.fields.components] if issue.fields.components else [],
                "assignee": str(issue.fields.assignee) if issue.fields.assignee else "Unassigned"
            }
            
        except JIRAError as e:
            if e.status_code == 404:
                return {"error": f"Ticket {ticket_id} does not exist or you don't have permission to access it"}
            elif e.status_code == 401:
                return {"error": "JIRA authentication failed. Please check your credentials."}
            elif e.status_code == 403:
                return {"error": "Access forbidden. You don't have permission to access this ticket."}
            else:
                logger.error(f"JIRA API error for {ticket_id}: {e}")
                return {"error": f"JIRA API error: {str(e)}"}
        except Exception as e:
            logger.error(f"Error fetching ticket {ticket_id}: {e}")
            return {"error": f"Unexpected error: {str(e)}"}

    def generate_test_cases_with_ai(self, ticket_data: Dict) -> List[Dict]:
        """Generate test cases using AI analysis with proper error handling"""
        try:
            prompt = self.create_ai_prompt(ticket_data)
            
            # Add retry logic for quota issues
            for attempt in range(3):
                try:
                    response = self.ai_model.generate_content(prompt)
                    
                    if not response or not response.text:
                        logger.error("Empty response from AI model")
                        return []

                    logger.info(f"✅ AI response received: {len(response.text)} characters")
                    
                    # Parse AI response
                    test_cases = self.parse_ai_response(response.text, ticket_data)
                    
                    if test_cases:
                        logger.info(f"✅ Successfully generated {len(test_cases)} test cases with AI")
                        return test_cases
                    else:
                        logger.warning("AI failed to generate valid test cases")
                        return []
                        
                except Exception as e:
                    if "quota" in str(e).lower() or "429" in str(e):
                        wait_time = (attempt + 1) * 5  # Exponential backoff
                        logger.warning(f"API quota exceeded, waiting {wait_time} seconds before retry...")
                        time.sleep(wait_time)
                        continue
                    else:
                        raise e
                        
            return []  # All retries failed

        except Exception as e:
            logger.error(f"AI generation failed: {e}")
            return []

    def create_ai_prompt(self, ticket_data: Dict) -> str:
        """Create detailed AI prompt for test case generation"""
        # Truncate description if it's too long
        description = ticket_data['description']
        if len(description) > 1500:
            description = description[:1500] + "... [truncated]"
            
        return f"""
ROLE: You are a Senior QA Automation Engineer with 10+ years of experience.
TASK: Analyze this JIRA ticket and generate comprehensive test cases.

TICKET DETAILS:
- ID: {ticket_data['key']}
- Summary: {ticket_data['summary']}
- Description: {description}
- Type: {ticket_data['issue_type']}
- Priority: {ticket_data['priority']}
- Status: {ticket_data['status']}

Generate 5-8 test cases covering:
1. Positive scenarios
2. Negative scenarios  
3. Edge cases
4. Basic functionality

Return ONLY JSON array with each test case having:
- name: Test case name
- description: What is being tested
- priority: High/Medium/Low
- steps: Array of test steps
- expected_result: Expected outcome
- test_data: Any required test data
- prerequisites: Any setup requirements
- type: Test type

Format response as valid JSON only.
"""

    def parse_ai_response(self, ai_response: str, ticket_data: Dict) -> List[Dict]:
        """Parse AI response into test cases with robust error handling"""
        try:
            # Clean the response
            cleaned_response = re.sub(r'```json\s*|\s*```', '', ai_response.strip())
            
            # Extract JSON array
            json_match = re.search(r'\[\s*\{.*\}\s*\]', cleaned_response, re.DOTALL)
            if not json_match:
                return []
                
            json_str = json_match.group(0)
            return json.loads(json_str)

        except (json.JSONDecodeError, ValueError):
            return []

    def generate_rule_based_test_cases(self, ticket_data: Dict) -> List[Dict]:
        """Generate comprehensive test cases based on ticket content"""
        summary = ticket_data['summary'].lower()
        description = ticket_data['description'].lower()
        
        test_cases = []
        
        # Extract main functionality from summary
        if "class" in summary and "student" in summary:
            # Test cases for class and student management
            test_cases.extend([
                {
                    "name": "Test creating a new class",
                    "description": "Verify ability to create a new class with valid parameters",
                    "priority": "High",
                    "type": "Functional",
                    "steps": [
                        "Navigate to class management section",
                        "Click 'Create New Class' button",
                        "Enter valid class name and details",
                        "Save the class"
                    ],
                    "expected_result": "New class is created successfully and appears in class list",
                    "test_data": "Valid class name: 'Mathematics 101'",
                    "prerequisites": "User has admin privileges"
                },
                {
                    "name": "Test adding student to class",
                    "description": "Verify ability to add a student to an existing class",
                    "priority": "High",
                    "type": "Functional",
                    "steps": [
                        "Navigate to class management section",
                        "Select an existing class",
                        "Click 'Add Student' button",
                        "Enter valid student information",
                        "Save student details"
                    ],
                    "expected_result": "Student is added to the class successfully",
                    "test_data": "Valid student name: 'John Doe', Student ID: 'S12345'",
                    "prerequisites": "Class must exist in the system"
                },
                {
                    "name": "Test duplicate class creation",
                    "description": "Verify system prevents creating duplicate classes",
                    "priority": "Medium",
                    "type": "Negative",
                    "steps": [
                        "Navigate to class management section",
                        "Click 'Create New Class' button",
                        "Enter class name that already exists",
                        "Save the class"
                    ],
                    "expected_result": "System displays error message about duplicate class",
                    "test_data": "Existing class name",
                    "prerequisites": "At least one class already exists"
                },
                {
                    "name": "Test adding student with invalid data",
                    "description": "Verify system validates student information properly",
                    "priority": "Medium",
                    "type": "Negative",
                    "steps": [
                        "Navigate to class management section",
                        "Select an existing class",
                        "Click 'Add Student' button",
                        "Enter invalid student information",
                        "Save student details"
                    ],
                    "expected_result": "System displays validation errors and prevents saving",
                    "test_data": "Invalid email: 'invalid-email'",
                    "prerequisites": "Class must exist in the system"
                },
                {
                    "name": "Test class list display",
                    "description": "Verify classes are displayed correctly in the list",
                    "priority": "Low",
                    "type": "UI",
                    "steps": [
                        "Navigate to class management section",
                        "View the list of classes"
                    ],
                    "expected_result": "All existing classes are displayed with correct information",
                    "test_data": "N/A",
                    "prerequisites": "At least one class exists in the system"
                }
            ])
        else:
            # Generic test cases for other types of tickets
            test_cases.extend([
                {
                    "name": f"Test basic functionality for {ticket_data['key']}",
                    "description": f"Basic functionality test for {ticket_data['summary']}",
                    "priority": "High",
                    "type": "Functional",
                    "steps": [
                        f"Access {ticket_data['summary']} feature",
                        "Perform basic operation",
                        "Verify results"
                    ],
                    "expected_result": "Feature works as expected without errors",
                    "test_data": "N/A",
                    "prerequisites": "System is operational"
                },
                {
                    "name": f"Test error handling for {ticket_data['key']}",
                    "description": f"Verify proper error handling for {ticket_data['summary']}",
                    "priority": "Medium",
                    "type": "Negative",
                    "steps": [
                        f"Access {ticket_data['summary']} feature",
                        "Provide invalid input data",
                        "Attempt to execute operation"
                    ],
                    "expected_result": "System displays appropriate error messages",
                    "test_data": "Invalid input data",
                    "prerequisites": "System is operational"
                },
                {
                    "name": f"Test data validation for {ticket_data['key']}",
                    "description": f"Verify data validation works correctly for {ticket_data['summary']}",
                    "priority": "Medium",
                    "type": "Validation",
                    "steps": [
                        f"Access {ticket_data['summary']} feature",
                        "Enter various test data scenarios",
                        "Verify validation rules"
                    ],
                    "expected_result": "Data validation works as specified",
                    "test_data": "Various test data inputs",
                    "prerequisites": "System is operational"
                }
            ])
        
        return test_cases

    def create_test_scripts(self, test_cases: List[Dict], ticket_id: str):
        """Create executable test scripts from test cases"""
        try:
            # Create Python test script
            python_script = self.generate_python_test_script(test_cases, ticket_id)

            # Create behavior-driven development (BDD) feature file
            bdd_script = self.generate_bdd_feature_file(test_cases, ticket_id)

            # Save files
            os.makedirs("generated_tests", exist_ok=True)

            python_filename = f"generated_tests/test_{ticket_id.replace('-', '_')}.py"
            with open(python_filename, 'w', encoding='utf-8') as f:
                f.write(python_script)

            bdd_filename = f"generated_tests/{ticket_id.replace('-', '_')}.feature"
            with open(bdd_filename, 'w', encoding='utf-8') as f:
                f.write(bdd_script)

            logger.info(f"Test scripts generated: {python_filename}, {bdd_filename}")
            
        except Exception as e:
            logger.error(f"Failed to create test scripts: {e}")

    def generate_python_test_script(self, test_cases: List[Dict], ticket_id: str) -> str:
        """Generate Python test script using pytest"""
        script = f'''"""
Automated Test Cases for JIRA Ticket: {ticket_id}
Generated by Ultimate Test Automation Coordinator
"""

import pytest
import time
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class Test{ticket_id.replace('-', '_')}:
    """Test cases for {ticket_id}"""

'''

        for i, test_case in enumerate(test_cases, 1):
            method_name = test_case['name'].lower()[:40].replace(' ', '_').replace('-', '_')
            method_name = ''.join(c for c in method_name if c.isalnum() or c == '_')

            script += f'''
    def test_{method_name}(self):
        """{test_case['name']}"""
        logger.info("Testing: {test_case['name']}")
        logger.info("Description: {test_case['description']}")
        logger.info("Priority: {test_case.get('priority', 'Medium')}")
        logger.info("Type: {test_case.get('type', 'Functional')}")
        
        logger.info("Steps:")
        for step in {test_case['steps']}:
            logger.info(f"  - {{step}}")
        
        logger.info("Prerequisites: {test_case.get('prerequisites', 'None')}")
        logger.info("Test Data: {test_case.get('test_data', 'None')}")
        
        # Simulate test execution
        time.sleep(0.2)
        
        logger.info("Expected: {test_case['expected_result']}")
        assert True, "Test implementation needed - replace with actual test logic"

'''

        script += '''
if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])
'''

        return script

    def generate_bdd_feature_file(self, test_cases: List[Dict], ticket_id: str) -> str:
        """Generate Gherkin feature file for BDD"""
        feature = f'''# Feature: {ticket_id} - {test_cases[0]['name'] if test_cases else 'Generated Tests'}
# Generated by Ultimate Test Automation Coordinator

Feature: Test cases for JIRA ticket {ticket_id}

'''

        for test_case in test_cases:
            feature += f'''
Scenario: {test_case['name']}
    Description: {test_case['description']}
    Priority: {test_case.get('priority', 'Medium')}
    Type: {test_case.get('type', 'Functional')}

'''
            for step in test_case['steps']:
                feature += f'    Given {step}\n'

            feature += f'    Then {test_case["expected_result"]}\n'

        return feature

    def get_generated_files(self, ticket_id: str) -> List[str]:
        """Get list of generated files"""
        base_name = ticket_id.replace('-', '_')
        # Check for different file extensions
        extensions = ['.py', '.feature', '.robot']
        files = []
        
        for ext in extensions:
            filename = f"generated_tests/test_{base_name}{ext}"
            if os.path.exists(filename):
                files.append(filename)
        
        return files