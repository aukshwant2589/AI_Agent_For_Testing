import sqlite3
import logging
from contextlib import contextmanager
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from .config_manager import config, logger


class ResourceManager:
    """Intelligent resource management and optimization"""

    def __init__(self):
        self.resource_pools = {}
        self.allocation_history = []
        self.optimization_enabled = config.get('performance.auto_optimization', True)

    @contextmanager
    def managed_resource(self, resource_type: str, **kwargs):
        """Context manager for automatic resource management"""
        resource = None
        try:
            resource = self._allocate_resource(resource_type, **kwargs)
            yield resource
        finally:
            if resource:
                self._release_resource(resource_type, resource)

    def _allocate_resource(self, resource_type: str, **kwargs):
        """Allocate resource with intelligent pooling"""
        if resource_type == 'webdriver':
            return self._create_optimized_webdriver(**kwargs)
        elif resource_type == 'database_connection':
            return self._create_database_connection(**kwargs)
        else:
            raise ValueError(f"Unknown resource type: {resource_type}")

    def _create_optimized_webdriver(self, **kwargs):
        """Create optimized WebDriver instance"""
        options = webdriver.ChromeOptions()

        options.add_argument('--headless')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('--disable-gpu')
        options.add_argument('--disable-extensions')
        options.add_argument('--disable-plugins')
        options.add_argument('--disable-images')
        options.add_argument('--disable-javascript')
        options.add_argument('--memory-pressure-off')
        options.add_argument('--max_old_space_size=4096')

        options.add_argument('--virtual-time-budget=5000')
        options.add_argument('--run-all-compositor-stages-before-draw')

        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=options)
        driver.set_window_size(1920, 1080)

        return driver

    def _create_database_connection(self, **kwargs):
        """Create optimized database connection"""
        db_path = kwargs.get('db_path', 'test_results.db')
        conn = sqlite3.connect(db_path, check_same_thread=False)
        conn.execute('''CREATE TABLE IF NOT EXISTS test_results
                       (id TEXT PRIMARY KEY, status TEXT, start_time TEXT,
                        end_time TEXT, metrics TEXT, error_details TEXT)''')
        return conn

    def _release_resource(self, resource_type: str, resource):
        """Release resource with cleanup"""
        try:
            if resource_type == 'webdriver' and resource:
                resource.quit()
            elif resource_type == 'database_connection' and resource:
                resource.close()
        except Exception as e:
            logger.error(f"Error releasing {resource_type}: {e}")