#!/bin/bash

# Ultimate Test Automation Coordinator - Dependency Installation Script

set -e

echo "Installing dependencies for Ultimate Test Automation Coordinator..."

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "Python 3 is required but not installed. Please install Python 3.8 or higher."
    exit 1
fi

# Check Python version
PYTHON_VERSION=$(python3 -c 'import sys; print(f"{sys.version_info.major}.{sys.version_info.minor}")')
if [[ $(echo "$PYTHON_VERSION < 3.8" | bc -l) -eq 1 ]]; then
    echo "Python 3.8 or higher is required. Current version: $PYTHON_VERSION"
    exit 1
fi

# Create virtual environment
echo "Creating virtual environment..."
python3 -m venv venv
source venv/bin/activate

# Upgrade pip
echo "Upgrading pip..."
pip install --upgrade pip

# Install dependencies from requirements.txt
echo "Installing Python dependencies..."
if [ -f "requirements.txt" ]; then
    pip install -r requirements.txt
else
    echo "requirements.txt not found. Installing core dependencies..."
    pip install crewai==0.28.8 crewai-tools==0.1.6 google-generativeai
    pip install jira pytest playwright pytest-html requests faker pyyaml pytest-xvfb
    pip install selenium webdriver-manager beautifulsoup4 aiohttp asyncio-throttle
    pip install pandas numpy matplotlib seaborn plotly dash
    pip install redis celery kombu prometheus-client
    pip install tenacity backoff pybreaker
    pip install memory-profiler psutil GPUtil py-cpuinfo
fi

# Install Playwright browsers
echo "Installing Playwright browsers..."
python -m playwright install

# Install ChromeDriver
echo "Installing ChromeDriver..."
python -c "
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service
service = Service(ChromeDriverManager().install())
print(f'ChromeDriver installed at: {service.path}')
"

# Create necessary directories
echo "Creating necessary directories..."
mkdir -p logs
mkdir -p reports
mkdir -p test_data
mkdir -p screenshots
mkdir -p test_sessions
mkdir -p config

# Create default config if it doesn't exist
if [ ! -f "config/ultimate_test_config.yaml" ]; then
    echo "Creating default configuration..."
    cat > config/ultimate_test_config.yaml << 'EOL'
execution:
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
EOL
fi

# Set up database
echo "Setting up database..."
python -c "
import sqlite3
conn = sqlite3.connect('test_results.db')
conn.execute('''CREATE TABLE IF NOT EXISTS test_results
               (id TEXT PRIMARY KEY, status TEXT, start_time TEXT,
                end_time TEXT, metrics TEXT, error_details TEXT)''')
conn.commit()
conn.close()
print('Database setup completed.')
"

echo "Dependency installation completed successfully!"
echo ""
echo "Next steps:"
echo "1. Set up your environment variables:"
echo "   - export JIRA_SERVER=your_jira_server"
echo "   - export JIRA_USERNAME=your_jira_username"
echo "   - export JIRA_API_TOKEN=your_jira_token"
echo "   - export GEMINI_API_KEY=your_gemini_api_key"
echo ""
echo "2. Activate the virtual environment: source venv/bin/activate"
echo ""
echo "3. Run the coordinator: python src/main.py --help"