#!/usr/bin/env python3
"""
Hyperpure.com Product Scraper
============================

A comprehensive web scraper to extract product listings from Hyperpure.com Menu Add-ons
and export them to a detailed CSV file.

Requirements:
- requests==2.31.0
- beautifulsoup4==4.12.2
- lxml==4.9.3
- pandas==2.0.3
- selenium==4.15.0 (optional, for JS-heavy content)
- webdriver-manager==4.0.1 (optional, for Selenium)

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
        logging.FileHandler('hyperpure_scraper.log'),
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


class HyperpureScraper:
    """Main scraper class for Hyperpure.com"""
    
    def __init__(self):
        self.base_url = "https://www.hyperpure.com"
        self.session = requests.Session()
        self.setup_session()
        self.scraped_urls: Set[str] = set()
        self.products: List[Product] = []
        
    def setup_session(self):
        """Configure session with headers and settings for ethical scraping"""
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'DNT': '1',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'none',
            'Cache-Control': 'max-age=0'
        }
        self.session.headers.update(headers)
        
    def safe_request(self, url: str, max_retries: int = 3) -> Optional[BeautifulSoup]:
        """Make a safe HTTP request with retries and delays"""
        for attempt in range(max_retries):
            try:
                # Random delay between 1-3 seconds for ethical scraping
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
                time.sleep(random.uniform(2, 5))  # Longer delay before retry
                
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
        
        # TODO: Add specific price extraction logic based on HTML structure
        # Common patterns: ₹199, ₹199/pack, strikethrough prices, discount percentages
        
        # Extract current price
        current_match = re.search(r'₹(\d+(?:,\d+)*(?:\.\d+)?)', price_text)
        if current_match:
            current_price = f"₹{current_match.group(1)}"
        
        # Extract original price (usually strikethrough or crossed out)
        # TODO: Implement based on actual HTML structure
        
        # Calculate discount if both prices available
        if current_price and original_price:
            try:
                current_val = float(re.sub(r'[₹,]', '', current_price))
                original_val = float(re.sub(r'[₹,]', '', original_price))
                discount_pct = f"{((original_val - current_val) / original_val * 100):.1f}%"
            except (ValueError, ZeroDivisionError):
                pass
        
        return current_price, original_price, discount_pct
    
    def extract_unit_size(self, text: str) -> str:
        """Extract unit size information from product text"""
        if not text:
            return ""
        
        # Common patterns: 500 gm, 1 Kg, 720 gm, etc.
        size_patterns = [
            r'(\d+(?:\.\d+)?\s*(?:gm|kg|ml|ltr|pc|pack))',
            r'(\d+(?:\.\d+)?\s*(?:gram|kilogram|milliliter|liter|piece|pieces))',
            r'\((\d+(?:\.\d+)?\s*(?:gm|kg|ml|ltr|pc)/?\w*)\)'
        ]
        
        for pattern in size_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                return match.group(1).strip()
        
        return ""
    
    def get_category_links(self, soup: BeautifulSoup) -> List[tuple[str, str]]:
        """Extract all category and subcategory links from the main page"""
        category_links = []
        
        # TODO: Implement category link extraction based on actual HTML structure
        # Look for navigation menus, category grids, or sidebar links
        
        # Example patterns to look for:
        # - Links in navigation menu
        # - Category cards/tiles
        # - Sidebar category lists
        
        # Placeholder implementation - needs to be updated based on actual HTML
        category_elements = soup.find_all('a', href=re.compile(r'/(in/)?[\w-]+'))
        
        for link in category_elements:
            href = link.get('href', '')
            text = self.clean_text(link.get_text())
            
            if href and text and 'Menu-Addons' not in href:
                full_url = urljoin(self.base_url, href)
                category_links.append((text, full_url))
        
        # Remove duplicates
        category_links = list(set(category_links))
        
        logger.info(f"Found {len(category_links)} category links")
        return category_links
    
    def extract_product_from_listing(self, product_element, category: str = "") -> Optional[Product]:
        """Extract product information from a product listing element"""
        product = Product()
        product.scraped_timestamp = datetime.now().isoformat()
        product.category = category
        
        try:
            # TODO: Update selectors based on actual HTML structure
            
            # Product name
            name_elem = product_element.find(['h3', 'h4', 'a'], class_=re.compile(r'product|title|name'))
            if name_elem:
                product.product_name = self.clean_text(name_elem.get_text())
            
            # Product URL
            link_elem = product_element.find('a', href=True)
            if link_elem:
                product.product_page_url = urljoin(self.base_url, link_elem['href'])
            
            # Price information
            price_elem = product_element.find(['span', 'div'], class_=re.compile(r'price|cost|amount'))
            if price_elem:
                price_text = self.clean_text(price_elem.get_text())
                product.price_current, product.price_original, product.discount_percentage = self.extract_price_info(price_text)
            
            # Product image
            img_elem = product_element.find('img')
            if img_elem:
                img_src = img_elem.get('src') or img_elem.get('data-src')
                if img_src:
                    product.product_image_url = urljoin(self.base_url, img_src)
            
            # Unit size
            product.unit_size = self.extract_unit_size(product.product_name)
            
            # Availability status
            # TODO: Look for stock indicators, "Add to cart" buttons, etc.
            if product_element.find(text=re.compile(r'out of stock|unavailable', re.IGNORECASE)):
                product.availability_status = "Out of Stock"
            else:
                product.availability_status = "In Stock"
            
            # Tags (dietary badges, features)
            badges = product_element.find_all(['span', 'div'], class_=re.compile(r'badge|tag|dietary'))
            if badges:
                tags = [self.clean_text(badge.get_text()) for badge in badges if badge.get_text().strip()]
                product.tags = ";".join(tags)
            
            if product.product_name:  # Only return if we got at least a name
                return product
                
        except Exception as e:
            logger.error(f"Error extracting product: {str(e)}")
            
        return None
    
    def scrape_product_details(self, product: Product) -> Product:
        """Scrape detailed information from individual product page"""
        if not product.product_page_url or product.product_page_url in self.scraped_urls:
            return product
        
        soup = self.safe_request(product.product_page_url)
        if not soup:
            return product
        
        self.scraped_urls.add(product.product_page_url)
        
        try:
            # TODO: Update selectors based on actual product page HTML structure
            
            # Product description
            desc_elem = soup.find(['div', 'p'], class_=re.compile(r'description|detail|about'))
            if desc_elem:
                product.product_description = self.clean_text(desc_elem.get_text())
            
            # Ingredients
            ingredients_elem = soup.find(text=re.compile(r'ingredients?', re.IGNORECASE))
            if ingredients_elem:
                # Look for the next sibling or parent that contains ingredient info
                parent = ingredients_elem.parent
                if parent:
                    product.ingredients = self.clean_text(parent.get_text())
            
            # Nutritional information
            nutrition_elem = soup.find(text=re.compile(r'nutrition|nutritional', re.IGNORECASE))
            if nutrition_elem:
                parent = nutrition_elem.parent
                if parent:
                    product.nutritional_info = self.clean_text(parent.get_text())
            
            # Product ID/SKU
            sku_elem = soup.find(text=re.compile(r'sku|product id|item code', re.IGNORECASE))
            if sku_elem:
                # Extract ID from text or nearby elements
                sku_match = re.search(r'(?:sku|id)[:\s]*([a-zA-Z0-9\-_]+)', sku_elem.parent.get_text(), re.IGNORECASE)
                if sku_match:
                    product.sku_code = sku_match.group(1)
            
            # Rating and reviews
            rating_elem = soup.find(['span', 'div'], class_=re.compile(r'rating|star'))
            if rating_elem:
                rating_text = rating_elem.get_text()
                rating_match = re.search(r'(\d+(?:\.\d+)?)', rating_text)
                if rating_match:
                    product.rating = rating_match.group(1)
            
            review_elem = soup.find(['span', 'div'], class_=re.compile(r'review|count'))
            if review_elem:
                review_text = review_elem.get_text()
                review_match = re.search(r'(\d+)', review_text)
                if review_match:
                    product.review_count = review_match.group(1)
            
            # Packaging type
            packaging_keywords = ['frozen', 'fresh', 'chilled', 'ambient', 'dry']
            text_content = soup.get_text().lower()
            for keyword in packaging_keywords:
                if keyword in text_content:
                    product.packaging_type = keyword.title()
                    break
            
        except Exception as e:
            logger.error(f"Error scraping product details for {product.product_page_url}: {str(e)}")
        
        return product
    
    def scrape_category_page(self, category_name: str, category_url: str) -> List[Product]:
        """Scrape all products from a category page with pagination support"""
        products = []
        page_num = 1
        
        logger.info(f"Scraping category: {category_name} from {category_url}")
        
        while True:
            # Handle pagination - adjust URL structure based on actual implementation
            if page_num > 1:
                if '?' in category_url:
                    paginated_url = f"{category_url}&page={page_num}"
                else:
                    paginated_url = f"{category_url}?page={page_num}"
            else:
                paginated_url = category_url
            
            soup = self.safe_request(paginated_url)
            if not soup:
                break
            
            # TODO: Update product selectors based on actual HTML structure
            product_elements = soup.find_all(['div', 'article'], class_=re.compile(r'product|item|card'))
            
            if not product_elements:
                logger.info(f"No products found on page {page_num} for {category_name}")
                break
            
            page_products = []
            for elem in product_elements:
                product = self.extract_product_from_listing(elem, category_name)
                if product:
                    # Get detailed information from product page
                    detailed_product = self.scrape_product_details(product)
                    page_products.append(detailed_product)
                    
            products.extend(page_products)
            logger.info(f"Scraped {len(page_products)} products from {category_name} page {page_num}")
            
            # Check for next page
            next_page = soup.find('a', text=re.compile(r'next|more', re.IGNORECASE)) or \
                       soup.find('a', class_=re.compile(r'next|pagination'))
            
            if not next_page:
                break
                
            page_num += 1
            
            # Safety limit for pagination
            if page_num > 50:
                logger.warning(f"Reached pagination safety limit for {category_name}")
                break
        
        logger.info(f"Total products scraped from {category_name}: {len(products)}")
        return products
    
    def scrape_all_products(self) -> List[Product]:
        """Main method to scrape all products from all categories"""
        logger.info("Starting Hyperpure scraping process...")
        
        # Start from the main Menu Add-ons page
        main_url = f"{self.base_url}/in/Menu-Addons"
        soup = self.safe_request(main_url)
        
        if not soup:
            logger.error("Failed to fetch main page")
            return []
        
        # Get all category links
        category_links = self.get_category_links(soup)
        
        if not category_links:
            logger.warning("No category links found, trying to scrape main page products")
            # Try to scrape products directly from main page
            main_products = self.scrape_category_page("Menu Add-ons", main_url)
            self.products.extend(main_products)
        else:
            # Scrape each category
            for category_name, category_url in category_links:
                try:
                    category_products = self.scrape_category_page(category_name, category_url)
                    self.products.extend(category_products)
                    
                    logger.info(f"Progress: {len(self.products)} total products scraped so far")
                    
                except Exception as e:
                    logger.error(f"Error scraping category {category_name}: {str(e)}")
                    continue
        
        logger.info(f"Scraping completed. Total products: {len(self.products)}")
        return self.products
    
    def save_to_csv(self, filename: str = "hyperpure_products.csv"):
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
    """Main function to run the scraper"""
    scraper = HyperpureScraper()
    
    try:
        # Scrape all products
        products = scraper.scrape_all_products()
        
        if products:
            # Save to CSV
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"hyperpure_products_{timestamp}.csv"
            scraper.save_to_csv(filename)
            
            print(f"\nScraping completed successfully!")
            print(f"Total products scraped: {len(products)}")
            print(f"Data saved to: {filename}")
            
            # Print some statistics
            categories = set(product.category for product in products if product.category)
            print(f"Categories found: {len(categories)}")
            for category in sorted(categories):
                count = sum(1 for p in products if p.category == category)
                print(f"  - {category}: {count} products")
                
        else:
            print("No products were scraped. Please check the logs for errors.")
            
    except KeyboardInterrupt:
        logger.info("Scraping interrupted by user")
        print("\nScraping interrupted. Saving partial data...")
        if scraper.products:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"hyperpure_products_partial_{timestamp}.csv"
            scraper.save_to_csv(filename)
            print(f"Partial data saved to: {filename}")
            
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        print(f"An error occurred: {str(e)}")


if __name__ == "__main__":
    main()
