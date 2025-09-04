import os
import json
import logging
import hashlib
import tempfile
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
from pathlib import Path


class HelperUtils:
    """Utility functions for the test automation framework"""

    @staticmethod
    def setup_logging(log_level: int = logging.INFO, log_file: str = "test_automation.log"):
        """Setup comprehensive logging configuration"""
        logging.basicConfig(
            level=log_level,
            format='%(asctime)s - %(name)s - %(levelname)s - [%(filename)s:%(lineno)d] - %(message)s',
            handlers=[
                logging.FileHandler(log_file),
                logging.StreamHandler()
            ]
        )
        return logging.getLogger('UltimateTestCoordinator')

    @staticmethod
    def load_json_file(file_path: str) -> Dict:
        """Load JSON data from file"""
        try:
            with open(file_path, 'r') as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError) as e:
            logging.error(f"Error loading JSON file {file_path}: {e}")
            return {}

    @staticmethod
    def save_json_file(data: Dict, file_path: str, indent: int = 2):
        """Save data to JSON file"""
        try:
            os.makedirs(os.path.dirname(file_path), exist_ok=True)
            with open(file_path, 'w') as f:
                json.dump(data, f, indent=indent, default=str)
        except Exception as e:
            logging.error(f"Error saving JSON file {file_path}: {e}")

    @staticmethod
    def generate_unique_id(prefix: str = "test") -> str:
        """Generate a unique identifier"""
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        random_hash = hashlib.md5(os.urandom(32)).hexdigest()[:8]
        return f"{prefix}_{timestamp}_{random_hash}"

    @staticmethod
    def format_duration(seconds: float) -> str:
        """Format duration in human-readable format"""
        if seconds < 1:
            return f"{seconds * 1000:.0f}ms"
        elif seconds < 60:
            return f"{seconds:.1f}s"
        elif seconds < 3600:
            minutes = seconds // 60
            seconds = seconds % 60
            return f"{minutes:.0f}m {seconds:.0f}s"
        else:
            hours = seconds // 3600
            minutes = (seconds % 3600) // 60
            return f"{hours:.0f}h {minutes:.0f}m"

    @staticmethod
    def safe_get(dictionary: Dict, keys: List[str], default: Any = None) -> Any:
        """Safely get nested dictionary values"""
        current = dictionary
        for key in keys:
            if isinstance(current, dict) and key in current:
                current = current[key]
            else:
                return default
        return current

    @staticmethod
    def create_temp_file(content: str, suffix: str = ".tmp") -> str:
        """Create a temporary file with content"""
        try:
            with tempfile.NamedTemporaryFile(mode='w', suffix=suffix, delete=False) as f:
                f.write(content)
                return f.name
        except Exception as e:
            logging.error(f"Error creating temp file: {e}")
            return ""

    @staticmethod
    def cleanup_temp_files(file_paths: List[str]):
        """Clean up temporary files"""
        for file_path in file_paths:
            try:
                if os.path.exists(file_path):
                    os.unlink(file_path)
            except Exception as e:
                logging.warning(f"Error cleaning up temp file {file_path}: {e}")

    @staticmethod
    def validate_email(email: str) -> bool:
        """Validate email format"""
        import re
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return bool(re.match(pattern, email))

    @staticmethod
    def validate_url(url: str) -> bool:
        """Validate URL format"""
        import re
        pattern = r'^https?://[^\s/$.?#].[^\s]*$'
        return bool(re.match(pattern, url))

    @staticmethod
    def retry_operation(operation, max_attempts: int = 3, delay: float = 1.0,
                       backoff: float = 2.0, exceptions: tuple = (Exception,)):
        """Retry an operation with exponential backoff"""
        import time
        attempt = 1
        while attempt <= max_attempts:
            try:
                return operation()
            except exceptions as e:
                if attempt == max_attempts:
                    raise e
                sleep_time = delay * (backoff ** (attempt - 1))
                logging.warning(f"Attempt {attempt} failed: {e}. Retrying in {sleep_time:.1f}s...")
                time.sleep(sleep_time)
                attempt += 1

    @staticmethod
    def format_file_size(size_bytes: int) -> str:
        """Format file size in human-readable format"""
        if size_bytes == 0:
            return "0B"
        size_names = ["B", "KB", "MB", "GB", "TB"]
        i = 0
        while size_bytes >= 1024 and i < len(size_names) - 1:
            size_bytes /= 1024.0
            i += 1
        return f"{size_bytes:.2f}{size_names[i]}"

    @staticmethod
    def get_file_hash(file_path: str, algorithm: str = "md5") -> str:
        """Calculate file hash"""
        hash_func = hashlib.new(algorithm)
        try:
            with open(file_path, "rb") as f:
                for chunk in iter(lambda: f.read(4096), b""):
                    hash_func.update(chunk)
            return hash_func.hexdigest()
        except Exception as e:
            logging.error(f"Error calculating file hash: {e}")
            return ""

    @staticmethod
    def deep_merge_dicts(dict1: Dict, dict2: Dict) -> Dict:
        """Deep merge two dictionaries"""
        result = dict1.copy()
        for key, value in dict2.items():
            if (key in result and isinstance(result[key], dict)
                and isinstance(value, dict)):
                result[key] = HelperUtils.deep_merge_dicts(result[key], value)
            else:
                result[key] = value
        return result