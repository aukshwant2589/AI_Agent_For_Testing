from crewai import Agent
from langchain.tools import tool
from langchain.llms import OpenAI
from typing import List, Dict
from ..core.config_manager import config, logger


class RequirementAnalyzerAgent:
    """AI Agent for analyzing and interpreting test requirements"""

    def __init__(self):
        self.llm = OpenAI(temperature=0.1)
        self.agent = self._create_agent()

    def _create_agent(self) -> Agent:
        """Create the requirement analyzer agent"""
        return Agent(
            role='Senior Test Requirement Analyst',
            goal='Analyze and interpret complex test requirements to create comprehensive test strategies',
            backstory="""You are an expert test analyst with decades of experience in interpreting complex 
            requirements and transforming them into actionable test plans. You have a keen eye for 
            identifying edge cases, boundary conditions, and potential failure points that others might miss.""",
            verbose=True,
            allow_delegation=False,
            tools=[self._analyze_requirement_tool, self._generate_test_scenarios_tool],
            llm=self.llm
        )

    @tool
    def _analyze_requirement_tool(self, requirement: str) -> Dict:
        """Analyze a requirement and identify test scenarios"""
        try:
            analysis = {
                'requirement': requirement,
                'test_scenarios': [],
                'edge_cases': [],
                'risk_assessment': {},
                'complexity_score': 0
            }

            complexity_keywords = ['complex', 'integrate', 'multiple', 'system', 'api', 'database']
            analysis['complexity_score'] = sum(1 for word in complexity_keywords if word in requirement.lower())

            if 'login' in requirement.lower():
                analysis['test_scenarios'].extend([
                    'Successful login with valid credentials',
                    'Failed login with invalid credentials',
                    'Login with empty credentials',
                    'Login with SQL injection payload',
                    'Login with XSS payload',
                    'Login rate limiting',
                    'Session management after login'
                ])
                analysis['edge_cases'].extend([
                    'Very long username/password',
                    'Special characters in credentials',
                    'Concurrent login attempts',
                    'Login after session timeout'
                ])

            if 'form' in requirement.lower():
                analysis['test_scenarios'].extend([
                    'Form submission with valid data',
                    'Form validation with invalid data',
                    'Required field validation',
                    'Cross-site scripting prevention',
                    'SQL injection prevention',
                    'File upload validation',
                    'Form reset functionality'
                ])

            analysis['risk_assessment'] = {
                'high_risk': len([s for s in analysis['test_scenarios'] if 'injection' in s or 'XSS' in s]),
                'medium_risk': len(analysis['test_scenarios']) // 2,
                'low_risk': len(analysis['test_scenarios']) // 4
            }

            return analysis

        except Exception as e:
            logger.error(f"Requirement analysis failed: {e}")
            return {'error': str(e)}

    @tool
    def _generate_test_scenarios_tool(self, analysis: Dict) -> List[Dict]:
        """Generate detailed test scenarios from requirement analysis"""
        scenarios = []

        for scenario in analysis.get('test_scenarios', []):
            scenarios.append({
                'name': scenario,
                'priority': self._determine_priority(scenario),
                'estimated_time': self._estimate_execution_time(scenario),
                'test_data_requirements': self._identify_test_data_needs(scenario),
                'preconditions': self._identify_preconditions(scenario),
                'expected_results': self._define_expected_results(scenario)
            })

        return scenarios

    def _determine_priority(self, scenario: str) -> str:
        """Determine test scenario priority"""
        high_priority_keywords = ['security', 'injection', 'XSS', 'authentication', 'payment']
        medium_priority_keywords = ['validation', 'integration', 'performance']

        if any(keyword in scenario.lower() for keyword in high_priority_keywords):
            return 'HIGH'
        elif any(keyword in scenario.lower() for keyword in medium_priority_keywords):
            return 'MEDIUM'
        else:
            return 'LOW'

    def _estimate_execution_time(self, scenario: str) -> int:
        """Estimate execution time in seconds"""
        if 'security' in scenario.lower():
            return 120
        elif 'performance' in scenario.lower():
            return 180
        elif 'integration' in scenario.lower():
            return 90
        else:
            return 60

    def _identify_test_data_needs(self, scenario: str) -> List[str]:
        """Identify test data requirements"""
        needs = ['valid test data', 'invalid test data']

        if 'login' in scenario.lower():
            needs.extend(['valid credentials', 'invalid credentials', 'edge case credentials'])
        if 'form' in scenario.lower():
            needs.extend(['boundary values', 'special characters', 'max length data'])

        return needs

    def _identify_preconditions(self, scenario: str) -> List[str]:
        """Identify test preconditions"""
        preconditions = ['System is available', 'Test environment is prepared']

        if 'login' in scenario.lower():
            preconditions.append('User account exists')
        if 'database' in scenario.lower():
            preconditions.append('Database is accessible')

        return preconditions

    def _define_expected_results(self, scenario: str) -> List[str]:
        """Define expected results for test scenario"""
        if 'successful' in scenario.lower():
            return ['Operation completes successfully', 'Correct response is received']
        elif 'failed' in scenario.lower():
            return ['Appropriate error message is displayed', 'System handles error gracefully']
        elif 'security' in scenario.lower():
            return ['Security controls are effective', 'Vulnerability is prevented']
        else:
            return ['Expected behavior is observed']