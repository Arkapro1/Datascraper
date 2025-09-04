#!/usr/bin/env python3
"""
Hyperpure.com Targeted Product Scraper
=====================================

A more targeted scraper specifically designed for Hyperpure's HTML structure
based on the successful test results.

Requirements: requests, beautifulsoup4, lxml, pandas

Author: AI Assistant
Date: 2025-09-03
"""

import requests
from bs4 import BeautifulSoup
import csv
import time
import logging
import re
from urllib.parse import urljoin, urlparse
from datetime import datetime
import json
from typing import List, Dict, Optional, Set
import random
from dataclasses import dataclass
import sys


# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('hyperpure_targeted_scraper.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)


@dataclass
class Product:
    """Data class to represent a product with all required fields"""
    product_name: str = ""
    category: str = ""
    subcategory: str = ""
    price_current: str = ""
    price_original: str = ""
    discount_percentage: str = ""
    product_description: str = ""
    product_image_url: str = ""
    product_page_url: str = ""
    availability_status: str = ""
    brand_name: str = "Hyperpure"
    unit_size: str = ""
    packaging_type: str = ""
    nutritional_info: str = ""
    ingredients: str = ""
    product_id: str = ""
    sku_code: str = ""
    rating: str = ""
    review_count: str = ""
    tags: str = ""
    scraped_timestamp: str = ""

    def to_dict(self) -> Dict[str, str]:
        """Convert to dictionary for CSV writing"""
        return {
            'product_name': self.product_name,
            'category': self.category,
            'subcategory': self.subcategory,
            'price_current': self.price_current,
            'price_original': self.price_original,
            'discount_percentage': self.discount_percentage,
            'product_description': self.product_description,
            'product_image_url': self.product_image_url,
            'product_page_url': self.product_page_url,
            'availability_status': self.availability_status,
            'brand_name': self.brand_name,
            'unit_size': self.unit_size,
            'packaging_type': self.packaging_type,
            'nutritional_info': self.nutritional_info,
            'ingredients': self.ingredients,
            'product_id': self.product_id,
            'sku_code': self.sku_code,
            'rating': self.rating,
            'review_count': self.review_count,
            'tags': self.tags,
            'scraped_timestamp': self.scraped_timestamp
        }


