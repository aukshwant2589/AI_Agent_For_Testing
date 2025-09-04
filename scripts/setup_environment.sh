#!/bin/bash

# Ultimate Test Automation Coordinator - Environment Setup Script

set -e

echo "Setting up Ultimate Test Automation environment..."

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install --upgrade pip
pip install -r requirements.txt

# Install Playwright browsers
python -m playwright install

# Create necessary directories
mkdir -p logs
mkdir -p reports
mkdir -p test_data
mkdir -p screenshots

# Set up database
python -c "
import sqlite3
conn = sqlite3.connect('test_results.db')
conn.execute('''CREATE TABLE IF NOT EXISTS test_results
               (id TEXT PRIMARY KEY, status TEXT, start_time TEXT,
                end_time TEXT, metrics TEXT, error_details TEXT)''')
conn.commit()
conn.close()
"

echo "Environment setup completed successfully!"
echo "To activate virtual environment: source venv/bin/activate"
echo "To run the coordinator: python src/main.py --help"