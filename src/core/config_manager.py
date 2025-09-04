import os
import threading
import yaml
import logging
import sys
from typing import Any, Dict, Optional
from dataclasses import dataclass
from enum import Enum


class TestStatus(Enum):
    PENDING = "pending"
    RUNNING = "running"
    PASSED = "passed"
    FAILED = "failed"
    SKIPPED = "skipped"
    ERROR = "error"


class Priority(Enum):
    LOW = 1
    MEDIUM = 2
    HIGH = 3
    CRITICAL = 4


class ExecutionMode(Enum):
    SEQUENTIAL = "sequential"
    PARALLEL = "parallel"
    DISTRIBUTED = "distributed"
    ADAPTIVE = "adaptive"


@dataclass
class TestMetrics:
    execution_time: float
    memory_usage: float
    cpu_usage: float
    network_calls: int
    screenshots_taken: int
    retries_count: int
    success_rate: float


@dataclass
class TestResult:
    test_id: str
    status: TestStatus
    start_time: str
    end_time: str
    metrics: TestMetrics
    error_details: Optional[str] = None
    artifacts: Optional[list] = None


class UltimateConfigManager:
    """Enterprise-grade configuration management with hot-reload and validation"""

    def __init__(self, config_file: str = "config/ultimate_test_config.yaml"):
        self.config_file = config_file
        self.config_lock = threading.RLock()
        self.config_cache = {}
        self.watchers = []
        self.setup_logging()
        self.load_config()

    def setup_logging(self):
        """Setup comprehensive logging system"""
        log_format = '%(asctime)s - %(name)s - %(levelname)s - [%(filename)s:%(lineno)d] - %(message)s'

        logging.basicConfig(
            level=logging.INFO,
            format=log_format,
            handlers=[
                logging.FileHandler('test_automation.log'),
                logging.StreamHandler(sys.stdout)
            ]
        )

        self.logger = logging.getLogger('UltimateTestCoordinator')
        self.perf_logger = logging.getLogger('Performance')
        self.security_logger = logging.getLogger('Security')

    def load_config(self):
        """Load and validate configuration with advanced features"""
        default_config = {
            'execution': {
                'mode': 'adaptive',
                'max_parallel_tests': min(os.cpu_count() or 4, 8),
                'timeout_base': 30,
                'timeout_multiplier': 1.5,
                'adaptive_scaling': True,
                'resource_monitoring': True
            },
            'retry_policy': {
                'max_attempts': 5,
                'backoff_factor': 2.0,
                'backoff_max': 300,
                'exponential_base': 2,
                'jitter': True,
                'circuit_breaker_threshold': 0.5
            },
            'performance': {
                'memory_limit_mb': 2048,
                'cpu_limit_percent': 80,
                'enable_profiling': True,
                'metrics_collection': True,
                'auto_optimization': True
            },
            'security': {
                'encrypt_sensitive_data': True,
                'audit_logging': True,
                'rate_limiting': True,
                'input_validation': True
            },
            'ai_features': {
                'intelligent_test_generation': True,
                'self_healing_tests': True,
                'predictive_failure_analysis': True,
                'automatic_optimization': True
            },
            'integrations': {
                'jira_advanced_features': True,
                'slack_rich_notifications': True,
                'prometheus_metrics': True,
                'grafana_dashboards': True
            },
            'test_scenarios': {
                'login_form': {
                    'selectors': ['input[name="username"]', 'input[name="email"]', 'input[type="email"]', '#email', '#username'],
                    'password_selectors': ['input[name="password"]', 'input[type="password"]', '#password'],
                    'submit_selectors': ['button[type="submit"]', 'input[type="submit"]', '.login-btn', '.submit-btn', '#login'],
                    'success_indicators': ['dashboard', 'welcome', 'profile', 'logout', 'account', 'home'],
                    'failure_indicators': ['error', 'invalid', 'incorrect', 'failed', 'denied']
                },
                'contact_form': {
                    'selectors': ['input[name="name"]', '#contact-name', '.name-field', '#name'],
                    'email_selectors': ['input[name="email"]', 'input[type="email"]', '#email'],
                    'message_selectors': ['textarea[name="message"]', '#message', '.message-field', '#contact-message'],
                    'submit_selectors': ['button[type="submit"]', '.submit-btn', '#submit', '.contact-submit'],
                    'success_indicators': ['thank you', 'message sent', 'success', 'received', 'contact received'],
                    'failure_indicators': ['error', 'failed', 'invalid', 'required']
                },
                'registration_form': {
                    'selectors': ['input[name="username"]', 'input[name="firstname"]', '#username', '#firstname'],
                    'email_selectors': ['input[name="email"]', 'input[type="email"]', '#email'],
                    'password_selectors': ['input[name="password"]', '#password'],
                    'confirm_password_selectors': ['input[name="confirm_password"]', 'input[name="password_confirmation"]', '#confirm_password'],
                    'submit_selectors': ['button[type="submit"]', '.register-btn', '#register', '.signup-btn'],
                    'success_indicators': ['registration successful', 'account created', 'welcome', 'verify email'],
                    'failure_indicators': ['error', 'exists', 'invalid', 'weak password']
                },
                'search_form': {
                    'query_selectors': ['input[name="q"]', 'input[name="query"]', 'input[name="search"]', '#search', '.search-input'],
                    'submit_selectors': ['button[type="submit"]', '.search-btn', '#search-btn'],
                    'success_indicators': ['results', 'found', 'matches', 'search results'],
                    'failure_indicators': ['no results', 'not found', 'error']
                }
            }
        }

        with self.config_lock:
            if os.path.exists(self.config_file):
                try:
                    with open(self.config_file, 'r') as f:
                        loaded_config = yaml.safe_load(f)
                    self.config = self._merge_configs(default_config, loaded_config)
                    self._validate_config()
                except Exception as e:
                    self.logger.error(f"Error loading config: {e}. Using default config.")
                    self.config = default_config
            else:
                os.makedirs(os.path.dirname(self.config_file), exist_ok=True)
                self.config = default_config
                self.save_config()

    def _merge_configs(self, default: dict, loaded: dict) -> dict:
        """Deep merge configuration dictionaries"""
        for key, value in loaded.items():
            if key in default and isinstance(default[key], dict) and isinstance(value, dict):
                default[key] = self._merge_configs(default[key], value)
            else:
                default[key] = value
        return default

    def _validate_config(self):
        """Validate configuration parameters"""
        if self.config['execution']['max_parallel_tests'] > (os.cpu_count() or 4) * 2:
            self.logger.warning("max_parallel_tests exceeds recommended limit")

        if self.config['performance']['memory_limit_mb'] < 512:
            raise ValueError("memory_limit_mb too low, minimum 512MB required")

    def get(self, key: str, default: Any = None) -> Any:
        """Thread-safe configuration getter with caching"""
        with self.config_lock:
            if key in self.config_cache:
                return self.config_cache[key]

            keys = key.split('.')
            value = self.config
            for k in keys:
                if isinstance(value, dict) and k in value:
                    value = value[k]
                else:
                    value = default
                    break

            self.config_cache[key] = value
            return value

    def save_config(self):
        """Thread-safe configuration saver"""
        with self.config_lock:
            try:
                os.makedirs(os.path.dirname(self.config_file), exist_ok=True)
                with open(self.config_file, 'w') as f:
                    yaml.dump(self.config, f, default_flow_style=False, indent=2)
                self.config_cache.clear()
            except Exception as e:
                self.logger.error(f"Error saving config: {e}")


# Global configuration instance
config = UltimateConfigManager()
logger = logging.getLogger('UltimateTestCoordinator')