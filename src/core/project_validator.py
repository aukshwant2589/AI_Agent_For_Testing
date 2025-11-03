"""Project validation module for JIRA access control"""
import re
import logging
from typing import Optional, List
from jira import JIRA

logger = logging.getLogger(__name__)

class ProjectValidator:
    """Validates JIRA project access and ticket format"""
    
    def __init__(self, jira_client: JIRA):
        """Initialize validator with JIRA client.
        
        Args:
            jira_client: Authenticated JIRA client instance
        """
        self.jira = jira_client
        self._accessible_projects = None
    
    def validate_ticket_id(self, ticket_id: str) -> bool:
        """Validate ticket ID format and project access.
        
        Args:
            ticket_id: JIRA ticket ID (e.g., 'PROJECT-123')
            
        Returns:
            bool: True if ticket format is valid and project is accessible
        """
        if not ticket_id:
            return False
            
        # Check ticket ID format
        if not re.match(r'^[A-Z0-9]+-\d+$', ticket_id.upper()):
            logger.warning(f"Invalid ticket ID format: {ticket_id}")
            return False
            
        # Extract project key
        project_key = ticket_id.split('-')[0].upper()
        
        # Check if project is accessible
        return self.is_project_accessible(project_key)
    
    def is_project_accessible(self, project_key: str) -> bool:
        """Check if user has access to the specified project.
        
        Args:
            project_key: JIRA project key
            
        Returns:
            bool: True if project exists and is accessible
        """
        try:
            # Load accessible projects if not already loaded
            if self._accessible_projects is None:
                self._load_accessible_projects()
            
            return project_key.upper() in self._accessible_projects
            
        except Exception as e:
            logger.error(f"Error checking project access: {str(e)}")
            return False
    
    def _load_accessible_projects(self):
        """Load list of accessible project keys."""
        try:
            projects = self.jira.projects()
            self._accessible_projects = {p.key.upper() for p in projects}
            logger.info(f"Loaded {len(self._accessible_projects)} accessible projects")
        except Exception as e:
            logger.error(f"Error loading projects: {str(e)}")
            self._accessible_projects = set()
    
    def get_accessible_projects(self) -> List[str]:
        """Get list of accessible project keys.
        
        Returns:
            List of project keys user has access to
        """
        if self._accessible_projects is None:
            self._load_accessible_projects()
        return sorted(list(self._accessible_projects))

    def is_ticket_accessible(self, ticket_id: str) -> bool:
        """Check if a specific ticket is accessible.
        
        Args:
            ticket_id: JIRA ticket ID
            
        Returns:
            bool: True if ticket exists and is accessible
        """
        try:
            # First validate format and project access
            if not self.validate_ticket_id(ticket_id):
                return False
                
            # Try to fetch minimal ticket info to verify access
            self.jira.issue(ticket_id, fields='key')
            return True
            
        except Exception as e:
            logger.error(f"Error checking ticket access: {str(e)}")
            return False