from collections import defaultdict
from datetime import datetime
from typing import Any, Callable
from .config_manager import logger


class CircuitBreakerManager:
    """Advanced circuit breaker for fault tolerance"""

    def __init__(self):
        self.circuit_breakers = {}
        self.failure_counts = defaultdict(int)
        self.last_failure_time = defaultdict(lambda: None)
        self.recovery_timeout = 60

    def protected_call(self, func_name: str, func: Callable, *args, **kwargs) -> Any:
        """Execute function with circuit breaker protection"""
        try:
            # Check if circuit is open
            if (self.last_failure_time[func_name] and
                (datetime.now() - self.last_failure_time[func_name]).total_seconds() < self.recovery_timeout and
                self.failure_counts[func_name] >= 5):
                raise Exception(f"Circuit breaker open for {func_name}")

            result = func(*args, **kwargs)
            self.failure_counts[func_name] = 0
            return result
        except Exception as e:
            self.failure_counts[func_name] += 1
            self.last_failure_time[func_name] = datetime.now()
            logger.error(f"Circuit breaker triggered for {func_name}: {e}")
            raise