from crewai import Agent
from langchain.tools import tool
from langchain.llms import OpenAI
from typing import List, Dict
from concurrent.futures import ThreadPoolExecutor, as_completed
from ..core.config_manager import config, logger
from ..core.performance_monitor import PerformanceMonitor
from ..core.circuit_breaker import CircuitBreakerManager


class ExecutionOrchestratorAgent:
    """AI Agent for orchestrating test execution with optimization"""

    def __init__(self):
        self.llm = OpenAI(temperature=0.1)
        self.performance_monitor = PerformanceMonitor()
        self.circuit_breaker = CircuitBreakerManager()
        self.executor = ThreadPoolExecutor(max_workers=config.get('execution.max_parallel_tests', 4))
        self.agent = self._create_agent()

    def _create_agent(self) -> Agent:
        """Create the execution orchestrator agent"""
        return Agent(
            role='Test Execution Orchestrator',
            goal='Optimize and coordinate test execution for maximum efficiency and reliability',
            backstory="""You are an expert in test execution optimization with deep knowledge of
            parallel processing, resource management, and fault tolerance. You ensure tests run
            efficiently while maintaining system stability and providing comprehensive results.""",
            verbose=True,
            allow_delegation=False,
            tools=[self._execute_tests_tool, self._optimize_execution_tool],
            llm=self.llm
        )

    @tool
    def _execute_tests_tool(self, test_cases: List[Dict]) -> Dict:
        """Execute test cases with optimization and monitoring"""
        results = {
            'total_tests': len(test_cases),
            'passed': 0,
            'failed': 0,
            'skipped': 0,
            'execution_time': 0,
            'detailed_results': []
        }

        self.performance_monitor.start_monitoring()

        try:
            future_to_test = {
                self.executor.submit(self._execute_single_test, test_case): test_case
                for test_case in test_cases
            }

            for future in as_completed(future_to_test):
                test_case = future_to_test[future]
                try:
                    result = future.result()
                    results['detailed_results'].append(result)

                    if result['status'] == 'passed':
                        results['passed'] += 1
                    elif result['status'] == 'failed':
                        results['failed'] += 1
                    else:
                        results['skipped'] += 1

                except Exception as e:
                    logger.error(f"Test execution failed for {test_case.get('name')}: {e}")
                    results['failed'] += 1
                    results['detailed_results'].append({
                        'name': test_case.get('name'),
                        'status': 'error',
                        'error': str(e)
                    })

        finally:
            self.performance_monitor.stop_monitoring()
            results['performance_report'] = self.performance_monitor.get_performance_report()
            results['execution_time'] = sum(r.get('execution_time', 0) for r in results['detailed_results'])

        return results

    def _execute_single_test(self, test_case: Dict) -> Dict:
        """Execute a single test case with comprehensive monitoring"""
        start_time = time.time()
        result = {
            'name': test_case['name'],
            'start_time': datetime.now().isoformat(),
            'status': 'pending',
            'execution_time': 0,
            'performance_metrics': {}
        }

        try:
            if not self._check_preconditions(test_case.get('dependencies', [])):
                result['status'] = 'skipped'
                result['reason'] = 'Preconditions not met'
                return result

            logger.info(f"Executing test: {test_case['name']}")

            test_result = self.circuit_breaker.protected_call(
                f"test_{test_case['name']}",
                self._run_test_implementation,
                test_case
            )

            result.update(test_result)
            result['status'] = 'passed'

        except Exception as e:
            result['status'] = 'failed'
            result['error'] = str(e)
            result['stack_trace'] = self._get_stack_trace()

        finally:
            end_time = time.time()
            result['execution_time'] = end_time - start_time
            result['end_time'] = datetime.now().isoformat()
            result['performance_metrics'] = self._collect_performance_metrics()

        return result

    def _run_test_implementation(self, test_case: Dict) -> Dict:
        """Actual test implementation - to be overridden by specific test frameworks"""
        time.sleep(random.uniform(0.1, 2.0))

        if random.random() < 0.1:
            raise Exception("Simulated test failure")

        return {
            'assertions_passed': random.randint(1, 10),
            'screenshots_taken': random.randint(0, 3),
            'network_requests': random.randint(1, 5)
        }

    def _check_preconditions(self, dependencies: List[str]) -> bool:
        """Check if test preconditions are met"""
        return all(self._check_dependency(dep) for dep in dependencies)

    def _check_dependency(self, dependency: str) -> bool:
        """Check a single dependency"""
        if 'database' in dependency.lower():
            return self._check_database_connection()
        elif 'api' in dependency.lower():
            return self._check_api_availability()
        elif 'user' in dependency.lower():
            return self._check_user_exists()
        else:
            return True

    def _collect_performance_metrics(self) -> Dict:
        """Collect performance metrics for the test"""
        return {
            'memory_peak': psutil.Process().memory_info().rss / 1024 / 1024,
            'cpu_peak': psutil.Process().cpu_percent(),
            'io_operations': 0
        }

    def _get_stack_trace(self) -> str:
        """Get current stack trace for error reporting"""
        import traceback
        return traceback.format_exc()

    @tool
    def _optimize_execution_tool(self, execution_results: Dict) -> Dict:
        """Analyze execution results and provide optimization recommendations"""
        recommendations = {
            'parallelization_opportunities': [],
            'resource_optimizations': [],
            'test_prioritization': [],
            'infrastructure_improvements': []
        }

        execution_times = [r.get('execution_time', 0) for r in execution_results.get('detailed_results', [])]
        if execution_times:
            avg_time = sum(execution_times) / len(execution_times)
            recommendations['parallelization_opportunities'].append(
                f"Average test time: {avg_time:.2f}s - Consider parallel execution for tests > {avg_time * 2:.2f}s"
            )

        memory_usage = [r.get('performance_metrics', {}).get('memory_peak', 0)
                       for r in execution_results.get('detailed_results', [])]
        if memory_usage:
            max_memory = max(memory_usage)
            if max_memory > 500:
                recommendations['resource_optimizations'].append(
                    f"High memory usage detected (max: {max_memory:.2f}MB) - Optimize memory-intensive tests"
                )

        failed_tests = [r for r in execution_results.get('detailed_results', [])
                       if r.get('status') in ['failed', 'error']]
        if failed_tests:
            recommendations['test_prioritization'].append(
                f"Focus on fixing {len(failed_tests)} failing tests before adding new features"
            )

        return recommendations