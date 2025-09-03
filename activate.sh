#!/bin/bash
# Activation script for Hyperpure scraper environment

echo "Activating Hyperpure Scraper Virtual Environment..."
source venv/bin/activate

echo "Virtual environment activated!"
echo "Available commands:"
echo "  python test_scraper.py                              - Test connectivity"
echo "  python hyperpure_scraper_enhanced.py                - Run basic scraper"
echo "  python hyperpure_scraper_enhanced.py --selenium     - Run with Selenium"
echo "  python hyperpure_scraper_enhanced.py --help         - Show all options"
echo ""
echo "To deactivate: type 'deactivate'"
