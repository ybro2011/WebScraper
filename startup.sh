#!/bin/bash

# Create logs directory
mkdir -p /home/LogFiles

# Set up logging
exec 1> >(tee -a /home/LogFiles/python.log)
exec 2>&1

echo "Starting application setup at $(date)"

# Set environment variables
export PYTHONPATH=/home/site/wwwroot
export FLASK_APP=main.py
export FLASK_ENV=production
export PORT=8000

# Print environment information
echo "Python version: $(python --version)"
echo "Pip version: $(pip --version)"
echo "Current directory: $(pwd)"
echo "Contents of /home/site/wwwroot:"
ls -la /home/site/wwwroot

# Create and activate virtual environment
echo "Creating virtual environment..."
python -m venv /home/site/wwwroot/antenv
source /home/site/wwwroot/antenv/bin/activate

# Upgrade pip and install dependencies
echo "Upgrading pip and installing dependencies..."
python -m pip install --upgrade pip
echo "Installing requirements from /home/site/wwwroot/requirements.txt"
pip install -r /home/site/wwwroot/requirements.txt

# Verify installations
echo "Verifying installations..."
pip list

# Install Playwright browsers
echo "Installing Playwright browsers..."
playwright install chromium
playwright install firefox
playwright install webkit

# Start the application
echo "Starting Gunicorn server..."
gunicorn --bind=0.0.0.0:8000 --workers=2 --timeout=300 --access-logfile=- --error-logfile=- --log-level=debug main:app 