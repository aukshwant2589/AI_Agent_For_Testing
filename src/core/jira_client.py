"""JIRA API integration module"""
import os
from typing import Dict, Optional
from jira import JIRA
import logging

logger = logging.getLogger(__name__)

class JIRAClient:
    """Handles JIRA API interactions"""
    
    def __init__(self):
        self.jira = None
        self.validator = None
        self._connect()
        
    def _connect(self):
        """Establish connection to JIRA with enhanced validation"""
        try:
            logger.info("Starting JIRA connection setup...")
            
            # Get credentials from environment variables
            jira_email = os.getenv('JIRA_EMAIL')
            jira_api_token = os.getenv('JIRA_API_TOKEN')
            jira_server = os.getenv('JIRA_SERVER')
            
            logger.info("Loading JIRA credentials:")
            logger.info(f"JIRA_EMAIL: {'*' * len(jira_email) if jira_email else 'Not found'}")
            logger.info(f"JIRA_API_TOKEN: {'*' * 10 if jira_api_token else 'Not found'}")
            logger.info(f"JIRA_SERVER: {jira_server if jira_server else 'Not found'}")
            
            if not all([jira_email, jira_api_token, jira_server]):
                missing = []
                if not jira_email: missing.append("JIRA_EMAIL")
                if not jira_api_token: missing.append("JIRA_API_TOKEN")
                if not jira_server: missing.append("JIRA_SERVER")
                raise ValueError(f"Missing JIRA credentials: {', '.join(missing)}")
            
            logger.info("Configuring JIRA client...")
            
            # Create JIRA client with advanced options
            jira_options = {
                'server': jira_server,
                'verify': True,
                'timeout': 30
            }
            
            logger.info("Attempting JIRA connection...")
            
            # Create JIRA client
            self.jira = JIRA(
                options=jira_options,
                basic_auth=(jira_email, jira_api_token)
            )
            
            logger.info("JIRA connection successful, initializing validator...")
            
            # Initialize project validator
            from .project_validator import ProjectValidator
            self.validator = ProjectValidator(self.jira)
            
            # Log connection status
            logger.info("Loading accessible projects...")
            accessible_projects = self.validator.get_accessible_projects()
            logger.info(f"Successfully initialized with access to {len(accessible_projects)} projects")
            
        except Exception as e:
            logger.error(f"Failed to connect to JIRA: {str(e)}", exc_info=True)
            raise
            
    def get_issue_details(self, issue_key: str) -> Optional[Dict]:
        """
        Get detailed information about a JIRA issue
        
        Args:
            issue_key: The JIRA issue key (e.g., 'KAN-1')
            
        Returns:
            Dict containing issue details or None if not found/accessible
        """
        try:
            # Fetch issue
            issue = self.jira.issue(issue_key)
            
            # Extract custom fields and components
            custom_fields = {}
            components = []
            
            for field_name, field_value in issue.raw['fields'].items():
                if field_name.startswith('customfield_'):
                    if field_value:
                        custom_fields[field_name] = field_value
                        
            if hasattr(issue.fields, 'components'):
                components = [c.name for c in issue.fields.components]
            
            # Build comprehensive issue data
            issue_data = {
                'key': issue.key,
                'summary': issue.fields.summary,
                'description': issue.fields.description or '',
                'issuetype': {
                    'name': issue.fields.issuetype.name,
                    'description': issue.fields.issuetype.description
                },
                'priority': {
                    'name': issue.fields.priority.name if issue.fields.priority else 'Medium',
                    'id': issue.fields.priority.id if issue.fields.priority else '3'
                },
                'status': {
                    'name': issue.fields.status.name,
                    'description': issue.fields.status.description
                },
                'components': components,
                'labels': issue.fields.labels,
                'custom_fields': custom_fields,
                'created': issue.fields.created,
                'updated': issue.fields.updated
            }
            
            # Add acceptance criteria if available
            if hasattr(issue.fields, 'customfield_10029'):  # Adjust field ID as needed
                issue_data['acceptance_criteria'] = issue.fields.customfield_10029
            
            # Add epic link if available
            if hasattr(issue.fields, 'customfield_10014'):  # Adjust field ID as needed
                issue_data['epic_link'] = issue.fields.customfield_10014
            
            # Add sprint information if available
            if hasattr(issue.fields, 'customfield_10020'):  # Adjust field ID as needed
                sprint_data = issue.fields.customfield_10020
                if sprint_data:
                    issue_data['sprint'] = sprint_data[0].name if isinstance(sprint_data, list) else sprint_data
            
            return issue_data
            
        except Exception as e:
            logger.error(f"Error fetching issue {issue_key}: {str(e)}", exc_info=True)
            return None
            
    def extract_test_requirements(self, issue_data: Dict) -> Dict:
        """
        Extract test-relevant information from issue data
        
        Args:
            issue_data: Issue details from get_issue_details()
            
        Returns:
            Dict containing structured test requirements
        """
        requirements = {
            'key': issue_data['key'],
            'summary': issue_data['summary'],
            'description': issue_data['description'],
            'type': issue_data['issuetype']['name'],
            'priority': issue_data['priority']['name'],
            'components': issue_data.get('components', []),
            'labels': issue_data.get('labels', []),
            'acceptance_criteria': issue_data.get('acceptance_criteria', ''),
            'test_focus_areas': [],
            'security_requirements': [],
            'validation_points': []
        }
        
        # Analyze description and acceptance criteria for test requirements
        text_to_analyze = f"{requirements['description']} {requirements.get('acceptance_criteria', '')}"
        text_to_analyze = text_to_analyze.lower()
        
        # Identify test focus areas
        if 'api' in text_to_analyze or 'endpoint' in text_to_analyze:
            requirements['test_focus_areas'].append('API Testing')
        if 'ui' in text_to_analyze or 'interface' in text_to_analyze:
            requirements['test_focus_areas'].append('UI Testing')
        if 'database' in text_to_analyze or 'data' in text_to_analyze:
            requirements['test_focus_areas'].append('Data Validation')
            
        # Identify security requirements
        security_keywords = ['security', 'auth', 'permission', 'access', 'role', 'login']
        for keyword in security_keywords:
            if keyword in text_to_analyze:
                requirements['security_requirements'].append(f"Verify {keyword} controls")
                
        # Extract validation points with categorization
        validation_indicators = {
            'functional': ['should', 'must', 'needs to', 'will', 'verify', 'check', 'ensure'],
            'performance': ['response time', 'load time', 'performance', 'fast', 'slow', 'second'],
            'usability': ['user friendly', 'intuitive', 'accessible', 'easy to', 'clear'],
            'security': ['secure', 'authenticated', 'authorized', 'permission', 'role'],
            'data': ['valid', 'invalid', 'data', 'input', 'output', 'format'],
            'error': ['error', 'exception', 'fail', 'invalid', 'incorrect'],
            'integration': ['api', 'endpoint', 'service', 'integration', 'connect']
        }
        
        # Initialize categorized validation points
        categorized_points = {category: [] for category in validation_indicators.keys()}
        
        # Process description and acceptance criteria
        lines = text_to_analyze.split('\n')
        for line in lines:
            line = line.strip().lower()
            if len(line) < 10:  # Skip very short lines
                continue
                
            # Categorize the line based on indicators
            for category, indicators in validation_indicators.items():
                if any(indicator in line for indicator in indicators):
                    # Clean up the line for better readability
                    clean_line = line.capitalize()
                    if not clean_line.endswith('.'):
                        clean_line += '.'
                        
                    if clean_line not in categorized_points[category]:
                        categorized_points[category].append(clean_line)
                        
        # Add categorized points to requirements
        requirements['validation_points'] = {
            category: points for category, points in categorized_points.items()
            if points  # Only include categories with points
        }
        
        # Add test complexity estimation
        requirements['test_complexity'] = self._estimate_test_complexity(
            issue_data, 
            categorized_points
        )
        
        return requirements
        
    def _estimate_test_complexity(self, issue_data: Dict, validation_points: Dict) -> str:
        """
        Estimate test complexity based on various factors
        
        Returns: 'Low', 'Medium', or 'High'
        """
        complexity_score = 0
        
        # Factor 1: Number of validation points
        total_points = sum(len(points) for points in validation_points.values())
        if total_points <= 3:
            complexity_score += 1
        elif total_points <= 7:
            complexity_score += 2
        else:
            complexity_score += 3
            
        # Factor 2: Number of components involved
        components = issue_data.get('components', [])
        if len(components) <= 1:
            complexity_score += 1
        elif len(components) <= 3:
            complexity_score += 2
        else:
            complexity_score += 3
            
        # Factor 3: Integration points
        if validation_points.get('integration'):
            complexity_score += 2
            
        # Factor 4: Security requirements
        if validation_points.get('security'):
            complexity_score += 2
            
        # Factor 5: Data complexity
        if validation_points.get('data'):
            complexity_score += len(validation_points['data']) // 2
            
        # Map score to complexity level
        if complexity_score <= 5:
            return 'Low'
        elif complexity_score <= 9:
            return 'Medium'
        else:
            return 'High'