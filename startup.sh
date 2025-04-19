#!/bin/bash

# Create logs directory
mkdir -p /home/LogFiles

# Set up logging
exec 1> >(tee -a /home/LogFiles/startup.log)
exec 2>&1

echo "Starting application setup..."

# Set environment variables
export PYTHONPATH=/home/site/wwwroot
export FLASK_APP=main.py
export FLASK_ENV=production
export PORT=8000

# Use the correct Python path
export PATH="/opt/python/3.9.21/bin:$PATH"

# Create and activate virtual environment
echo "Setting up virtual environment..."
python -m venv /home/site/wwwroot/antenv
source /home/site/wwwroot/antenv/bin/activate

# Upgrade pip and install dependencies
echo "Upgrading pip and installing dependencies..."
python -m pip install --upgrade pip
pip install --no-cache-dir -r requirements.txt
if [ $? -ne 0 ]; then
    echo "Failed to install dependencies"
    exit 1
fi

# Install Playwright browsers
echo "Installing Playwright browsers..."
playwright install chromium
if [ $? -ne 0 ]; then
    echo "Failed to install Playwright browsers"
    exit 1
fi

# Start the application with Gunicorn
echo "Starting Gunicorn application..."
exec gunicorn --config gunicorn_config.py main:app 