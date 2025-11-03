# AI Test Automation Agent

An intelligent test case generation system that leverages AI to analyze JIRA tickets and generate structured test scenarios. Features environment-based learning to improve test quality over time.

## Features

- AI-Powered Test Generation with Google Gemini
- JIRA Integration for ticket analysis
- Environment-based learning system
- Multiple output formats (JSON, CSV, Feature files)
- BDD scenario generation
- PyTest + Playwright test implementation
- Pattern recognition and test case reuse
- Similarity analysis for consistent testing

## Prerequisites

- Python 3.11+
- JIRA account with API access
- Google Gemini API key
- Required environment variables:
  ```
  JIRA_EMAIL=your.email@domain.com
  JIRA_API_TOKEN=your_api_token
  JIRA_SERVER=https://your-instance.atlassian.net
  GOOGLE_API_KEY=your_gemini_api_key
  ```

## Installation

1. Clone the repository:
```bash
git clone https://github.com/aukshwant2589/AI_Agent_For_Testing.git
cd AI_Agent_For_Testing
```

2. Create and activate virtual environment:
```bash
python -m venv myenv
source myenv/bin/activate  # Unix/macOS
myenv\Scripts\activate     # Windows
```

3. Install dependencies and set up Playwright:
```bash
# Install Python dependencies
pip install -r requirements.txt

# Install Playwright and its dependencies
playwright install

# Install pytest-html for report generation
pip install pytest-html pytest-playwright
```

## Usage

### Basic Test Generation
Generate test cases for a JIRA ticket:
```bash
python jira_analyzer_cli.py --ticket TICKET-ID
```

Example:
```bash
python jira_analyzer_cli.py --ticket KAN-1
```

### Using Full JIRA URL
```bash
python jira_analyzer_cli.py https://your-instance.atlassian.net/browse/TICKET-ID
```

## Output Structure
Generated files are organized as follows:
```
generated_tests/
└── TICKET-ID/
    ├── tests/
    │   └── test_cases.json    # Detailed test scenarios
    ├── test_cases.csv         # CSV format for easy viewing
    ├── TICKET-ID.feature      # Cucumber/Gherkin feature file
    └── test_TICKET-ID.py      # PyTest implementation
```

## Learning System Features

### Pattern Recognition
The agent automatically learns from existing test cases:
- Common prerequisites patterns
- Effective test step sequences
- Standard verification steps
- Naming conventions

### Test Case Preservation
- Maintains existing test cases without modification
- Updates only when explicitly requested
- Ensures testing consistency

### Similarity Analysis
- Matches new tickets with similar existing tests
- Suggests relevant test patterns
- Maintains consistent testing approaches

## Command Reference

### Standard Test Generation
```bash
# Basic test generation
python jira_analyzer_cli.py --ticket TICKET-ID

# Generate with specific output format
python jira_analyzer_cli.py --ticket TICKET-ID --format [json|csv|feature]

# Force regeneration of existing tests
python jira_analyzer_cli.py --ticket TICKET-ID --force

# Generate with enhanced learning
python jira_analyzer_cli.py --ticket TICKET-ID --learn
```

### Running Generated Playwright Tests
```bash
# Install Playwright browsers and dependencies
playwright install

# Run tests for a specific ticket
pytest generated_tests/test_KAN_1.py -v

# Run with HTML report
pytest generated_tests/test_KAN_1.py --html=generated_tests/KAN-1/reports/report.html

# Run in headed mode (visible browser)
pytest generated_tests/test_KAN_1.py --headed

# Run with specific browser
pytest generated_tests/test_KAN_1.py --browser chromium  # or firefox, webkit

# Run with debug mode
pytest generated_tests/test_KAN_1.py --slowmo 1000 --headed --debug
```

### Test Debugging Options
```bash
# Show test steps in console
pytest generated_tests/test_KAN_1.py -v --capture=no

# Save video recordings of test runs
pytest generated_tests/test_KAN_1.py --video=retain-on-failure

# Save screenshots on failure
pytest generated_tests/test_KAN_1.py --screenshot=only-on-failure
```

### Batch Operations
```bash
# Process multiple tickets
python jira_analyzer_cli.py --batch-file tickets.txt

# Generate tests for all tickets in a project
python jira_analyzer_cli.py --project PROJECT-KEY

# Run all generated tests
pytest generated_tests/test_*.py
```

## Configuration
Key configuration files:

### config/config.yaml
```yaml
jira:
  server: https://auxworx.atlassian.net
  project_key: KAN
  
test_generation:
  framework: playwright
  output_format: all
  learning_enabled: true
```

### config/ultimate_test_config.yaml
Advanced settings for test generation patterns and learning behavior.

## Test Reports and Artifacts

Generated test artifacts are organized as follows:
```
generated_tests/
└── TICKET-ID/
    ├── tests/
    │   └── test_cases.json
    ├── reports/
    │   ├── report.html       # Test execution report
    │   ├── assets/          # Report assets
    │   └── screenshots/     # Failure screenshots
    ├── playwright/
    │   ├── videos/          # Test execution recordings
    │   └── traces/          # Playwright trace files
    ├── test_cases.csv
    ├── TICKET-ID.feature
    └── test_TICKET-ID.py
```

## Project Structure
```
AI_Agent_For_Testing/
├── src/
│   ├── core/
│   │   ├── test_case_generator.py
│   │   └── learning/
│   │       └── test_case_analyzer.py
│   ├── agents/
│   └── utils/
├── config/
├── generated_tests/
└── tests/
```

## Error Handling

Common error codes:
- Exit Code 1: Configuration/environment issues
- Exit Code 2: JIRA API access problems
- Exit Code 3: Test generation failures

## Contributing
1. Fork the repository
2. Create a feature branch
3. Submit a pull request with description

## License
MIT License - See LICENSE file for details