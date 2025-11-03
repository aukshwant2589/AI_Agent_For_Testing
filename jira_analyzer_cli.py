#!/usr/bin/env python3
"""
JIRA Ticket Analyzer - Command line interface for analyzing JIRA tickets
"""

import argparse
import sys
import os
import json
import logging
from pathlib import Path
from typing import Dict, List, Optional
from dotenv import load_dotenv

# Add src to path
sys.path.insert(0, str(Path(__file__).parent))

from src.core import TestCaseGenerator, JIRAClient
from src.core.playwright_generator import PlaywrightTestGenerator

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv(verbose=True)

# Display environment variables (without sensitive values)
logger.info("Loading JIRA credentials:")
logger.info(f"JIRA_EMAIL: {'*' * 20}")
logger.info(f"JIRA_API_TOKEN: {'*' * 10}")
logger.info(f"JIRA_SERVER: {os.getenv('JIRA_SERVER', 'https://auxworx.atlassian.net')}")

class JiraAnalyzer:
    def __init__(self, output_dir: Path):
        """Initialize JiraAnalyzer.
        
        Args:
            output_dir: Path to output directory
        """
        self.output_dir = Path(output_dir)
        self.generator = TestCaseGenerator()
        self.jira_client = JIRAClient()
        
    def get_jira_issue(self, ticket_id: str) -> Dict:
        """Get JIRA issue data.
        
        Args:
            ticket_id: JIRA ticket ID
            
        Returns:
            Dictionary containing issue data
        """
        try:
            issue_data = self.jira_client.get_issue_details(ticket_id)
            
            if not issue_data:
                raise ValueError(f"Could not fetch details for ticket {ticket_id}")
                
            return {
                'key': ticket_id,
                'summary': issue_data.get('summary', ''),
                'description': issue_data.get('description', ''),
                'acceptance_criteria': issue_data.get('acceptance_criteria', '')
            }
            
        except Exception as e:
            logger.error(f"Error fetching JIRA issue: {str(e)}", exc_info=True)
            raise
            
    def setup_output_directory(self, ticket_id: str) -> Dict[str, str]:
        """Setup output directory structure for a ticket.
        
        Args:
            ticket_id: JIRA ticket ID
            
        Returns:
            Dictionary of created directory paths
        """
        dirs = {
            'base': self.output_dir / ticket_id,
            'tests': self.output_dir / ticket_id / 'tests',
            'playwright': self.output_dir / ticket_id / 'playwright',
            'reports': self.output_dir / ticket_id / 'reports'
        }
        
        for dir_path in dirs.values():
            dir_path.mkdir(parents=True, exist_ok=True)
            
        return {k: str(v) for k, v in dirs.items()}
        
    def process_ticket(self, ticket_id: str, options: Dict) -> Optional[Dict]:
        """Process a single JIRA ticket.
        
        Args:
            ticket_id: JIRA ticket ID
            options: Processing options
            
        Returns:
            Generated test cases if successful
        """
        try:
            # Setup directories
            output_dirs = self.setup_output_directory(ticket_id)
            
            # Get issue data
            issue_data = self.get_jira_issue(ticket_id)
            
            if not issue_data:
                raise ValueError(f"Could not fetch details for ticket {ticket_id}")
                
            # Generate test cases
            test_cases = self.generator.generate_test_cases(
                issue_data=issue_data,
                output_dir=output_dirs['base'],
                learning_enabled=options.get('learning', True)
            )
            
            if test_cases:
                # Generate Playwright tests if test cases were created
                playwright_gen = PlaywrightTestGenerator(output_dirs['playwright'])
                playwright_gen.generate_automation_scripts(test_cases)
                logger.info("Generated Playwright tests successfully")
                
            logger.info(f"Test scripts generated successfully for {ticket_id}")
            return test_cases
            
        except Exception as e:
            logger.error(f"Error processing ticket {ticket_id}: {str(e)}")
            raise
            
    def process_batch(self, batch_file: str) -> None:
        """Process multiple tickets from a file.
        
        Args:
            batch_file: Path to file containing ticket IDs
        """
        try:
            with open(batch_file) as f:
                tickets = [line.strip() for line in f if line.strip()]
                
            for ticket in tickets:
                logger.info(f"Processing ticket: {ticket}")
                self.process_ticket(ticket, {'learning': True})
                
        except Exception as e:
            logger.error(f"Error processing batch file: {str(e)}")
            sys.exit(1)
            
    def validate_and_process_ticket(self, ticket_id: str) -> bool:
        """Validate and process a ticket if accessible.
        
        Args:
            ticket_id: JIRA ticket ID
            
        Returns:
            bool: True if ticket was processed successfully
        """
        try:
            # Check if ticket is valid and accessible
            if not self.jira_client.validator.is_ticket_accessible(ticket_id):
                logger.error(f"Ticket {ticket_id} is not accessible or doesn't exist")
                return False
                
            # Process the ticket
            logger.info(f"Processing ticket {ticket_id}...")
            self.process_ticket(ticket_id, {})
            return True
            
        except Exception as e:
            logger.error(f"Error processing ticket {ticket_id}: {str(e)}")
            return False
    
    def run(self, args: argparse.Namespace) -> None:
        """Run the CLI with provided arguments.
        
        Args:
            args: Parsed command line arguments
        """
        try:
            if args.batch_file:
                self.process_batch(args.batch_file)
            else:
                ticket_id = args.ticket or self._extract_ticket_id(args.url)
                if not ticket_id:
                    logger.error("No ticket ID provided")
                    sys.exit(1)
                    
                options = {
                    'learning': not args.no_learning,
                    'format': args.format
                }
                
                self.process_ticket(ticket_id, options)
                
        except Exception as e:
            logger.error(f"Error: {str(e)}")
            sys.exit(1)
            
    def _extract_ticket_id(self, url: Optional[str]) -> Optional[str]:
        """Extract ticket ID from JIRA URL.
        
        Args:
            url: JIRA ticket URL
            
        Returns:
            Extracted ticket ID or None
        """
        if not url:
            return None
            
        try:
            return url.split('/')[-1]
        except:
            return None

def main():
    """Main entry point for the CLI."""
    # Parse command line arguments
    parser = argparse.ArgumentParser(description="Generate test cases from JIRA tickets")
    parser.add_argument("--ticket", help="JIRA ticket ID")
    parser.add_argument("--url", help="JIRA ticket URL")
    parser.add_argument("--output-dir", default="generated_tests", help="Output directory")
    parser.add_argument("--format", default="all", choices=["all", "feature", "pytest"], help="Output format")
    parser.add_argument("--batch-file", help="Path to file containing list of ticket IDs")
    parser.add_argument("--no-learning", action="store_true", help="Disable learning mode")
    
    args = parser.parse_args()
    
    # Create analyzer instance
    analyzer = JiraAnalyzer(Path(args.output_dir))
    
    try:
        # Run the analyzer
        analyzer.run(args)
    except KeyboardInterrupt:
        logger.info("Process interrupted by user")
        sys.exit(0)

if __name__ == "__main__":
    main()
