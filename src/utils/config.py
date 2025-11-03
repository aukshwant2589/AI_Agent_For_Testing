"""Configuration management for the test case generation system."""

import os
from typing import Dict, Any
from pathlib import Path

class Config:
    """Configuration manager for the application."""
    
    DEFAULTS = {
        'JIRA_SERVER': 'https://auxworx.atlassian.net',
        'OUTPUT_DIR': 'generated_tests',
        'LOG_LEVEL': 'INFO',
        'FRAMEWORK': 'playwright',
        'LEARNING_ENABLED': True
    }
    
    def __init__(self):
        """Initialize configuration with environment variables and defaults."""
        self.config = self.DEFAULTS.copy()
        self._load_env_vars()
    
    def _load_env_vars(self) -> None:
        """Load configuration from environment variables."""
        env_vars = {
            'JIRA_EMAIL': os.getenv('JIRA_EMAIL'),
            'JIRA_API_TOKEN': os.getenv('JIRA_API_TOKEN'),
            'JIRA_SERVER': os.getenv('JIRA_SERVER'),
            'GOOGLE_API_KEY': os.getenv('GOOGLE_API_KEY')
        }
        
        # Update config with environment variables
        self.config.update({k: v for k, v in env_vars.items() if v is not None})
        
    def get(self, key: str, default: Any = None) -> Any:
        """Get configuration value by key."""
        return self.config.get(key, default)
    
    def validate(self) -> bool:
        """Validate required configuration values."""
        required_vars = ['JIRA_EMAIL', 'JIRA_API_TOKEN', 'GOOGLE_API_KEY']
        missing = [var for var in required_vars if not self.config.get(var)]
        
        if missing:
            print(f"Error: Missing required environment variables: {', '.join(missing)}")
            return False
            
        return True
    
    @property
    def output_dir(self) -> Path:
        """Get the output directory path."""
        return Path(self.config.get('OUTPUT_DIR', 'generated_tests'))
    
    @property
    def jira_config(self) -> Dict[str, str]:
        """Get JIRA configuration."""
        return {
            'email': self.config['JIRA_EMAIL'],
            'api_token': self.config['JIRA_API_TOKEN'],
            'server': self.config['JIRA_SERVER']
        }
    
    @property
    def ai_config(self) -> Dict[str, str]:
        """Get AI configuration."""
        return {
            'api_key': self.config['GOOGLE_API_KEY'],
            'model': 'models/gemini-2.5-pro'
        }