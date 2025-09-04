Write-Host "Ultimate Test Automation Coordinator - Windows Setup" -ForegroundColor Green
Write-Host "===================================================" -ForegroundColor Green

# Check if Python is installed
try {
    $pythonVersion = python --version 2>&1
    Write-Host "Python version: $pythonVersion" -ForegroundColor Green
} catch {
    Write-Host "Python is not installed or not in PATH." -ForegroundColor Red
    Write-Host "Please install Python 3.8 or higher from https://python.org" -ForegroundColor Red
    pause
    exit 1
}

# Create virtual environment
Write-Host "Creating virtual environment..." -ForegroundColor Yellow
python -m venv venv

# Activate virtual environment
Write-Host "Activating virtual environment..." -ForegroundColor Yellow
.\venv\Scripts\Activate.ps1

# Upgrade pip
Write-Host "Upgrading pip..." -ForegroundColor Yellow
python -m pip install --upgrade pip

# Install dependencies
Write-Host "Installing Python dependencies..." -ForegroundColor Yellow
if (Test-Path "requirements.txt") {
    pip install -r requirements.txt
} else {
    Write-Host "requirements.txt not found. Installing core dependencies..." -ForegroundColor Yellow
    pip install crewai==0.28.8 crewai-tools==0.1.6 google-generativeai
    pip install jira pytest playwright pytest-html requests faker pyyaml pytest-xvfb
    pip install selenium webdriver-manager beautifulsoup4 aiohttp asyncio-throttle
    pip install pandas numpy matplotlib seaborn plotly dash
    pip install redis celery kombu prometheus-client
    pip install tenacity backoff pybreaker
    pip install memory-profiler psutil GPUtil py-cpuinfo
}

# Install Playwright browsers
Write-Host "Installing Playwright browsers..." -ForegroundColor Yellow
python -m playwright install

# Install ChromeDriver
Write-Host "Installing ChromeDriver..." -ForegroundColor Yellow
python -c "from webdriver_manager.chrome import ChromeDriverManager; from selenium.webdriver.chrome.service import Service; service = Service(ChromeDriverManager().install()); print(f'ChromeDriver installed at: {service.path}')"

# Create necessary directories
Write-Host "Creating necessary directories..." -ForegroundColor Yellow
@("logs", "reports", "test_data", "screenshots", "test_sessions", "config") | ForEach-Object {
    if (!(Test-Path $_)) { New-Item -ItemType Directory -Path $_ | Out-Null }
}

# Create default config if it doesn't exist
if (!(Test-Path "config\ultimate_test_config.yaml")) {
    Write-Host "Creating default configuration..." -ForegroundColor Yellow
    $configContent = @"
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
"@
    Set-Content -Path "config\ultimate_test_config.yaml" -Value $configContent
}

# Set up database
Write-Host "Setting up database..." -ForegroundColor Yellow
python -c "import sqlite3; conn = sqlite3.connect('test_results.db'); conn.execute('CREATE TABLE IF NOT EXISTS test_results (id TEXT PRIMARY KEY, status TEXT, start_time TEXT, end_time TEXT, metrics TEXT, error_details TEXT)'); conn.commit(); conn.close(); print('Database setup completed.')"

Write-Host "`nSetup completed successfully!" -ForegroundColor Green
Write-Host "`nNext steps:" -ForegroundColor Yellow
Write-Host "1. Set your environment variables:" -ForegroundColor Yellow
Write-Host "   `$env:JIRA_SERVER = 'your_jira_server'" -ForegroundColor Cyan
Write-Host "   `$env:JIRA_USERNAME = 'your_jira_username'" -ForegroundColor Cyan
Write-Host "   `$env:JIRA_API_TOKEN = 'your_jira_token'" -ForegroundColor Cyan
Write-Host "   `$env:GEMINI_API_KEY = 'your_gemini_api_key'" -ForegroundColor Cyan
Write-Host "`n2. Activate the virtual environment: .\venv\Scripts\Activate.ps1" -ForegroundColor Yellow
Write-Host "`n3. Run the coordinator: python src\main.py --help" -ForegroundColor Yellow

pause