#!/bin/bash
# Script to publish PeiDocker to PyPI

set -e  # Exit on error

echo "PeiDocker PyPI Publication Script"
echo "================================="

# Clean previous builds
echo "Cleaning previous builds..."
rm -rf dist/ build/ *.egg-info/

# Build the package
echo "Building package..."
python -m build

# Show what will be uploaded
echo "Package contents:"
ls -la dist/

# Ask for confirmation
echo ""
read -p "Do you want to upload to TestPyPI first? (y/n) " -n 1 -r
echo ""

if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo "Uploading to TestPyPI..."
    python -m twine upload --repository testpypi dist/*
    echo ""
    echo "Test installation with:"
    echo "  pip install --index-url https://test.pypi.org/simple/ --extra-index-url https://pypi.org/simple/ pei-docker"
    echo ""
    read -p "Continue to upload to PyPI? (y/n) " -n 1 -r
    echo ""
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo "Aborted."
        exit 1
    fi
fi

# Upload to PyPI
echo "Uploading to PyPI..."
python -m twine upload dist/*

echo ""
echo "Successfully published to PyPI!"
echo "Install with: pip install pei-docker"