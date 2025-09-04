#!/usr/bin/env python3
"""
Test script for Hyperpure scraper
Tests basic functionality and connectivity
"""

import requests
from bs4 import BeautifulSoup
import sys
import time

def test_basic_connectivity():
    """Test basic connectivity to Hyperpure website"""
    print("Testing basic connectivity...")
    
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        
        response = requests.get("https://www.hyperpure.com/in/Menu-Addons", headers=headers, timeout=10)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.content, 'lxml')
        title = soup.find('title')
        
        print(f"✓ Successfully connected to Hyperpure")
        print(f"✓ Page title: {title.get_text() if title else 'No title found'}")
        print(f"✓ Response status: {response.status_code}")
        print(f"✓ Content length: {len(response.content)} bytes")
        
        return True
        
    except Exception as e:
        print(f"✗ Connection failed: {str(e)}")
        return False

def test_product_detection():
    """Test if we can detect products on the main page"""
    print("\nTesting product detection...")
    
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        
        response = requests.get("https://www.hyperpure.com/in/Menu-Addons", headers=headers, timeout=10)
        soup = BeautifulSoup(response.content, 'lxml')
        
        # Look for product indicators
        links_with_product_pages = soup.find_all('a', href=lambda x: x and '/in/' in x and 'frozen' in x.lower())
        price_elements = soup.find_all(text=lambda x: x and '₹' in x)
        images = soup.find_all('img', src=lambda x: x and 'assets.hyperpure.com' in x)
        
        print(f"✓ Found {len(links_with_product_pages)} potential product links")
        print(f"✓ Found {len(price_elements)} price elements")
        print(f"✓ Found {len(images)} product images")
        
        # Show sample product links
        if links_with_product_pages:
            print("\nSample product links found:")
            for i, link in enumerate(links_with_product_pages[:3]):
                href = link.get('href', '')
                text = link.get_text().strip()[:50]
                print(f"  {i+1}. {text} -> {href}")
        
        return len(links_with_product_pages) > 0
        
    except Exception as e:
        print(f"✗ Product detection failed: {str(e)}")
        return False

def test_individual_product():
    """Test scraping an individual product page"""
    print("\nTesting individual product page...")
    
    # Test with a known product URL
    test_url = "https://www.hyperpure.com/in/walnut-brownie-80-gm-pc-pack-of-9-frozen"
    
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        
        response = requests.get(test_url, headers=headers, timeout=10)
        soup = BeautifulSoup(response.content, 'lxml')
        
        # Extract basic product info
        title = soup.find('title')
        h1_elements = soup.find_all('h1')
        price_text = soup.get_text()
        
        print(f"✓ Successfully loaded product page")
        print(f"✓ Page title: {title.get_text()[:100] if title else 'No title'}")
        
        if h1_elements:
            print(f"✓ Product name: {h1_elements[0].get_text()[:50]}")
        
        # Look for price
        import re
        price_match = re.search(r'₹(\d+(?:,\d+)*)', price_text)
        if price_match:
            print(f"✓ Price found: ₹{price_match.group(1)}")
        
        return True
        
    except Exception as e:
        print(f"✗ Individual product test failed: {str(e)}")
        return False

def main():
    """Run all tests"""
    print("Hyperpure Scraper Test Suite")
    print("=" * 40)
    
    tests = [
        test_basic_connectivity,
        test_product_detection,
        test_individual_product
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        try:
            if test():
                passed += 1
            time.sleep(1)  # Small delay between tests
        except Exception as e:
            print(f"✗ Test {test.__name__} crashed: {str(e)}")
    
    print("\n" + "=" * 40)
    print(f"Tests passed: {passed}/{total}")
    
    if passed == total:
        print("✓ All tests passed! The scraper should work correctly.")
        return 0
    else:
        print("✗ Some tests failed. Check the logs above.")
        return 1

if __name__ == "__main__":
    sys.exit(main())
