#!/usr/bin/env python3
"""
Ultimate AI Test Automation Coordinator - Command Line Interface
"""

import argparse
import sys
import os
import logging

def check_dependencies():
    """Check if required dependencies are installed"""
    missing_deps = []

    try:
        import yaml
    except ImportError:
        missing_deps.append("pyyaml")

    try:
        import crewai
    except ImportError:
        missing_deps.append("crewai")

    try:
        import jira
    except ImportError:
        missing_deps.append("jira")

    if missing_deps:
        print("Error: The following dependencies are missing:")
        for dep in missing_deps:
            print(f"  - {dep}")
        print("\nPlease install them using: pip install " + " ".join(missing_deps))
        return False
    return True

def main():
    """Main command line interface"""
    # Check dependencies first
    if not check_dependencies():
        sys.exit(1)

    # Now import the rest of the modules
    try:
        # Add the src directory to the Python path
        sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

        from src.main import UltimateTestCoordinator
        from src.core.config_manager import UltimateConfigManager
        from src.utils.helpers import HelperUtils

        parser = argparse.ArgumentParser(
            description='Ultimate AI Test Automation Coordinator',
            formatter_class=argparse.RawDescriptionHelpFormatter,
            epilog="""
Examples:
  # Run complete test cycle from requirements
  python run.py --requirements "Test login functionality with security validation"

  # Run targeted login testing
  python run.py --target https://example.com/login --test-type login

  # Run targeted form testing
  python run.py --target https://example.com/contact --test-type form

  # Run API testing
  python run.py --target https://api.example.com/v1/users --test-type api
            """
        )

        parser.add_argument(
            '--requirements', '-r',
            type=str,
            help='Test requirements to analyze'
        )

        parser.add_argument(
            '--target', '-t',
            type=str,
            help='Target URL or API endpoint to test'
        )

        parser.add_argument(
            '--test-type',
            choices=['login', 'form', 'api'],
            help='Type of test to run'
        )

        parser.add_argument(
            '--report-format',
            choices=['text', 'json'],
            default='text',
            help='Report format'
        )

        # Parse arguments
        args = parser.parse_args()

        # Validate that we have either requirements or target
        if not args.requirements and not args.target:
            parser.print_help()
            sys.exit(1)

        if args.target and not args.test_type:
            print("Error: --test-type is required when using --target")
            sys.exit(1)

        if args.test_type and not args.target:
            print("Error: --target is required when using --test-type")
            sys.exit(1)

        # Setup logging
        logger = HelperUtils.setup_logging()

        # Load configuration
        config = UltimateConfigManager()

        # Execute based on arguments
        coordinator = UltimateTestCoordinator()

        if args.requirements:
            logger.info(f"Starting requirements-based testing: {args.requirements}")
            results = coordinator.run_full_test_cycle(args.requirements)

            # Generate report
            if args.report_format == "json":
                report = coordinator.generate_test_report(results, "json")
                print(report)
            else:
                report = coordinator.generate_test_report(results, "html")
                report_file = f"reports/test_report_{HelperUtils.generate_unique_id()}.html"
                with open(report_file, "w", encoding="utf-8") as f:
                    f.write(report)
                print(f"HTML report generated: {report_file}")

                # Show summary
                summary = results.get('execution_results', {})
                print(f"\nTest Execution Summary:")
                print(f"  Total Tests: {summary.get('total_tests', 0)}")
                print(f"  Passed: {summary.get('passed', 0)}")
                print(f"  Failed: {summary.get('failed', 0)}")
                print(f"  Success Rate: {summary.get('success_rate', 0):.1f}%")

        else:
            logger.info(f"Starting targeted {args.test_type} testing for {args.target}")
            results = coordinator.run_targeted_test(args.test_type, args.target)

            if args.report_format == "json":
                import json
                print(json.dumps(results, indent=2))
            else:
                print(f"\nTargeted Test Results ({args.test_type}):")
                print(f"  Target: {args.target}")
                print(f"  Status: {results.get('status', 'unknown')}")

                if 'tests_performed' in results:
                    print(f"  Tests Performed: {len(results.get('tests_performed', []))}")

                if 'vulnerabilities_found' in results:
                    print(f"  Vulnerabilities Found: {len(results.get('vulnerabilities_found', []))}")

                if 'error' in results:
                    print(f"  Error: {results.get('error')}")

    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()