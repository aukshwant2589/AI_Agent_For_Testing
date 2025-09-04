@echo off
echo Ultimate Test Automation Coordinator - Windows Setup
echo ===================================================

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo Python is not installed or not in PATH.
    echo Please install Python 3.8 or higher from https://python.org
    pause
    exit /b 1
)

REM Check Python version
for /f "tokens=2 delims= " %%i in ('python --version 2^>^&1') do set PYTHON_VERSION=%%i
echo Python version: %PYTHON_VERSION%

REM Create virtual environment
echo Creating virtual environment...
python -m venv venv

REM Activate virtual environment
call venv\Scripts\activate.bat

REM Upgrade pip
echo Upgrading pip...
python -m pip install --upgrade pip

REM Install dependencies
echo Installing Python dependencies...
if exist requirements.txt (
    pip install -r requirements.txt
) else (
    echo requirements.txt not found. Installing core dependencies...
    pip install crewai==0.28.8 crewai-tools==0.1.6 google-generativeai
    pip install jira pytest playwright pytest-html requests faker pyyaml pytest-xvfb
    pip install selenium webdriver-manager beautifulsoup4 aiohttp asyncio-throttle
    pip install pandas numpy matplotlib seaborn plotly dash
    pip install redis celery kombu prometheus-client
    pip install tenacity backoff pybreaker
    pip install memory-profiler psutil GPUtil py-cpuinfo
)

REM Install Playwright browsers
echo Installing Playwright browsers...
python -m playwright install

REM Install ChromeDriver
echo Installing ChromeDriver...
python -c "from webdriver_manager.chrome import ChromeDriverManager; from selenium.webdriver.chrome.service import Service; service = Service(ChromeDriverManager().install()); print(f'ChromeDriver installed at: {service.path}')"

REM Create necessary directories
echo Creating necessary directories...
if not exist logs mkdir logs
if not exist reports mkdir reports
if not exist test_data mkdir test_data
if not exist screenshots mkdir screenshots
if not exist test_sessions mkdir test_sessions
if not exist config mkdir config

REM Create default config if it doesn't exist
if not exist config\ultimate_test_config.yaml (
    echo Creating default configuration...
    (
    echo execution:
    echo   mode: adaptive
    echo   max_parallel_tests: 8
    echo   timeout_base: 30
    echo   timeout_multiplier: 1.5
    echo   adaptive_scaling: true
    echo   resource_monitoring: true
    echo.
    echo retry_policy:
    echo   max_attempts: 5
    echo   backoff_factor: 2.0
    echo   backoff_max: 300
    echo   exponential_base: 2
    echo   jitter: true
    echo   circuit_breaker_threshold: 0.5
    echo.
    echo performance:
    echo   memory_limit_mb: 2048
    echo   cpu_limit_percent: 80
    echo   enable_profiling: true
    echo   metrics_collection: true
    echo   auto_optimization: true
    echo.
    echo security:
    echo   encrypt_sensitive_data: true
    echo   audit_logging: true
    echo   rate_limiting: true
    echo   input_validation: true
    echo.
    echo ai_features:
    echo   intelligent_test_generation: true
    echo   self_healing_tests: true
    echo   predictive_failure_analysis: true
    echo   automatic_optimization: true
    echo.
    echo integrations:
    echo   jira_advanced_features: true
    echo   slack_rich_notifications: true
    echo   prometheus_metrics: true
    echo   grafana_dashboards: true
    echo.
    echo test_scenarios:
    echo   login_form:
    echo     selectors:
    echo       - input[name="username"]
    echo       - input[name="email"]
    echo       - input[type="email"]
    echo       - "#email"
    echo       - "#username"
    echo     password_selectors:
    echo       - input[name="password"]
    echo       - input[type="password"]
    echo       - "#password"
    echo     submit_selectors:
    echo       - button[type="submit"]
    echo       - input[type="submit"]
    echo       - ".login-btn"
    echo       - ".submit-btn"
    echo       - "#login"
    echo     success_indicators:
    echo       - dashboard
    echo       - welcome
    echo       - profile
    echo       - logout
    echo       - account
    echo       - home
    echo     failure_indicators:
    echo       - error
    echo       - invalid
    echo       - incorrect
    echo       - failed
    echo       - denied
    ) > config\ultimate_test_config.yaml
)

REM Set up database
echo Setting up database...
python -c "import sqlite3; conn = sqlite3.connect('test_results.db'); conn.execute('CREATE TABLE IF NOT EXISTS test_results (id TEXT PRIMARY KEY, status TEXT, start_time TEXT, end_time TEXT, metrics TEXT, error_details TEXT)'); conn.commit(); conn.close(); print('Database setup completed.')"

echo.
echo Setup completed successfully!
echo.
echo Next steps:
echo 1. Set your environment variables:
echo    set JIRA_SERVER=your_jira_server
echo    set JIRA_USERNAME=your_jira_username
echo    set JIRA_API_TOKEN=your_jira_token
echo    set GEMINI_API_KEY=your_gemini_api_key
echo.
echo 2. Activate the virtual environment: venv\Scripts\activate.bat
echo.
echo 3. Run the coordinator: python src\main.py --help
echo.
pause