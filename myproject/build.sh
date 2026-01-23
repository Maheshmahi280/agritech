#!/usr/bin/env bash
# Render.com build script for AgriConnect

set -o errexit  # Exit on error

# Install dependencies
pip install --upgrade pip
pip install -r requirements.txt

# Navigate to backend directory
cd backend

# Collect static files
python manage.py collectstatic --no-input

# Run migrations
python manage.py migrate --no-input