class HyperpureTargetedScraper:
    """Targeted scraper specifically for Hyperpure.com Menu Add-ons"""
    
    def __init__(self):
        self.base_url = "https://www.hyperpure.com"
        self.session = requests.Session()
        self.setup_session()
        self.scraped_urls: Set[str] = set()
        self.products: List[Product] = []
        
    def setup_session(self):
        """Configure session with headers for ethical scraping"""
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'DNT': '1',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
        }
        self.session.headers.update(headers)
        
    def safe_request(self, url: str, max_retries: int = 3) -> Optional[BeautifulSoup]:
        """Make a safe HTTP request with retries and delays"""
        for attempt in range(max_retries):
            try:
                time.sleep(random.uniform(1, 3))
                
                response = self.session.get(url, timeout=30)
                response.raise_for_status()
                
                logger.info(f"Successfully fetched: {url}")
                return BeautifulSoup(response.content, 'lxml')
                
            except requests.exceptions.RequestException as e:
                logger.warning(f"Attempt {attempt + 1} failed for {url}: {str(e)}")
                if attempt == max_retries - 1:
                    logger.error(f"All attempts failed for {url}")
                    return None
                time.sleep(random.uniform(2, 5))
                
        return None
    
    def clean_text(self, text: str) -> str:
        """Clean and normalize text content"""
        if not text:
            return ""
        
        # Remove extra whitespace and normalize
        cleaned = re.sub(r'\s+', ' ', text.strip())
        
        # Remove special characters that might break CSV
        cleaned = cleaned.replace('"', '""')  # Escape quotes for CSV
        
        return cleaned
    
    def extract_price_info(self, price_text: str) -> tuple[str, str, str]:
        """Extract current price, original price, and discount percentage"""
        current_price = ""
        original_price = ""
        discount_pct = ""
        
        if not price_text:
            return current_price, original_price, discount_pct
        
        # Extract all prices from text
        price_matches = re.findall(r'₹(\d+(?:,\d+)*(?:\.\d+)?)', price_text)
        
        if price_matches:
            # Assume first price is current price
            current_price = f"₹{price_matches[0]}"
            
            # If multiple prices, second might be original
            if len(price_matches) > 1:
                original_price = f"₹{price_matches[1]}"
                
                # Calculate discount
                try:
                    current_val = float(re.sub(r'[₹,]', '', current_price))
                    original_val = float(re.sub(r'[₹,]', '', original_price))
                    if original_val > current_val:
                        discount_pct = f"{((original_val - current_val) / original_val * 100):.1f}%"
                except (ValueError, ZeroDivisionError):
                    pass
        
        return current_price, original_price, discount_pct
    
    def extract_unit_size(self, text: str) -> str:
        """Extract unit size information from product text"""
        if not text:
            return ""
        
        # Common patterns for unit sizes
        size_patterns = [
            r'(\d+(?:\.\d+)?\s*(?:gm|kg|ml|ltr|litre|pc|pcs|piece|pieces|pack|packs))',
            r'(\d+(?:\.\d+)?\s*(?:gram|kilogram|milliliter|liter))',
            r'\((\d+(?:\.\d+)?\s*(?:gm|kg|ml|ltr|pc|pcs)/?\w*)\)',
            r'(\d+(?:\.\d+)?\s*(?:g|kg|ml|l)\b)'
        ]
        
        for pattern in size_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                return match.group(1).strip()
        
        return ""
    
    def extract_products_from_main_page(self, soup: BeautifulSoup) -> List[Product]:
        """Extract products directly from the main Menu Add-ons page"""
        products = []
        
        # Based on the test, we know there are links like:
        # https://www.hyperpure.com/in/walnut-brownie-80-gm-pc-pack-of-9-frozen?source=CATEGORY
        
        # Find all product links that match the pattern
        product_links = []
        
        # Look for links that contain product patterns
        for link in soup.find_all('a', href=True):
            href = link['href']
            if (href.startswith('/in/') and 
                any(keyword in href.lower() for keyword in ['frozen', 'pack', 'gm', 'kg', 'pc']) and
                href.count('-') > 2):  # Product URLs tend to have many hyphens
                
                full_url = urljoin(self.base_url, href)
                product_name = self.clean_text(link.get_text())
                
                if product_name and len(product_name) > 5:  # Filter out short non-product text
                    product_links.append((product_name, full_url))
        
        # Remove duplicates
        product_links = list(set(product_links))
        
        logger.info(f"Found {len(product_links)} potential product links")
        
        # Extract basic info for each product
        for product_name, product_url in product_links:
            product = Product()
            product.scraped_timestamp = datetime.now().isoformat()
            product.category = "Menu Add-ons"
            product.product_name = product_name
            product.product_page_url = product_url
            product.unit_size = self.extract_unit_size(product_name)
            
            # Extract price from the current page if visible
            # Look for price near the product link
            parent = soup.find('a', href=product_url.replace(self.base_url, ''))
            if parent:
                # Look for price in surrounding text
                surrounding_text = ""
                for sibling in parent.parent.find_all(string=True):
                    surrounding_text += sibling + " "
                
                product.price_current, product.price_original, product.discount_percentage = self.extract_price_info(surrounding_text)
            
            # Determine packaging type
            if 'frozen' in product_name.lower():
                product.packaging_type = "Frozen"
            elif 'fresh' in product_name.lower():
                product.packaging_type = "Fresh"
            
            # Set availability (assume in stock if we can see it)
            product.availability_status = "In Stock"
            
            products.append(product)
            logger.info(f"Extracted basic info for: {product.product_name}")
        
        return products
    
    def scrape_product_details(self, product: Product) -> Product:
        """Scrape detailed information from individual product page"""
        if not product.product_page_url or product.product_page_url in self.scraped_urls:
            return product
        
        soup = self.safe_request(product.product_page_url)
        if not soup:
            return product
        
        self.scraped_urls.add(product.product_page_url)
        
        try:
            # Get page title for product name if not already set
            if not product.product_name:
                title = soup.find('title')
                if title:
                    product.product_name = self.clean_text(title.get_text().split('|')[0])
            
            # Look for h1 tag which often contains the product name
            h1_tag = soup.find('h1')
            if h1_tag and not product.product_name:
                product.product_name = self.clean_text(h1_tag.get_text())
            
            # Extract description from page content
            page_text = soup.get_text()
            
            # Look for product description patterns
            desc_patterns = [
                r'premium\s+[^.]+[.!]',
                r'[A-Z][^.]+(?:brownies?|patty|sauce|kebab|wings)[^.]*[.!]',
                r'indulge\s+[^.]+[.!]',
                r'crafted\s+[^.]+[.!]'
            ]
            
            for pattern in desc_patterns:
                match = re.search(pattern, page_text, re.IGNORECASE | re.DOTALL)
                if match:
                    desc = self.clean_text(match.group(0))
                    if len(desc) > 50:  # Ensure substantial description
                        product.product_description = desc
                        break
            
            # Extract price information from page
            price_text = page_text
            if not product.price_current:
                product.price_current, product.price_original, product.discount_percentage = self.extract_price_info(price_text)
            
            # Look for images
            images = soup.find_all('img')
            for img in images:
                src = img.get('src') or img.get('data-src')
                if src and 'assets.hyperpure.com' in src and 'products' in src:
                    product.product_image_url = urljoin(self.base_url, src)
                    break
            
            # Extract ingredients if mentioned
            if 'ingredients' in page_text.lower():
                ingredients_match = re.search(r'ingredients?[:\s]+(.*?)(?:\n|\.|\||$)', page_text, re.IGNORECASE)
                if ingredients_match:
                    product.ingredients = self.clean_text(ingredients_match.group(1))
            
            # Extract features/tags
            feature_keywords = ['premium', 'imported', 'handcrafted', 'frozen', 'fresh', 'organic', 'natural']
            tags = []
            for keyword in feature_keywords:
                if keyword.lower() in page_text.lower():
                    tags.append(keyword.title())
            
            if tags:
                product.tags = ";".join(tags)
            
            # Extract SKU from URL
            url_path = urlparse(product.product_page_url).path
            sku_match = re.search(r'/([a-zA-Z0-9\-_]+)(?:\?|$)', url_path)
            if sku_match:
                product.sku_code = sku_match.group(1)
            
            # Update unit size if we find more detailed info
            if not product.unit_size:
                product.unit_size = self.extract_unit_size(page_text)
            
        except Exception as e:
            logger.error(f"Error scraping product details for {product.product_page_url}: {str(e)}")
        
        return product
    
    def scrape_all_products(self) -> List[Product]:
        """Main method to scrape all products"""
        logger.info("Starting targeted Hyperpure scraping process...")
        
        # Start from the main Menu Add-ons page
        main_url = f"{self.base_url}/in/Menu-Addons"
        soup = self.safe_request(main_url)
        
        if not soup:
            logger.error("Failed to fetch main page")
            return []
        
        # Extract products from main page
        main_products = self.extract_products_from_main_page(soup)
        logger.info(f"Found {len(main_products)} products on main page")
        
        # Get detailed information for each product
        for i, product in enumerate(main_products):
            logger.info(f"Processing product {i+1}/{len(main_products)}: {product.product_name}")
            detailed_product = self.scrape_product_details(product)
            self.products.append(detailed_product)
            
            # Add a small delay between requests
            time.sleep(random.uniform(1, 2))
        
        logger.info(f"Scraping completed. Total products: {len(self.products)}")
        return self.products
    
    def save_to_csv(self, filename: str = "hyperpure_products_targeted.csv"):
        """Save scraped products to CSV file"""
        if not self.products:
            logger.error("No products to save")
            return
        
        fieldnames = [
            'product_name', 'category', 'subcategory', 'price_current', 'price_original',
            'discount_percentage', 'product_description', 'product_image_url', 'product_page_url',
            'availability_status', 'brand_name', 'unit_size', 'packaging_type', 'nutritional_info',
            'ingredients', 'product_id', 'sku_code', 'rating', 'review_count', 'tags', 'scraped_timestamp'
        ]
        
        try:
            with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                writer.writeheader()
                
                for product in self.products:
                    writer.writerow(product.to_dict())
            
            logger.info(f"Successfully saved {len(self.products)} products to {filename}")
            
        except Exception as e:
            logger.error(f"Error saving to CSV: {str(e)}")


def main():
    """Main function to run the targeted scraper"""
    scraper = HyperpureTargetedScraper()
    
    try:
        # Scrape all products
        products = scraper.scrape_all_products()
        
        if products:
            # Save to CSV
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"hyperpure_products_targeted_{timestamp}.csv"
            scraper.save_to_csv(filename)
            
            print(f"\nScraping completed successfully!")
            print(f"Total products scraped: {len(products)}")
            print(f"Data saved to: {filename}")
            
            # Print sample products
            print(f"\nSample products scraped:")
            for i, product in enumerate(products[:5]):
                print(f"{i+1}. {product.product_name} - {product.price_current}")
                
        else:
            print("No products were scraped. Please check the logs for errors.")
            
    except KeyboardInterrupt:
        logger.info("Scraping interrupted by user")
        print("\nScraping interrupted. Saving partial data...")
        if scraper.products:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"hyperpure_products_targeted_partial_{timestamp}.csv"
            scraper.save_to_csv(filename)
            print(f"Partial data saved to: {filename}")
            
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        print(f"An error occurred: {str(e)}")


if __name__ == "__main__":
    main()
