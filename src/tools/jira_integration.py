import os
import json
from typing import Dict, List, Any, Optional
from collections import deque
from jira import JIRA
from tenacity import retry, stop_after_attempt, wait_exponential
from crewai_tools import BaseTool
from ..core.config_manager import config, logger
from ..utils.helpers import HelperUtils


class UltimateJiraIntegration(BaseTool):
    name: str = "Ultimate Jira Integration"
    description: str = "Enterprise-grade Jira integration with advanced analytics, bulk operations, and AI-powered insights."

    def __init__(self):
        super().__init__()
        self.jira_client = None
        self.analytics_data = deque(maxlen=10000)
        self.cache = {}
        self.bulk_operations_queue = []

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10))
    def _get_jira_client(self):
        """Get authenticated Jira client with retry logic"""
        if self.jira_client is None:
            try:
                jira_server = os.environ.get("JIRA_SERVER")
                jira_username = os.environ.get("JIRA_USERNAME")
                jira_token = os.environ.get("JIRA_API_TOKEN")

                if not all([jira_server, jira_username, jira_token]):
                    raise ValueError("JIRA credentials not found in environment variables")

                jira_options = {'server': jira_server}
                self.jira_client = JIRA(
                    options=jira_options,
                    basic_auth=(jira_username, jira_token)
                )
                logger.info("Jira client initialized successfully")
            except Exception as e:
                logger.error(f"Failed to initialize Jira client: {e}")
                raise
        return self.jira_client

    def _run(self, action: str, **kwargs) -> str:
        """Enhanced Jira operations with comprehensive feature set"""
        try:
            jira = self._get_jira_client()
            result = self._execute_jira_action(jira, action, **kwargs)

            self._log_analytics(action, 'success', kwargs, result)
            return result

        except Exception as e:
            self._log_analytics(action, 'failed', kwargs, str(e))
            logger.error(f"Jira operation failed: {action} - {e}")
            return f"Jira operation failed: {e}"

    def _execute_jira_action(self, jira, action: str, **kwargs) -> str:
        """Execute comprehensive Jira actions"""
        actions = {
            'read_ticket': self._read_ticket,
            'create_ticket': self._create_ticket,
            'update_ticket': self._update_ticket,
            'add_comment': self._add_comment,
            'attach_file': self._attach_file,
            'search_tickets': self._search_tickets,
        }

        if action not in actions:
            raise ValueError(f"Unknown Jira action: {action}")

        return actions[action](jira, **kwargs)

    def _read_ticket(self, jira, ticket_id: str, **kwargs) -> str:
        """Enhanced ticket reading with comprehensive analysis"""
        try:
            issue = jira.issue(ticket_id)

            analysis = {
                'basic_info': {
                    'key': issue.key,
                    'summary': issue.fields.summary,
                    'description': issue.fields.description or "",
                    'status': str(issue.fields.status),
                    'priority': str(issue.fields.priority),
                    'assignee': str(issue.fields.assignee) if issue.fields.assignee else None,
                    'reporter': str(issue.fields.reporter) if issue.fields.reporter else None,
                    'created': str(issue.fields.created),
                    'updated': str(issue.fields.updated)
                },
                'test_analysis': self._analyze_for_testing(issue),
            }

            return json.dumps(analysis, indent=2)

        except Exception as e:
            raise Exception(f"Failed to read ticket {ticket_id}: {e}")

    def _analyze_for_testing(self, issue) -> Dict:
        """AI-powered analysis for testing requirements"""
        description = (issue.fields.description or "").lower()
        summary = issue.fields.summary.lower()
        combined_text = f"{description} {summary}"

        analysis = {
            'form_types_detected': [],
            'testing_priority': self._calculate_testing_priority(issue),
            'estimated_complexity': self._estimate_complexity(combined_text),
            'recommended_test_types': [],
            'risk_factors': []
        }

        form_patterns = {
            'login_form': ['login', 'sign in', 'authenticate', 'credentials'],
            'registration_form': ['register', 'sign up', 'create account', 'new user'],
            'contact_form': ['contact', 'feedback', 'inquiry', 'message'],
            'search_form': ['search', 'find', 'filter', 'query'],
            'payment_form': ['payment', 'billing', 'checkout', 'purchase'],
            'profile_form': ['profile', 'settings', 'account', 'preferences']
        }

        for form_type, keywords in form_patterns.items():
            if any(keyword in combined_text for keyword in keywords):
                analysis['form_types_detected'].append(form_type)

        if 'api' in combined_text or 'endpoint' in combined_text:
            analysis['recommended_test_types'].append('api_testing')
        if any(word in combined_text for word in ['form', 'input', 'button']):
            analysis['recommended_test_types'].append('ui_testing')
        if 'performance' in combined_text or 'load' in combined_text:
            analysis['recommended_test_types'].append('performance_testing')

        if 'security' in combined_text or 'authentication' in combined_text:
            analysis['risk_factors'].append('security_sensitive')
        if 'payment' in combined_text or 'financial' in combined_text:
            analysis['risk_factors'].append('financial_data')
        if 'integration' in combined_text or 'third-party' in combined_text:
            analysis['risk_factors'].append('external_dependencies')

        return analysis

    def _calculate_testing_priority(self, issue) -> int:
        """Calculate testing priority based on issue attributes"""
        priority_score = 0

        priority_map = {'Lowest': 1, 'Low': 2, 'Medium': 3, 'High': 4, 'Highest': 5}
        priority_score += priority_map.get(str(issue.fields.priority), 3)

        issue_type = str(issue.fields.issuetype).lower()
        if 'bug' in issue_type:
            priority_score += 2
        elif 'story' in issue_type:
            priority_score += 1

        if hasattr(issue.fields, 'labels') and issue.fields.labels:
            labels = [label.lower() for label in issue.fields.labels]
            if 'critical' in labels:
                priority_score += 3
            if 'security' in labels:
                priority_score += 2

        return min(priority_score, 10)

    def _estimate_complexity(self, text: str) -> int:
        """Estimate testing complexity based on text analysis"""
        complexity_keywords = {
            'simple': ['login', 'logout', 'simple', 'basic'],
            'medium': ['form', 'validation', 'integration', 'api'],
            'complex': ['workflow', 'multi-step', 'complex', 'advanced'],
            'very_complex': ['payment', 'security', 'multi-user', 'real-time']
        }

        scores = {'simple': 1, 'medium': 3, 'complex': 5, 'very_complex': 8}

        for complexity, keywords in complexity_keywords.items():
            if any(keyword in text for keyword in keywords):
                return scores[complexity]

        return 2

    def _create_ticket(self, jira, project_key: str, summary: str, description: str, **kwargs) -> str:
        """Create enhanced ticket with comprehensive metadata"""
        issue_dict = {
            'project': {'key': project_key},
            'summary': summary,
            'description': description,
            'issuetype': {'name': kwargs.get('issue_type', 'Bug')},
        }

        if kwargs.get('priority'):
            issue_dict['priority'] = {'name': kwargs['priority']}

        if kwargs.get('assignee'):
            issue_dict['assignee'] = {'name': kwargs['assignee']}

        if kwargs.get('labels'):
            issue_dict['labels'] = kwargs['labels']

        if kwargs.get('components'):
            issue_dict['components'] = [{'name': comp} for comp in kwargs['components']]

        new_issue = jira.create_issue(fields=issue_dict)

        return json.dumps({
            'created_issue': new_issue.key,
            'url': f"{os.environ.get('JIRA_SERVER')}/browse/{new_issue.key}",
            'creation_time': datetime.now().isoformat()
        })

    def _add_comment(self, jira, issue_id: str, comment: str, **kwargs) -> str:
        """Add enhanced comment with formatting"""
        formatted_comment = f"{comment}\n\n---\n*Automated by Ultimate Test Coordinator* | {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"

        jira.add_comment(issue_id, formatted_comment)
        return f"Comment added to {issue_id}"

    def _attach_file(self, jira, issue_id: str, file_path: str, **kwargs) -> str:
        """Attach file with metadata"""
        if not os.path.exists(file_path):
            return f"File not found: {file_path}"

        jira.add_attachment(issue=issue_id, attachment=file_path)
        return f"Attached {file_path} to {issue_id}"

    def _search_tickets(self, jira, jql: str, **kwargs) -> str:
        """Search for tickets using JQL"""
        try:
            max_results = kwargs.get('max_results', 50)
            issues = jira.search_issues(jql, maxResults=max_results)

            results = []
            for issue in issues:
                results.append({
                    'key': issue.key,
                    'summary': issue.fields.summary,
                    'status': str(issue.fields.status),
                    'priority': str(issue.fields.priority),
                    'url': f"{os.environ.get('JIRA_SERVER')}/browse/{issue.key}"
                })

            return json.dumps({
                'total_results': len(issues),
                'issues': results,
                'jql': jql
            }, indent=2)

        except Exception as e:
            raise Exception(f"JQL search failed: {e}")

    def _log_analytics(self, action: str, status: str, params: Dict, result: Any = None):
        """Enhanced analytics logging"""
        analytics_entry = {
            'timestamp': datetime.now().isoformat(),
            'action': action,
            'status': status,
            'params': {k: str(v) for k, v in params.items()},
            'result_size': len(str(result)) if result else 0
        }

        self.analytics_data.append(analytics_entry)