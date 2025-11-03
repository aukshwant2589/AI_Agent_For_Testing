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
            jira_username = os.environ.get("JIRA_USERNAME")
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
            if not gemini_api_key:
                logger.warning("GEMINI_API_KEY not found, using rule-based test generation")
                self.ai_available = False
                return
                
            try:
                genai.configure(api_key=gemini_api_key)
                
                # Check if we're using a free or paid API key
                try:
                    # Quick test call to check quota type
                    test_model = genai.GenerativeModel('gemini-pro')
                    test_model.generate_content("test")
                except Exception as e:
                    if "free_tier" in str(e).lower():
                        logger.warning("⚠️ Using Gemini API free tier (2 requests/min limit)")
                        logger.warning("Consider upgrading to paid tier for better performance")
                
                # Initialize our preferred model
                try:
                    model_name = 'models/gemini-2.5-pro'
                    self.ai_model = genai.GenerativeModel(model_name)
                    logger.info(f"✅ AI client initialized with model: {model_name}")
                    self.ai_available = True
                except Exception as model_e:
                    logger.warning(f"Failed to initialize preferred model: {model_e}")
                    
                    # Try fallback models
                    fallback_models = ['gemini-pro', 'gemini-1.0-pro']
                    for model in fallback_models:
                        try:
                            self.ai_model = genai.GenerativeModel(model)
                            logger.info(f"✅ AI client initialized with fallback model: {model}")
                            self.ai_available = True
                            break
                        except Exception:
                            continue
                            
                    if not self.ai_available:
                        logger.warning("No suitable AI models available")
                            
            except Exception as e:
                logger.error(f"AI client initialization failed: {e}")
                self.ai_available = False

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

            # Generate test cases based on availability
            test_cases = []
            if self.ai_available and self.ai_model:
                try:
                    logger.info("🚀 Attempting AI-powered test generation...")
                    test_cases = self.generate_test_cases_with_ai(ticket_data)
                    
                    if test_cases:
                        logger.info(f"✅ Generated {len(test_cases)} test cases with AI")
                except KeyboardInterrupt:
                    logger.info("\n\n⏳ Rate limit detected. Options:")
                    logger.info("1. Wait ~60 seconds for rate limit to reset")
                    logger.info("2. Use rule-based generation instead")
                    logger.info("3. Upgrade to paid API tier for higher limits")
                    
                    choice = input("\nPress Enter to use rule-based generation, or 'w' to wait: ")
                    if choice.lower() == 'w':
                        logger.info("Waiting 60 seconds...")
                        time.sleep(60)
                        try:
                            test_cases = self.generate_test_cases_with_ai(ticket_data)
                        except:
                            logger.info("🔄 Still rate limited, using rule-based generation")
                            test_cases = self.generate_rule_based_test_cases(ticket_data)
                    else:
                        logger.info("🔄 Using rule-based test generation")
                        test_cases = self.generate_rule_based_test_cases(ticket_data)
                        
            if not test_cases:
                logger.info("🔄 Falling back to rule-based generation")
                test_cases = self.generate_rule_based_test_cases(ticket_data)

            if not test_cases:
                return self._error_response("Failed to generate test cases", ticket_id)

            # Create test scripts
            try:
                self.create_test_scripts(test_cases, ticket_id)
                logger.info("✅ Test scripts generated successfully")
            except Exception as e:
                logger.error(f"Failed to create test scripts: {e}")

            return self._success_response(ticket_data, test_cases, ticket_id)
            
        except KeyboardInterrupt:
            logger.info("\n\n⚠️ Operation cancelled by user")
            return self._error_response("Operation cancelled", ticket_id)
        except Exception as e:
            logger.error(f"Unexpected error: {e}")
            return self._error_response(str(e), ticket_id)

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
        """Extract ticket ID from JIRA URL with proper validation"""
        try:
            # Remove any query parameters
            jira_url = jira_url.split('?')[0]
            
            # Handle different URL formats
            if "/browse/" in jira_url:
                ticket_id = jira_url.split("/browse/")[-1]
            elif "/jira/browse/" in jira_url:
                ticket_id = jira_url.split("/jira/browse/")[-1]
            else:
                # Assume it's already a ticket ID
                ticket_id = jira_url.strip()
            
            # Validate ticket ID format (PROJECT-NUMBER)
            if not re.match(r'^[A-Za-z]+-\d+$', ticket_id):
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
            max_retries = 3  # Reduced retries since we're handling rate limits better
            
            # Enhanced retry logic with proper rate limit handling
            for attempt in range(max_retries):
                try:
                    # Log attempt information
                    if attempt > 0:
                        logger.info(f"Retry attempt {attempt + 1}/{max_retries}")
                    
                    # Make the API call
                    response = self.ai_model.generate_content(prompt)
                    
                    if not response or not response.text:
                        logger.error("Empty response from AI model")
                        continue

                    logger.info(f"✅ AI response received: {len(response.text)} characters")
                    
                    # Parse AI response
                    test_cases = self.parse_ai_response(response.text, ticket_data)
                    
                    if test_cases:
                        logger.info(f"✅ Successfully generated {len(test_cases)} test cases with AI")
                        return test_cases
                    else:
                        logger.warning("AI failed to generate valid test cases")
                        time.sleep(5)  # Brief pause before retry
                        continue
                        
                except Exception as e:
                    error_msg = str(e).lower()
                    error_str = str(e)
                    
                    # Check for rate limit retry delay in the error message
                    retry_match = re.search(r'retry in (\d+\.?\d*)', error_str)
                    if retry_match:
                        wait_seconds = float(retry_match.group(1))
                        logger.warning(f"Rate limit reached. Waiting {wait_seconds:.1f} seconds as advised by API...")
                        time.sleep(wait_seconds + 1)  # Add 1 second buffer
                        continue
                        
                    if "quota" in error_msg or "rate" in error_msg or "429" in error_msg:
                        # Default wait time for other quota/rate limit errors
                        wait_time = 60 if attempt == 0 else 120
                        logger.warning(f"API quota exceeded, waiting {wait_time} seconds...")
                        time.sleep(wait_time)
                        continue
                        
                    logger.error(f"Unexpected error during AI generation: {e}")
                    return []
            
            logger.error(f"Failed to generate test cases after {max_retries} attempts")
            if self.ai_available:
                logger.info("🔄 Falling back to rule-based test generation...")
                return []  # Let the caller fall back to rule-based generation

        except Exception as e:
            logger.error(f"AI generation failed: {e}")
            return []

    def create_ai_prompt(self, ticket_data: Dict) -> str:
        """Create detailed AI prompt for test case generation"""
        description = ticket_data.get('description', '')
        if len(description) > 1500:
            description = description[:1500] + "... [truncated]"
        
        # Analyze content for test type and specifics
        content = description.lower()
        patterns = {
            'API': ['api', 'endpoint', 'request', 'response', 'http', 'rest'],
            'UI': ['ui', 'page', 'screen', 'button', 'click', 'display'],
            'Security': ['login', 'auth', 'token', 'password', 'credential'],
            'Performance': ['performance', 'load', 'stress', 'speed', 'timeout']
        }
        
        test_type = 'Functional'
        test_focus = []
        for type_name, keywords in patterns.items():
            if any(word in content for word in keywords):
                test_type = type_name
                test_focus.extend(kw for kw in keywords if kw in content)
                
        test_focus = list(set(test_focus))  # Remove duplicates
        
        # Build a targeted AI prompt
        prompt = f"""You are a senior QA automation engineer. Generate test cases for this {test_type} testing ticket.

TICKET INFORMATION:
ID: {ticket_data.get('key', '')}
Summary: {ticket_data.get('summary', '')}
Description: {description}
Type: {ticket_data.get('issue_type', '')}
Priority: {ticket_data.get('priority', '')}

{'Key Areas: ' + ', '.join(test_focus) if test_focus else ''}

INSTRUCTIONS:
1. Generate 4-6 detailed {test_type} test cases
2. Return ONLY a valid JSON array following this exact format:
[
  {{
    "id": "TC01",
    "name": "Brief descriptive name",
    "description": "What this test verifies",
    "type": "{test_type}",
    "priority": "High|Medium|Low",
    "steps": [
      "1. Detailed step one",
      "2. Detailed step two"
    ],
    "expected_result": "Specific expected outcome",
    "test_data": {{
      "inputs": {{"field1": "actual value"}},
      "validation": {{"expected": "expected value"}}
    }}
  }}
]

IMPORTANT:
- Ensure each test case has specific steps, not generic ones
- Include realistic test data, not placeholders
- Consider error cases and edge cases
- The response must be properly formatted JSON only, no other text"""
        
        return prompt

    def parse_ai_response(self, ai_response: str, ticket_data: Dict) -> List[Dict]:
        """Parse and validate AI response into well-structured test cases"""
        try:
            # Log the raw response in debug mode
            logger.debug(f"Raw AI response: {ai_response}")
            
            # Clean the response step by step
            cleaned = ai_response.strip()
            
            # Remove any markdown code blocks
            cleaned = re.sub(r'```(?:json)?\s*(.*?)\s*```', r'\1', cleaned, flags=re.DOTALL)
            
            # Remove any non-JSON text before or after
            json_match = re.search(r'\[\s*\{.*?\}\s*\]', cleaned, re.DOTALL)
            if not json_match:
                logger.error("No JSON array found in response")
                logger.debug(f"Cleaned response: {cleaned}")
                return []
                
            json_str = json_match.group(0)
            
            # Try to parse the JSON
            try:
                test_cases = json.loads(json_str)
            except json.JSONDecodeError as je:
                logger.error(f"JSON parse error at position {je.pos}: {je.msg}")
                logger.debug(f"Invalid JSON: {json_str}")
                return []
            
            # Must be a list
            if not isinstance(test_cases, list):
                logger.error("Response is not a JSON array")
                return []
            
            # Validate and clean test cases
            valid_test_cases = []
            for i, tc in enumerate(test_cases, 1):
                if not isinstance(tc, dict):
                    logger.warning(f"Test case {i} is not a JSON object, skipping")
                    continue
                    
                try:
                    if self._validate_test_case(tc):
                        cleaned_tc = self._clean_test_case(tc)
                        valid_test_cases.append(cleaned_tc)
                    else:
                        logger.warning(f"Test case {i} failed validation")
                except Exception as e:
                    logger.warning(f"Error processing test case {i}: {e}")
                    continue
            
            if not valid_test_cases:
                logger.warning("No valid test cases found after validation")
                logger.debug("All test cases failed validation")
                return []
                
            return valid_test_cases

        except Exception as e:
            logger.error(f"Failed to parse AI response: {e}")
            return []
            
    def _validate_test_case(self, tc: Dict) -> bool:
        """Validate individual test case structure and content"""
        try:
            # Basic field presence
            required_fields = ['id', 'name', 'type', 'priority', 'steps', 'expected_result']
            missing = [f for f in required_fields if f not in tc]
            if missing:
                logger.debug(f"Missing required fields: {', '.join(missing)}")
                return False
            
            # Type checking
            field_types = {
                'id': str,
                'name': str,
                'type': str,
                'priority': str,
                'steps': list,
                'expected_result': str
            }
            
            for field, expected_type in field_types.items():
                value = tc.get(field)
                if not isinstance(value, expected_type):
                    logger.debug(f"Field '{field}' has wrong type: {type(value)}, expected {expected_type}")
                    return False
            
            # Content validation
            if not tc['name'].strip():
                logger.debug("Empty test name")
                return False
                
            if not tc['steps']:
                logger.debug("Empty steps list")
                return False
                
            if not tc['expected_result'].strip():
                logger.debug("Empty expected result")
                return False
                
            # Normalize and validate priority
            priority = tc['priority'].strip().title()
            if priority not in ['High', 'Medium', 'Low']:
                logger.debug(f"Invalid priority: {priority}")
                return False
            
            return True
            
        except Exception as e:
            logger.debug(f"Validation error: {e}")
            return False
        
    def _clean_test_case(self, tc: Dict) -> Dict:
        """Clean and normalize test case data"""
        cleaned = {}
        
        # Required fields with specific formats
        tc_id = tc['id']
        if tc_id.isdigit():
            cleaned['id'] = "TC" + tc_id.zfill(2)
        else:
            cleaned['id'] = tc_id
            
        cleaned['name'] = tc['name'].strip()
        cleaned['description'] = tc['description'].strip()
        cleaned['priority'] = tc['priority'].strip().title()
        cleaned['type'] = tc['type'].strip().title()
        
        # Lists that need cleaning
        steps = []
        for i, step in enumerate(tc['steps']):
            step_text = step.strip()
            if step_text:
                if not step_text.startswith(str(i+1)):
                    step_text = f"{i+1}. {step_text}"
                steps.append(step_text)
        cleaned['steps'] = steps
        
        cleaned['prerequisites'] = [
            prereq.strip() for prereq in tc.get('prerequisites', [])
            if prereq.strip()
        ]
        
        # Single string field
        cleaned['expected_result'] = tc.get('expected_result', '').strip()
        
        # Test data structure
        cleaned['test_data'] = {
            'inputs': {
                k.strip(): str(v).strip()
                for k, v in tc.get('test_data', {}).get('inputs', {}).items()
            },
            'validation': {
                k.strip(): str(v).strip()
                for k, v in tc.get('test_data', {}).get('validation', {}).items()
            }
        }
        
        return cleaned

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