#!/bin/bash

# Activate virtual environment if it exists
if [ -d "antenv" ]; then
    source antenv/bin/activate
fi

# Install dependencies if requirements.txt exists
if [ -f "requirements.txt" ]; then
    pip install -r requirements.txt
fi

# Install Playwright browsers
playwright install chromium

# Start the application
gunicorn --bind=0.0.0.0:$PORT --timeout 600 main:app 