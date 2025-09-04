from crewai import Agent
from langchain.tools import tool
from langchain.llms import OpenAI
from typing import List, Dict
from ..core.config_manager import config, logger
from ..utils.edge_case_generator import EdgeCaseGenerator


class TestGeneratorAgent:
    """AI Agent for generating comprehensive test cases"""

    def __init__(self):
        self.llm = OpenAI(temperature=0.3)
        self.edge_case_generator = EdgeCaseGenerator()
        self.agent = self._create_agent()

    def _create_agent(self) -> Agent:
        """Create the test generator agent"""
        return Agent(
            role='Senior Test Automation Engineer',
            goal='Generate comprehensive, robust, and maintainable test cases covering all scenarios',
            backstory="""You are a seasoned test automation expert with expertise in creating tests 
            that catch even the most subtle bugs. You specialize in boundary testing, edge cases, 
            and security testing, ensuring applications are robust and secure.""",
            verbose=True,
            allow_delegation=False,
            tools=[self._generate_test_cases_tool, self._optimize_test_cases_tool],
            llm=self.llm
        )

    @tool
    def _generate_test_cases_tool(self, scenarios: List[Dict]) -> List[Dict]:
        """Generate detailed test cases from scenarios"""
        test_cases = []

        for scenario in scenarios:
            test_case = {
                'name': scenario['name'],
                'description': f"Test for: {scenario['name']}",
                'priority': scenario.get('priority', 'MEDIUM'),
                'steps': self._generate_test_steps(scenario['name']),
                'expected_results': scenario.get('expected_results', ['Test passes']),
                'test_data': self._generate_test_data(scenario['name']),
                'tags': self._generate_tags(scenario['name']),
                'dependencies': scenario.get('preconditions', []),
                'timeout': scenario.get('estimated_time', 60)
            }
            test_cases.append(test_case)

        return test_cases

    def _generate_test_steps(self, scenario_name: str) -> List[str]:
        """Generate test steps based on scenario"""
        steps = []

        if 'login' in scenario_name.lower():
            steps = [
                "Navigate to login page",
                "Enter credentials",
                "Click login button",
                "Verify login result"
            ]
        elif 'form' in scenario_name.lower():
            steps = [
                "Navigate to form page",
                "Fill form fields",
                "Submit form",
                "Verify submission result"
            ]
        else:
            steps = [
                "Execute test operation",
                "Verify expected behavior"
            ]

        return steps

    def _generate_test_data(self, scenario_name: str) -> Dict:
        """Generate test data for scenario"""
        test_data = {
            'valid_data': {},
            'invalid_data': {},
            'edge_case_data': {}
        }

        if 'login' in scenario_name.lower():
            test_data['valid_data'] = {
                'username': 'testuser',
                'password': 'ValidPass123!'
            }
            test_data['invalid_data'] = {
                'username': 'invaliduser',
                'password': 'wrongpassword'
            }
            test_data['edge_case_data'] = {
                'username': self.edge_case_generator.generate_edge_cases('strings', 3),
                'password': self.edge_case_generator.generate_edge_cases('strings', 3)
            }

        elif 'email' in scenario_name.lower():
            test_data['valid_data'] = {'email': 'test@example.com'}
            test_data['invalid_data'] = {'email': 'invalid-email'}
            test_data['edge_case_data'] = {
                'email': self.edge_case_generator.generate_edge_cases('emails', 5)
            }

        return test_data

    def _generate_tags(self, scenario_name: str) -> List[str]:
        """Generate tags for test organization"""
        tags = []

        if 'security' in scenario_name.lower():
            tags.extend(['security', 'owasp', 'penetration-test'])
        if 'performance' in scenario_name.lower():
            tags.extend(['performance', 'load', 'stress'])
        if 'login' in scenario_name.lower():
            tags.extend(['authentication', 'authn'])
        if 'api' in scenario_name.lower():
            tags.extend(['api', 'rest', 'integration'])

        tags.append(scenario_name.split()[0].lower())
        return tags

    @tool
    def _optimize_test_cases_tool(self, test_cases: List[Dict]) -> List[Dict]:
        """Optimize test cases for efficiency and coverage"""
        optimized_cases = []

        for test_case in test_cases:
            optimized_case = test_case.copy()

            if len(test_case['steps']) > 10:
                optimized_case['steps'] = self._optimize_steps(test_case['steps'])

            if len(test_case['test_data'].get('edge_case_data', {})) > 20:
                optimized_case['test_data']['edge_case_data'] = \
                    self._optimize_edge_cases(test_case['test_data']['edge_case_data'])

            optimized_case['execution_priority'] = self._calculate_execution_priority(test_case)

            optimized_cases.append(optimized_case)

        return optimized_cases

    def _optimize_steps(self, steps: List[str]) -> List[str]:
        """Optimize test steps for clarity and efficiency"""
        if len(steps) <= 10:
            return steps

        optimized = []
        i = 0
        while i < len(steps):
            if i + 1 < len(steps) and 'verify' in steps[i].lower() and 'verify' in steps[i+1].lower():
                optimized.append(f"Multiple verifications: {steps[i]} and {steps[i+1]}")
                i += 2
            else:
                optimized.append(steps[i])
                i += 1

        return optimized

    def _optimize_edge_cases(self, edge_cases: Dict) -> Dict:
        """Optimize edge cases to avoid test explosion"""
        optimized = {}
        for field, cases in edge_cases.items():
            optimized[field] = cases[:5]
        return optimized

    def _calculate_execution_priority(self, test_case: Dict) -> int:
        """Calculate execution priority based on multiple factors"""
        priority_map = {'HIGH': 3, 'MEDIUM': 2, 'LOW': 1}
        base_priority = priority_map.get(test_case.get('priority', 'MEDIUM'), 2)

        complexity_factors = len(test_case.get('steps', [])) * 0.1
        data_factors = sum(len(data) for data in test_case.get('test_data', {}).values()) * 0.05

        return min(10, max(1, int(base_priority + complexity_factors + data_factors)))