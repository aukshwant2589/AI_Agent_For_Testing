# src/core/config_manager.py
import os
import threading
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
    """Simplified configuration management"""

    def __init__(self, config_file: str = "config/ultimate_test_config.yaml"):
        self.config_file = config_file
        self.config_lock = threading.RLock()
        self.config_cache = {}
        self.setup_logging()
        self.load_config()

    def setup_logging(self):
        """Setup comprehensive logging system"""
        log_format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'

        logging.basicConfig(
            level=logging.INFO,
            format=log_format,
            handlers=[
                logging.FileHandler('test_automation.log'),
                logging.StreamHandler(sys.stdout)
            ]
        )

        self.logger = logging.getLogger('UltimateTestCoordinator')

    def load_config(self):
        """Load configuration with default values"""
        self.config = {
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
                }
            }
        }

    def get(self, key: str, default: Any = None) -> Any:
        """Thread-safe configuration getter"""
        with self.config_lock:
            keys = key.split('.')
            value = self.config
            for k in keys:
                if isinstance(value, dict) and k in value:
                    value = value[k]
                else:
                    return default
            return value


# Global configuration instance
config = UltimateConfigManager()
logger = logging.getLogger('UltimateTestCoordinator')