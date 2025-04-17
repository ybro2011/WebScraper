#!/bin/bash

# Install dependencies
pip install -r requirements.txt

# Install Playwright browsers
playwright install chromium

# Start the application
gunicorn --bind=0.0.0.0:8000 --timeout 600 main:app 