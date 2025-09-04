#!/usr/bin/env python3
"""
JIRA Ticket Analyzer - Command line interface for analyzing JIRA tickets
"""

import argparse
import sys
import os
import json
from pathlib import Path

# Add src to path
sys.path.insert(0, 'src')

def main():
    parser = argparse.ArgumentParser(description='Analyze JIRA tickets and generate test cases')
    
    # Main argument - ticket URL or ID
    parser.add_argument('jira_url', nargs='?', help='JIRA ticket URL or ID (optional for batch mode)')
    
    # Output format
    parser.add_argument('--output', '-o', choices=['json', 'text'], default='text', help='Output format')
    
    # NEW: Batch processing
    parser.add_argument('--batch', help='Comma-separated list of ticket IDs for batch processing')
    parser.add_argument('--output-dir', default='batch_results', help='Output directory for batch results')
    
    # NEW: Test framework selection
    parser.add_argument('--framework', choices=['pytest', 'unittest', 'behave', 'robot'], 
                       default='pytest', help='Test framework format')
    
    # NEW: Export options
    parser.add_argument('--export', choices=['testrail', 'xray', 'jira', 'browserstack'], help='Export to test management system')
    
    # NEW: Prompt templates
    parser.add_argument('--template', choices=['default', 'security', 'performance', 'accessibility'],
                       default='default', help='Prompt template to use')
    
    # NEW: Prioritization
    parser.add_argument('--prioritize', action='store_true', help='Auto-prioritize test cases')

    args = parser.parse_args()

    # Validate arguments
    if not args.jira_url and not args.batch:
        parser.error("Either provide a JIRA URL or use --batch option")

    try:
        from tools.jira_ai_analyzer import JIRAAIAnalyzer

        analyzer = JIRAAIAnalyzer()

        # Handle batch processing
        if args.batch:
            print(f"Processing batch of tickets: {args.batch}")
            print("=" * 60)
            
            ticket_ids = [ticket_id.strip() for ticket_id in args.batch.split(',')]
            results = analyzer.process_batch_tickets(ticket_ids, args.output_dir)
            
            print(f"✅ Batch processing completed!")
            print(f"📊 Total tickets: {results['total_tickets']}")
            print(f"✅ Successful: {results['successful']}")
            print(f"❌ Failed: {results['failed']}")
            print(f"📁 Results saved to: {args.output_dir}/")
            
            return

        # Handle single ticket processing
        print(f"Analyzing JIRA ticket: {args.jira_url}")
        print("=" * 60)

        # Pass additional parameters to the analyzer
        result = analyzer.run(
            args.jira_url, 
            framework=args.framework,
            template=args.template,
            prioritize=args.prioritize,
            export=args.export
        )

        # Parse the JSON response
        data = json.loads(result)
        
        if not data.get('valid', False):
            error_msg = data.get('error', 'Unknown error occurred')
            print(f"❌ ERROR: {error_msg}")
            print(f"📋 Ticket ID: {data.get('ticket_id', 'N/A')}")
            print(f"🔍 Status: Ticket not found or inaccessible")
            sys.exit(1)

        if args.output == 'json':
            print(json.dumps(data, indent=2))
        else:
            # Pretty print for text output
            print(f"✅ Ticket ID: {data.get('ticket_id', 'N/A')}")
            print(f"📋 Summary: {data.get('ticket_summary', 'N/A')}")
            print(f"📊 Test Cases Generated: {data.get('test_cases_generated', 0)}")
            
            if args.prioritize:
                print(f"🎯 Prioritization: Enabled")
            
            if args.framework != 'pytest':
                print(f"⚙️ Framework: {args.framework}")
            
            if args.template != 'default':
                print(f"📝 Template: {args.template}")
            
            print(f"\n📝 Description Preview:")
            desc = data.get('ticket_description', '')[:200] + "..." if len(data.get('ticket_description', '')) > 200 else data.get('ticket_description', '')
            print(f"   {desc}")
            
            print(f"\n📁 Generated Files:")
            for file in data.get('generated_files', []):
                print(f"   - {file}")

            print(f"\n🧪 Test Cases:")
            for i, test_case in enumerate(data.get('test_cases', []), 1):
                print(f"\n{i}. 🎯 {test_case.get('name', 'N/A')}")
                print(f"   📝 Description: {test_case.get('description', 'N/A')}")
                print(f"   ⚡ Priority: {test_case.get('priority', 'N/A')}")
                print(f"   🏷️ Type: {test_case.get('type', 'Functional')}")
                
                if args.prioritize:
                    print(f"   📊 Risk Score: {test_case.get('risk_score', 'N/A')}")
                    print(f"   🚀 Execution Priority: {test_case.get('execution_priority', 'N/A')}")
                
                print(f"   📋 Steps:")
                for step_i, step in enumerate(test_case.get('steps', []), 1):
                    print(f"      {step_i}. {step}")
                
                print(f"   ✅ Expected: {test_case.get('expected_result', 'N/A')}")
                print(f"   📊 Test Data: {test_case.get('test_data', 'N/A')}")
                print(f"   🔧 Prerequisites: {test_case.get('prerequisites', 'None')}")

    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("Make sure the JIRAAIAnalyzer class is available in src/tools/jira_ai_analyzer.py")
        sys.exit(1)
    except json.JSONDecodeError as e:
        print(f"❌ JSON parsing error: {e}")
        if 'result' in locals():
            print(f"Raw response: {result[:200]}...")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()