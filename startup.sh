#!/bin/bash

echo "Starting application setup..."

# Install dependencies
echo "Installing dependencies..."
pip install -r requirements.txt

# Install Playwright browsers
echo "Installing Playwright browsers..."
playwright install chromium

# Set environment variables
export PYTHONPATH=/home/site/wwwroot
export FLASK_APP=main.py
export FLASK_ENV=production

# Start the application
echo "Starting Gunicorn..."
exec gunicorn --bind=0.0.0.0:8000 --timeout 600 --workers 4 --threads 2 --access-logfile '-' --error-logfile '-' main:app 