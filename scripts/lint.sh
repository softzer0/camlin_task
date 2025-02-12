#!/bin/bash
set -e

# Run code formatting
poetry run black app tests

# Run linting
poetry run ruff app tests

# Run type checking
poetry run mypy app tests
