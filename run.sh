#!/bin/bash

# Exit immediately if a command exits with a non-zero status.
set -e

# Install all dependencies from requirements.txt
pip install -r requirements.txt

# Start the Gunicorn server
gunicorn src.main:app