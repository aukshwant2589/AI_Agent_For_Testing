"""JIRA AI Analyzer with learning capabilities for test case generation"""

import logging
import json
from datetime import datetime
from typing import Dict, List, Optional, Tuple

from src.core.test_case_analyzer import TestCaseAnalyzer
from src.core.test_case_feedback import TestCaseMemory, TestCasePattern, TestCaseFeedback

logger = logging.getLogger(__name__)

class JIRAAIAnalyzer:
    """Enhanced JIRA analyzer with AI integration and learning capabilities"""
    
    def __init__(self, config: Dict):
        """Initialize the analyzer with configuration"""
        self.config = config
        self.analyzer = TestCaseAnalyzer()
        self.memory = TestCaseMemory()
        
    def analyze_issue(self, issue_data: Dict) -> Dict:
        """Analyze a JIRA issue and generate test cases"""
        try:
            # Debug print of issue data
            logger.info("Analyzing issue data:")
            logger.info(f"Summary: {issue_data.get('summary', 'N/A')}")
            logger.info(f"Description: {issue_data.get('description', 'N/A')}")
            logger.info(f"Test Requirements: {json.dumps(issue_data.get('test_requirements', {}), indent=2)}")
            
            # Extract requirements and store in context
            self.context = {
                'issue_data': issue_data,
                'requirements': issue_data.get('test_requirements', {})
            }
            
            # Extract issue type and key features
            feature_type = self._determine_feature_type(issue_data)
            
            # Look for relevant pattern
            pattern = None
            if feature_type:
                pattern = self.memory.get_best_pattern(feature_type)
                
            # Generate test cases using pattern if available
            test_cases = self._generate_test_cases(issue_data, pattern)
            
            # Analyze and enhance test cases
            enhanced_cases = []
            for test_case in test_cases:
                quality_score, metrics = self.analyzer.analyze_test_case(test_case)
                suggestions = self.analyzer.provide_improvement_suggestions(test_case, metrics)
                
                # Apply improvements based on suggestions
                improved_case = self._enhance_test_case(test_case, suggestions)
                
                # Store feedback
                self._store_test_feedback(
                    improved_case,
                    quality_score,
                    metrics,
                    suggestions,
                    pattern.pattern_id if pattern else None
                )
                
                enhanced_cases.append(improved_case)
                
            # Learn from successful tests
            if len(enhanced_cases) >= 3:  # Need multiple cases to extract patterns
                successful_cases = [
                    case for case in enhanced_cases
                    if self.analyzer.analyze_test_case(case)[0] >= 0.8  # High quality threshold
                ]
                if successful_cases:
                    new_pattern = self.memory.extract_pattern(successful_cases)
                    if new_pattern:
                        self.memory.add_pattern(new_pattern)
                        
            return {
                'test_cases': enhanced_cases,
                'analysis': {
                    'pattern_used': pattern.pattern_id if pattern else None,
                    'quality_metrics': [
                        self.analyzer.analyze_test_case(case)[1]
                        for case in enhanced_cases
                    ],
                    'learning_stats': self.memory.analyze_patterns()
                }
            }
            
        except Exception as e:
            logger.error(f"Error analyzing issue: {str(e)}", exc_info=True)
            return {'error': str(e)}
            
    def _determine_feature_type(self, issue_data: Dict) -> Optional[str]:
        """Determine the feature type from issue data"""
        # Extract text from various fields
        text_content = [
            issue_data.get('summary', ''),
            issue_data.get('description', ''),
            *issue_data.get('labels', []),
            issue_data.get('issuetype', {}).get('name', '')
        ]
        combined_text = ' '.join(text_content).lower()
        
        # Feature type keywords
        type_indicators = {
            'login': ['login', 'authentication', 'credentials', 'password'],
            'data_validation': ['validation', 'verify', 'check', 'data quality'],
            'api_test': ['api', 'endpoint', 'service', 'request', 'response'],
            'ui_test': ['ui', 'interface', 'button', 'click', 'form'],
            'database_test': ['database', 'db', 'query', 'data', 'storage']
        }
        
        # Score each type based on keyword matches
        type_scores = {
            feature_type: sum(1 for keyword in keywords if keyword in combined_text)
            for feature_type, keywords in type_indicators.items()
        }
        
        # Get the type with highest score
        if max(type_scores.values(), default=0) > 0:
            return max(type_scores.items(), key=lambda x: x[1])[0]
            
        return None
        
    def _generate_test_cases(
        self,
        issue_data: Dict,
        pattern: Optional[TestCasePattern]
    ) -> List[Dict]:
        """Generate test cases using AI model and pattern guidance"""
        test_cases = []
        
        try:
            # Prepare the prompt using pattern if available
            prompt = self._prepare_generation_prompt(issue_data, pattern)
            
            # Generate test cases using AI (placeholder for actual AI call)
            # This would be replaced with actual AI model integration
            generated_cases = self._call_ai_model(prompt)
            
            # Post-process and validate generated cases
            for case in generated_cases:
                processed_case = self._post_process_test_case(case, pattern)
                if self._validate_test_case(processed_case):
                    test_cases.append(processed_case)
                    
        except Exception as e:
            logger.error(f"Error generating test cases: {str(e)}", exc_info=True)
            
        return test_cases
        
    def _prepare_generation_prompt(
        self,
        issue_data: Dict,
        pattern: Optional[TestCasePattern]
    ) -> str:
        """Prepare the prompt for test case generation"""
        prompt_parts = [
            f"Generate test cases for: {issue_data.get('summary', '')}",
            f"Description: {issue_data.get('description', '')}",
            "Requirements:",
            "- Include detailed steps",
            "- Specify test data",
            "- Define expected results",
        ]
        
        if pattern:
            prompt_parts.extend([
                "Follow this pattern:",
                f"Step structure: {json.dumps(pattern.steps_pattern, indent=2)}",
                f"Test data structure: {json.dumps(pattern.test_data_pattern, indent=2)}"
            ])
            
        return '\n'.join(prompt_parts)
        
    def _call_ai_model(self, prompt: str) -> List[Dict]:
        """Call the AI model to generate test cases"""
        # Get test cases based on prompt context
        if not hasattr(self, 'context'):
            self.context = {'issue_data': {}, 'requirements': {}}
            
        issue_data = self.context.get('issue_data', {})
        summary = issue_data.get('summary', '')
        test_focus = issue_data.get('test_focus_areas', [])
        security_reqs = issue_data.get('security_requirements', [])
        test_complexity = issue_data.get('test_complexity', 'Medium')
        
        test_cases = []
        
        # Define test scenarios based on ticket type
        scenarios = {
            'functional': [
                ('Verify Teacher Login', 'Test teacher login functionality with valid credentials'),
                ('Verify Class Creation', 'Test creating a new class with valid details'),
                ('Verify Student Addition', 'Test adding a new student to the class'),
                ('Verify Class Navigation', 'Test navigation to newly created class')
            ],
            'security': [
                ('Verify Login Security', 'Test login security controls and authentication'),
                ('Verify Role Access', 'Test teacher role access restrictions'),
                ('Verify Data Protection', 'Test protection of student and class data'),
                ('Verify Session Handling', 'Test secure session management')
            ],
            'performance': [
                ('Verify Response Time', 'Test system response time under normal load'),
                ('Verify Class Load Time', 'Test class page loading performance'),
                ('Verify Student List Load', 'Test performance with large student lists'),
                ('Verify Concurrent Access', 'Test system behavior with multiple users')
            ],
            'edge_cases': [
                ('Verify Large Class Size', 'Test handling of large number of students'),
                ('Verify Special Characters', 'Test handling of special characters in inputs'),
                ('Verify Boundary Conditions', 'Test system limits and boundaries'),
                ('Verify Error Scenarios', 'Test various error conditions and recovery')
            ],
            'validation': [
                ('Verify Input Validation', 'Test validation of input fields and data'),
                ('Verify Required Fields', 'Test handling of required field validation'),
                ('Verify Data Formats', 'Test validation of data formats and types'),
                ('Verify Field Limits', 'Test input field length and size limits')
            ]
        }
        
        # Generate test cases for each category
        for category, category_scenarios in scenarios.items():
            # Skip performance tests for low complexity tickets
            if category == 'performance' and test_complexity == 'Low':
                continue
                
            for name, desc in category_scenarios:
                # Format the test case steps
                if 'test_data' not in locals():
                    test_data = self._generate_test_data(desc, category)
                    
                steps = []
                
                # Add preconditions
                steps.append(f"Given I am on the login page at {test_data['inputs'].get('url', 'https://cert.hmhco.com/ui/login/')}")
                steps.append(f"And I have valid teacher credentials:")
                steps.append(f"  | username | {test_data['inputs'].get('username', 'Auksh123')} |")
                steps.append(f"  | password | {test_data['inputs'].get('password', 'Pass@123')} |")
                
                # Add main test steps
                if category == 'functional':
                    if 'login' in name.lower():
                        steps.extend([
                            "When I enter my credentials",
                            "And I click the login button",
                            "Then I should be successfully logged in",
                            "And I should see the teacher dashboard"
                        ])
                    elif 'class' in name.lower():
                        steps.extend([
                            "When I click on 'Manage Rosters'",
                            "And I click 'Create Class'",
                            "And I enter valid class details:",
                            f"  | class_name | {test_data['inputs'].get('class_name', 'Test Class A')} |",
                            "Then the class should be created successfully"
                        ])
                    elif 'student' in name.lower():
                        steps.extend([
                            "When I select the newly created class",
                            "And I click 'Add Students'",
                            "And I enter student details:",
                            f"  | first_name | {test_data['inputs']['student_details'].get('first_name', 'Test')} |",
                            f"  | last_name  | {test_data['inputs']['student_details'].get('last_name', 'Student')} |",
                            "Then the student should be added to the class"
                        ])
                        
                elif category == 'security':
                    steps.extend([
                        "When I attempt to access the page",
                        "Then proper authentication should be required",
                        "And sensitive data should be properly protected",
                        "And proper role-based access control should be enforced"
                    ])
                    
                elif category == 'performance':
                    steps.extend([
                        f"When I simulate {test_data['inputs'].get('concurrent_users', 10)} concurrent users",
                        f"And I run the test for {test_data['inputs'].get('test_duration', '5m')}",
                        f"Then response time should be less than {test_data['validation'].get('max_response_time', '2s')}",
                        f"And error rate should be less than {test_data['validation'].get('error_rate_threshold', '1%')}"
                    ])
                    
                elif category == 'edge_cases':
                    steps.extend([
                        "When I test with boundary values:",
                        "  | class_size | 0, 1, 100, 1000 |",
                        "  | special_chars | @, #, $, %, & |",
                        "Then the system should handle the edge cases gracefully",
                        "And maintain data integrity"
                    ])
                    
                elif category == 'validation':
                    steps.extend([
                        "When I submit the form with test data",
                        "Then all required fields should be validated",
                        "And proper error messages should be displayed for invalid input",
                        "And data format requirements should be enforced"
                    ])
                    
                # Create the test case
                test_case = {
                    'id': f'TEST-{category}-{len(test_cases) + 1}',
                    'name': name,
                    'description': desc,
                    'category': category,
                    'steps': steps,
                    'test_data': test_data,
                    'priority': self._determine_priority(category, test_complexity),
                    'complexity': test_complexity
                }
                test_cases.append(test_case)
                
        return test_cases
        
    def _determine_priority(self, category: str, complexity: str) -> str:
        """Determine test case priority based on category and complexity"""
        priority_matrix = {
            'security': {
                'Low': 'Medium',
                'Medium': 'High',
                'High': 'High'
            },
            'functional': {
                'Low': 'Medium',
                'Medium': 'Medium',
                'High': 'High'
            },
            'performance': {
                'Low': 'Low',
                'Medium': 'Medium',
                'High': 'High'
            },
            'edge_cases': {
                'Low': 'Low',
                'Medium': 'Medium',
                'High': 'Medium'
            },
            'validation': {
                'Low': 'Medium',
                'Medium': 'Medium',
                'High': 'High'
            }
        }
        
        return priority_matrix.get(category, {}).get(complexity, 'Medium')
                
        return test_cases
        
    def _generate_steps_for_point(self, point: str, category: str) -> List[str]:
        """Generate appropriate steps based on validation point and category"""
        # Get issue details from context
        issue_data = self.context.get('issue_data', {})
        description = issue_data.get('description', '')
        
        # Extract steps from description if available
        manual_steps = []
        if description:
            lines = description.split('\n')
            in_steps = False
            for line in lines:
                line = line.strip()
                if 'Steps:' in line:
                    in_steps = True
                    continue
                if in_steps and line and not line.startswith('URL:'):
                    manual_steps.append(line)
                    
        # Convert manual steps to Gherkin format
        steps = []
        
        # Add setup steps based on category
        if category == 'functional':
            steps.append('Given I am on the login page')
            steps.append('And I have valid teacher credentials')
            
        elif category == 'security':
            steps.append('Given I have a security testing environment')
            steps.append('And I have test credentials')
            
        elif category == 'performance':
            steps.append('Given the system is under normal load')
            steps.append('And performance monitoring is enabled')
            
        else:
            steps.append('Given the test environment is ready')
            
        # Add manual steps in Gherkin format
        for i, step in enumerate(manual_steps):
            if i == 0:
                steps.append(f'When {step}')
            else:
                steps.append(f'And {step}')
                
        # Add validation steps based on category
        if category == 'functional':
            steps.append('Then I should see the teacher dashboard')
            steps.append('And the class should be created successfully')
            
        elif category == 'security':
            steps.append('Then access should be properly controlled')
            steps.append('And sensitive data should be protected')
            
        elif category == 'performance':
            steps.append('Then the response time should be acceptable')
            steps.append('And system resources should be within limits')
            
        elif category == 'error':
            steps.append('Then appropriate error messages should be displayed')
            steps.append('And the system should handle errors gracefully')
            
        elif category == 'edge_cases':
            steps.append('Then edge conditions should be handled properly')
            steps.append('And the system should maintain stability')
            
        else:
            steps.append('Then the operation should complete successfully')
            steps.append('And all data should be properly validated')
            
        return steps
        
    def _generate_expected_result(self, point: str, category: str) -> str:
        """Generate expected result based on validation point and category"""
        # Category-specific expectations
        expectations = {
            'functional': 'System should successfully complete the operation',
            'performance': 'Response time should meet performance requirements',
            'security': 'Security controls should be properly enforced',
            'usability': 'User interface should be intuitive and responsive',
            'data': 'Data should be handled correctly and validated',
            'error': 'System should handle the error gracefully',
            'integration': 'Integration should work as expected'
        }
        
        return expectations.get(category, 'Operation should complete successfully')
        
    def _generate_test_data(self, point: str, category: str) -> Dict:
        """Generate appropriate test data based on validation point and category"""
        issue_data = self.context.get('issue_data', {})
        description = issue_data.get('description', '')
        
        test_data = {
            'inputs': {},
            'validation': {}
        }
        
        # Extract credentials from description if available
        if description:
            lines = description.split('\n')
            for line in lines:
                line = line.strip()
                if line.startswith('username:'):
                    test_data['inputs']['username'] = line.split(':')[1].strip()
                elif line.startswith('Password:'):
                    test_data['inputs']['password'] = line.split(':')[1].strip()
                elif line.startswith('URL:'):
                    # Clean up URL format
                    url = line.split(':')[1].strip()
                    # Remove markdown-style links if present
                    if '|' in url:
                        url = url.split('|')[0]
                    # Remove brackets if present
                    url = url.strip('[]')
                    test_data['inputs']['url'] = url
                    
        # Add category-specific test data
        if category == 'functional':
            test_data['inputs']['class_name'] = 'Test Class A'
            test_data['inputs']['student_details'] = {
                'first_name': 'Test',
                'last_name': 'Student',
                'grade': '9',
                'email': 'test.student@example.com'
            }
            test_data['validation']['expected_pages'] = [
                'login_page',
                'teacher_dashboard',
                'manage_roster',
                'create_class',
                'add_students'
            ]
            
        elif category == 'performance':
            test_data['inputs']['concurrent_users'] = 10
            test_data['inputs']['test_duration'] = '5m'
            test_data['validation']['max_response_time'] = '2s'
            test_data['validation']['error_rate_threshold'] = '1%'
            
        elif category == 'security':
            test_data['inputs']['invalid_tokens'] = [
                'expired_token',
                'invalid_token',
                'tampered_token'
            ]
            test_data['validation']['security_checks'] = [
                'auth_validation',
                'token_validation',
                'role_validation'
            ]
            
        elif category == 'edge_cases':
            test_data['inputs']['class_sizes'] = [0, 1, 100, 1000]
            test_data['inputs']['special_chars'] = ['@', '#', '$', '%', '&']
            test_data['validation']['handling_checks'] = [
                'overflow_check',
                'boundary_check',
                'special_char_check'
            ]
            
        return test_data
        
    def _post_process_test_case(
        self,
        test_case: Dict,
        pattern: Optional[TestCasePattern]
    ) -> Dict:
        """Post-process and enhance generated test case"""
        processed = test_case.copy()
        
        # Ensure required fields
        required_fields = ['id', 'name', 'description', 'steps', 'expected_result', 'test_data']
        for field in required_fields:
            if field not in processed:
                processed[field] = ''
                
        # Apply pattern guidance if available
        if pattern:
            # Enhance steps based on pattern
            if pattern.steps_pattern and processed['steps']:
                processed['steps'] = self._align_steps_with_pattern(
                    processed['steps'],
                    pattern.steps_pattern
                )
                
            # Enhance test data based on pattern
            if pattern.test_data_pattern and processed['test_data']:
                processed['test_data'] = self._align_test_data_with_pattern(
                    processed['test_data'],
                    pattern.test_data_pattern
                )
                
        return processed
        
    def _align_steps_with_pattern(self, steps: List[str], pattern_steps: List[str]) -> List[str]:
        """Align generated steps with pattern steps"""
        aligned_steps = []
        pattern_idx = 0
        
        for step in steps:
            # If we have a pattern step available, use it as guidance
            if pattern_idx < len(pattern_steps):
                pattern_step = pattern_steps[pattern_idx]
                # If current step is similar to pattern step, enhance it
                if self._calculate_step_similarity(step, pattern_step) > 0.5:
                    enhanced_step = self._merge_steps(step, pattern_step)
                    aligned_steps.append(enhanced_step)
                    pattern_idx += 1
                else:
                    aligned_steps.append(step)
            else:
                aligned_steps.append(step)
                
        return aligned_steps
        
    def _calculate_step_similarity(self, step1: str, step2: str) -> float:
        """Calculate similarity between two steps"""
        words1 = set(step1.lower().split())
        words2 = set(step2.lower().split())
        
        if not words1 or not words2:
            return 0.0
            
        intersection = words1.intersection(words2)
        union = words1.union(words2)
        
        return len(intersection) / len(union)
        
    def _merge_steps(self, generated_step: str, pattern_step: str) -> str:
        """Merge generated step with pattern step to create enhanced step"""
        # Extract key components from both steps
        gen_words = set(generated_step.lower().split())
        pat_words = set(pattern_step.lower().split())
        
        # Keep specific details from generated step
        specific_details = [
            word for word in generated_step.split()
            if any(c.isdigit() for c in word)  # Numbers
            or '@' in word  # Emails
            or word.startswith('"') or word.startswith("'")  # Quoted values
        ]
        
        # Use pattern step as base but incorporate specific details
        merged = pattern_step
        for detail in specific_details:
            if detail.lower() not in pat_words:
                merged += f" {detail}"
                
        return merged
        
    def _align_test_data_with_pattern(
        self,
        test_data: Dict,
        pattern_data: Dict
    ) -> Dict:
        """Align test data with pattern structure"""
        aligned_data = {}
        
        # Ensure all pattern fields are present
        for key, value_type in pattern_data.items():
            if key in test_data:
                # Validate and potentially convert the value
                aligned_data[key] = self._validate_and_convert_value(
                    test_data[key],
                    value_type
                )
            else:
                # Use a default value based on type
                aligned_data[key] = self._get_default_value(value_type)
                
        return aligned_data
        
    def _validate_and_convert_value(self, value: any, expected_type: str) -> any:
        """Validate and convert a value to expected type"""
        try:
            if expected_type == 'str':
                return str(value)
            elif expected_type == 'int':
                return int(value)
            elif expected_type == 'float':
                return float(value)
            elif expected_type == 'bool':
                return bool(value)
            elif expected_type == 'dict':
                return dict(value)
            elif expected_type == 'list':
                return list(value)
            else:
                return value
        except (ValueError, TypeError):
            return self._get_default_value(expected_type)
            
    def _get_default_value(self, value_type: str) -> any:
        """Get a default value for a given type"""
        defaults = {
            'str': '',
            'int': 0,
            'float': 0.0,
            'bool': False,
            'dict': {},
            'list': []
        }
        return defaults.get(value_type, None)
        
    def _validate_test_case(self, test_case: Dict) -> bool:
        """Validate a test case has all required components"""
        required_fields = ['id', 'name', 'description', 'steps', 'expected_result']
        return all(
            field in test_case and test_case[field]
            for field in required_fields
        )
        
    def _enhance_test_case(self, test_case: Dict, suggestions: List[str]) -> Dict:
        """Enhance a test case based on improvement suggestions"""
        enhanced = test_case.copy()
        
        for suggestion in suggestions:
            if "Add more specific details" in suggestion:
                enhanced['steps'] = self._enhance_step_details(enhanced['steps'])
            elif "Add missing fields" in suggestion:
                self._add_missing_fields(enhanced)
            elif "Improve test data" in suggestion:
                enhanced['test_data'] = self._enhance_test_data(enhanced['test_data'])
                
        return enhanced
        
    def _enhance_step_details(self, steps: List[str]) -> List[str]:
        """Add more specific details to steps"""
        enhanced_steps = []
        
        for step in steps:
            # Add step number if missing
            if not any(str(i) in step[:2] for i in range(10)):
                step = f"{len(enhanced_steps) + 1}. {step}"
                
            # Ensure step has an action verb
            if not any(verb in step.lower() for verb in [
                'click', 'enter', 'verify', 'check', 'validate',
                'submit', 'select', 'navigate'
            ]):
                step = f"Verify {step}"
                
            enhanced_steps.append(step)
            
        return enhanced_steps
        
    def _add_missing_fields(self, test_case: Dict) -> None:
        """Add missing required fields"""
        if not test_case.get('description'):
            test_case['description'] = f"Test case to verify {test_case.get('name', 'functionality')}"
            
        if not test_case.get('expected_result'):
            test_case['expected_result'] = "Test steps should complete successfully"
            
        if not test_case.get('test_data'):
            test_case['test_data'] = {'inputs': {}, 'validation': {}}
            
    def _enhance_test_data(self, test_data: Dict) -> Dict:
        """Enhance test data with more realistic values"""
        if not test_data:
            return {'inputs': {}, 'validation': {}}
            
        enhanced = test_data.copy()
        
        # Replace common placeholder values
        placeholders = {'test', 'example', 'placeholder', 'xxx', 'value'}
        
        if 'inputs' in enhanced:
            enhanced_inputs = {}
            for key, value in enhanced['inputs'].items():
                if str(value).lower() in placeholders:
                    enhanced_inputs[key] = self._generate_realistic_value(key)
                else:
                    enhanced_inputs[key] = value
            enhanced['inputs'] = enhanced_inputs
            
        return enhanced
        
    def _generate_realistic_value(self, field_name: str) -> str:
        """Generate a realistic value based on field name"""
        field_name = field_name.lower()
        
        if 'email' in field_name:
            return 'user@example.com'
        elif 'name' in field_name:
            return 'John Doe'
        elif 'phone' in field_name:
            return '+1-555-0123'
        elif 'date' in field_name:
            return datetime.now().strftime('%Y-%m-%d')
        else:
            return f'Sample{field_name.title()}'
            
    def _store_test_feedback(
        self,
        test_case: Dict,
        quality_score: float,
        metrics: Dict[str, float],
        suggestions: List[str],
        pattern_id: Optional[str]
    ) -> None:
        """Store feedback for a generated test case"""
        feedback = TestCaseFeedback(
            test_case_id=test_case['id'],
            timestamp=datetime.now(),
            quality_score=quality_score,
            metrics=metrics,
            suggestions=suggestions,
            pattern_used=pattern_id,
            is_successful=quality_score >= 0.7  # Consider tests with score >= 0.7 successful
        )
        
        self.memory.add_feedback(feedback)