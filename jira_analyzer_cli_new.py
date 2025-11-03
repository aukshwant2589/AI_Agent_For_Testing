#!/usr/bin/env python3
"""Command line interface for JIRA ticket analysis and test case generation."""

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
from src.core.test_case_analyzer import TestCaseAnalyzer
from src.utils.config import Config

# Load environment variables
load_dotenv(verbose=True)

# Initialize logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

logger = logging.getLogger(__name__)

class TestCaseGeneratorCLI:
    """Command line interface for test case generation."""
    
    def __init__(self):
        """Initialize CLI with configuration."""
        self.config = Config()
        if not self.config.validate():
            sys.exit(1)
            
        self.generator = TestCaseGenerator()
        self.output_dir = self.config.output_dir
        
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
        
    def process_ticket(self, ticket_id: str, options: Dict) -> None:
        """Process a single JIRA ticket.
        
        Args:
            ticket_id: JIRA ticket ID
            options: Processing options
        """
        try:
            # Setup directories
            output_dirs = self.setup_output_directory(ticket_id)
            
            # Get ticket data
            jira_client = JIRAClient(self.config.jira_config)
            issue_data = jira_client.get_issue(ticket_id)
            
            # Generate test cases
            test_cases = self.generator.generate_test_cases(
                issue_data,
                output_dirs['base'],
                learning_enabled=options.get('learning', True)
            )
            
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
            
        # Extract ticket ID from URL
        try:
            return url.split('/')[-1]
        except:
            return None

def parse_args() -> argparse.Namespace:
    """Parse command line arguments.
    
    Returns:
        Parsed command line arguments
    """
    parser = argparse.ArgumentParser(
        description='Generate test cases from JIRA tickets using AI.'
    )
    
    # Ticket identification
    group = parser.add_mutually_exclusive_group()
    group.add_argument(
        '--ticket', '-t',
        help='JIRA ticket ID (e.g., KAN-1)'
    )
    group.add_argument(
        '--url',
        help='Full JIRA ticket URL'
    )
    group.add_argument(
        '--batch-file',
        help='File containing list of ticket IDs'
    )
    
    # Output options
    parser.add_argument(
        '--format',
        choices=['json', 'csv', 'feature', 'all'],
        default='all',
        help='Output format for test cases'
    )
    
    # Learning options
    parser.add_argument(
        '--no-learning',
        action='store_true',
        help='Disable learning from existing test cases'
    )
    
    return parser.parse_args()

def main():
    """Main entry point for the CLI."""
    try:
        args = parse_args()
        cli = TestCaseGeneratorCLI()
        cli.run(args)
    except KeyboardInterrupt:
        logger.info("Operation cancelled by user")
        sys.exit(0)
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        sys.exit(1)

if __name__ == '__main__':
    main()