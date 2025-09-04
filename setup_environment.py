#!/usr/bin/env python3
"""
Setup script for Ultimate AI Test Automation Coordinator
"""

import os
import sys
import subprocess
import venv
from pathlib import Path

def create_virtual_environment():
    """Create virtual environment if it doesn't exist"""
    venv_path = Path("venv")
    if not venv_path.exists():
        print("Creating virtual environment...")
        venv.create(venv_path, with_pip=True)
        print("Virtual environment created.")
    else:
        print("Virtual environment already exists.")

def install_dependencies():
    """Install required dependencies"""
    # Determine the pip executable path
    if os.name == 'nt':  # Windows
        pip_path = Path("venv/Scripts/pip.exe")
    else:  # Unix/Linux/Mac
        pip_path = Path("venv/bin/pip")

    if not pip_path.exists():
        print("Error: pip not found in virtual environment")
        return False

    # Install requirements
    requirements_file = Path("requirements.txt")
    if requirements_file.exists():
        print("Installing dependencies from requirements.txt...")
        subprocess.run([str(pip_path), "install", "-r", "requirements.txt"], check=True)
    else:
        print("requirements.txt not found. Installing core dependencies...")
        core_deps = [
            "crewai==0.28.8", "crewai-tools==0.1.6", "google-generativeai==0.3.2",
            "jira==3.6.0", "pytest==7.4.3", "playwright==1.39.0", "pytest-html==4.0.2",
            "requests==2.31.0", "faker==19.6.2", "pyyaml==6.0.1", "pytest-xvfb==2.0.0",
            "selenium==4.15.0", "webdriver-manager==4.0.1", "beautifulsoup4==4.12.2",
            "aiohttp==3.9.1", "asyncio-throttle==1.0.2", "pandas==2.1.1", "numpy==1.25.2",
            "matplotlib==3.7.2", "seaborn==0.12.2", "plotly==5.17.0", "dash==2.14.1"
        ]
        subprocess.run([str(pip_path), "install"] + core_deps, check=True)

    print("Dependencies installed successfully.")
    return True

def setup_directories():
    """Create necessary directories"""
    directories = ["logs", "reports", "test_data", "screenshots", "test_sessions", "config"]
    for directory in directories:
        Path(directory).mkdir(exist_ok=True)
        print(f"Created directory: {directory}")

def create_default_config():
    """Create default configuration file if it doesn't exist"""
    config_path = Path("config/ultimate_test_config.yaml")
    if not config_path.exists():
        config_path.parent.mkdir(exist_ok=True)
        default_config = """execution:
  mode: adaptive
  max_parallel_tests: 8
  timeout_base: 30
  timeout_multiplier: 1.5
  adaptive_scaling: true
  resource_monitoring: true

retry_policy:
  max_attempts: 5
  backoff_factor: 2.0
  backoff_max: 300
  exponential_base: 2
  jitter: true
  circuit_breaker_threshold: 0.5

performance:
  memory_limit_mb: 2048
  cpu_limit_percent: 80
  enable_profiling: true
  metrics_collection: true
  auto_optimization: true

security:
  encrypt_sensitive_data: true
  audit_logging: true
  rate_limiting: true
  input_validation: true

ai_features:
  intelligent_test_generation: true
  self_healing_tests: true
  predictive_failure_analysis: true
  automatic_optimization: true

integrations:
  jira_advanced_features: true
  slack_rich_notifications: true
  prometheus_metrics: true
  grafana_dashboards: true

test_scenarios:
  login_form:
    selectors:
      - input[name="username"]
      - input[name="email"]
      - input[type="email"]
      - "#email"
      - "#username"
    password_selectors:
      - input[name="password"]
      - input[type="password"]
      - "#password"
    submit_selectors:
      - button[type="submit"]
      - input[type="submit"]
      - ".login-btn"
      - ".submit-btn"
      - "#login"
    success_indicators:
      - dashboard
      - welcome
      - profile
      - logout
      - account
      - home
    failure_indicators:
      - error
      - invalid
      - incorrect
      - failed
      - denied
"""
        with open(config_path, "w") as f:
            f.write(default_config)
        print("Default configuration file created.")

def main():
    """Main setup function"""
    print("Setting up Ultimate AI Test Automation Coordinator...")

    try:
        create_virtual_environment()
        setup_directories()
        create_default_config()

        # Install dependencies
        if install_dependencies():
            print("\nSetup completed successfully!")
            print("\nNext steps:")
            print("1. Activate virtual environment:")
            if os.name == 'nt':  # Windows
                print("   venv\\Scripts\\activate")
            else:  # Unix/Linux/Mac
                print("   source venv/bin/activate")
            print("2. Set up environment variables (JIRA_SERVER, JIRA_USERNAME, JIRA_API_TOKEN, GEMINI_API_KEY)")
            print("3. Run: python run.py --help")
        else:
            print("Setup failed during dependency installation.")

    except Exception as e:
        print(f"Setup failed with error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()