#!/bin/bash

# Script to run API integration tests
# Usage: ./run_api_tests.sh [test_class_name]

cd "$(dirname "$0")"

# Activate virtual environment if it exists
if [ -d "venv" ]; then
    source venv/bin/activate
fi

# Run tests
if [ -z "$1" ]; then
    # Run all API integration tests
    python3 -m pytest tests/integration/test_api_endpoints.py -v --tb=short
else
    # Run specific test class
    python3 -m pytest tests/integration/test_api_endpoints.py::$1 -v --tb=short
fi
