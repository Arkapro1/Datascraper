#!/usr/bin/env python3
"""
Hyperpure.com Comprehensive Product Scraper
==========================================

A comprehensive scraper that explores multiple product categories to get
the maximum number of products from Hyperpure.com.

Requirements: requests, beautifulsoup4, lxml

Author: AI Assistant
Date: 2025-09-03
"""

import requests
from bs4 import BeautifulSoup
import csv
import time
import logging
import re
from urllib.parse import urljoin, urlparse, parse_qs
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
        logging.FileHandler('hyperpure_comprehensive_scraper.log'),
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


class HyperpureComprehensiveScraper:
    """Comprehensive scraper for Hyperpure.com to get maximum products"""
    
    def __init__(self):
        self.base_url = "https://www.hyperpure.com"
        self.session = requests.Session()
        self.setup_session()
        self.scraped_urls: Set[str] = set()
        self.products: List[Product] = []
        
        # Known category URLs to explore
        self.category_urls = [
            "/in/Menu-Addons",
            "/in/brownies-cakes-and-lava",
            "/in/chicken-breast-boneless",
            "/in/cheese",
            "/in/curd",
            "/in/ghee",
            "/in/milk-milk-powder",
            "/in/butter",
            "/in/paneer",
            "/in/cream",
            "/in/eggs",
            "/in/tomato-onion-potato",
            "/in/edible-oils",
            "/in/salts-sugars",
            "/in/pasta-noodles",
            "/in/rice-rice-products",
            "/in/atta-maida-sooji",
            "/in/corn-flour-besan-others",
            "/in/urad-rajma-other-dal_1",
            "/in/cashews1",
            "/in/tea-and-coffee",
            "/in/ketchup-puree-pastes"
        ]
        
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
    
    def get_category_name_from_url(self, url: str) -> str:
        """Extract a readable category name from URL"""
        path = urlparse(url).path
        name = path.split('/')[-1]
        
        # Convert URL slug to readable name
        category_map = {
            "Menu-Addons": "Menu Add-ons",
            "brownies-cakes-and-lava": "Brownies, Cakes and Lava",
            "chicken-breast-boneless": "Chicken",
            "cheese": "Cheese",
            "curd": "Curd/Yogurt",
            "ghee": "Ghee",
            "milk-milk-powder": "Milk & Milk Powder",
            "butter": "Butter",
            "paneer": "Paneer",
            "cream": "Cream",
            "eggs": "Eggs",
            "tomato-onion-potato": "Tomato, Onion, Potato",
            "edible-oils": "Edible Oils",
            "salts-sugars": "Salt & Sugar",
            "pasta-noodles": "Pasta & Noodles",
            "rice-rice-products": "Rice & Rice Products",
            "atta-maida-sooji": "Atta, Maida, Sooji",
            "corn-flour-besan-others": "Corn Flour, Besan & Others",
            "urad-rajma-other-dal_1": "Urad, Rajma & Other Dal",
            "cashews1": "Cashews & Dry Fruits",
            "tea-and-coffee": "Tea & Coffee",
            "ketchup-puree-pastes": "Ketchup, Puree & Pastes"
        }
        
        return category_map.get(name, name.replace('-', ' ').title())
    
    def extract_products_from_page(self, soup: BeautifulSoup, category_url: str) -> List[Product]:
        """Extract products from a category page"""
        products = []
        category_name = self.get_category_name_from_url(category_url)
        
        # Find all product links that match the pattern
        product_links = []
        
        # Look for links that contain product patterns
        for link in soup.find_all('a', href=True):
            href = link['href']
            if (href.startswith('/in/') and 
                len(href.split('/')) >= 3 and  # At least /in/product-name
                not any(skip in href for skip in ['Menu-Addons', 'categories', 'search', 'cart', 'login', 'register']) and
                href != category_url):  # Don't include the category URL itself
                
                full_url = urljoin(self.base_url, href)
                product_name = self.clean_text(link.get_text())
                
                # Filter for meaningful product names
                if (product_name and 
                    len(product_name) > 5 and 
                    not any(skip in product_name.lower() for skip in ['home', 'login', 'cart', 'search', 'categories', 'how it works', 'products', 'faqs']) and
                    any(char.isalpha() for char in product_name)):  # Must contain letters
                    
                    product_links.append((product_name, full_url))
        
        # Remove duplicates
        product_links = list(set(product_links))
        
        logger.info(f"Found {len(product_links)} potential products in {category_name}")
        
        # Extract basic info for each product
        for product_name, product_url in product_links:
            product = Product()
            product.scraped_timestamp = datetime.now().isoformat()
            product.category = category_name
            product.product_name = product_name
            product.product_page_url = product_url
            product.unit_size = self.extract_unit_size(product_name)
            
            # Extract price from the current page if visible
            page_text = soup.get_text()
            if product_name in page_text:
                # Look for prices near the product name
                name_index = page_text.find(product_name)
                if name_index != -1:
                    surrounding_text = page_text[max(0, name_index-100):name_index+200]
                    product.price_current, product.price_original, product.discount_percentage = self.extract_price_info(surrounding_text)
            
            # Determine packaging type from product name or category
            if any(keyword in product_name.lower() for keyword in ['frozen', 'freeze']):
                product.packaging_type = "Frozen"
            elif any(keyword in product_name.lower() for keyword in ['fresh', 'dairy']):
                product.packaging_type = "Fresh"
            elif category_name in ['Milk & Milk Powder', 'Cheese', 'Butter', 'Paneer', 'Cream', 'Curd/Yogurt']:
                product.packaging_type = "Chilled"
            elif category_name in ['Rice & Rice Products', 'Atta, Maida, Sooji', 'Salt & Sugar']:
                product.packaging_type = "Dry"
            
            # Set availability (assume in stock if we can see it)
            product.availability_status = "In Stock"
            
            products.append(product)
            
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
                    title_text = title.get_text()
                    product.product_name = self.clean_text(title_text.split('|')[0].split(' Wholesalers')[0])
            
            # Look for h1 tag which often contains the product name
            h1_tag = soup.find('h1')
            if h1_tag and len(h1_tag.get_text().strip()) > len(product.product_name):
                product.product_name = self.clean_text(h1_tag.get_text())
            
            # Extract description from page content
            page_text = soup.get_text()
            
            # Look for product description patterns
            desc_patterns = [
                r'[A-Z][^.]*(?:premium|quality|ingredients|flavor|taste|rich|delicious|fresh|organic|natural)[^.]*[.!]',
                r'[A-Z][^.]*(?:made with|crafted|indulge|experience|enjoy)[^.]*[.!]',
                r'Key Features:[^.]*[.!]',
                r'Product details[^.]*[.!]'
            ]
            
            for pattern in desc_patterns:
                matches = re.findall(pattern, page_text, re.IGNORECASE | re.DOTALL)
                if matches:
                    # Get the longest meaningful description
                    best_desc = max(matches, key=len)
                    if len(best_desc) > 30 and len(best_desc) < 500:
                        product.product_description = self.clean_text(best_desc)
                        break
            
            # Extract price information from page if not already found
            if not product.price_current:
                product.price_current, product.price_original, product.discount_percentage = self.extract_price_info(page_text)
            
            # Look for images
            images = soup.find_all('img')
            for img in images:
                src = img.get('src') or img.get('data-src')
                if src and ('assets.hyperpure.com' in src or 'hyperpure.com' in src) and any(ext in src for ext in ['.jpg', '.jpeg', '.png', '.webp']):
                    product.product_image_url = urljoin(self.base_url, src)
                    break
            
            # Extract ingredients if mentioned
            ingredients_patterns = [
                r'ingredients?[:\s]+(.*?)(?:\n|\.|\||$)',
                r'contains?[:\s]+(.*?)(?:\n|\.|\||$)',
                r'made with[:\s]+(.*?)(?:\n|\.|\||$)'
            ]
            
            for pattern in ingredients_patterns:
                match = re.search(pattern, page_text, re.IGNORECASE)
                if match:
                    ingredient_text = self.clean_text(match.group(1))
                    if len(ingredient_text) > 10 and len(ingredient_text) < 200:
                        product.ingredients = ingredient_text
                        break
            
            # Extract features/tags
            feature_keywords = ['premium', 'imported', 'handcrafted', 'frozen', 'fresh', 'organic', 'natural', 'quality']
            tags = []
            page_lower = page_text.lower()
            for keyword in feature_keywords:
                if keyword in page_lower:
                    tags.append(keyword.title())
            
            if tags:
                product.tags = ";".join(list(set(tags)))  # Remove duplicates
            
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
        """Main method to scrape all products from multiple categories"""
        logger.info("Starting comprehensive Hyperpure scraping process...")
        
        all_products = []
        
        # Scrape each category
        for category_url in self.category_urls:
            try:
                full_url = urljoin(self.base_url, category_url)
                logger.info(f"Processing category: {full_url}")
                
                soup = self.safe_request(full_url)
                if not soup:
                    continue
                
                # Extract products from this category page
                category_products = self.extract_products_from_page(soup, category_url)
                
                # Get detailed information for a sample of products (to avoid overloading)
                max_details = min(5, len(category_products))  # Limit to 5 products per category for demo
                
                for i, product in enumerate(category_products[:max_details]):
                    logger.info(f"Getting details for product {i+1}/{max_details} in category: {product.product_name[:50]}...")
                    detailed_product = self.scrape_product_details(product)
                    all_products.append(detailed_product)
                    
                    # Add delay between detail requests
                    time.sleep(random.uniform(1, 2))
                
                # Add remaining products without detailed scraping (to include in dataset)
                for product in category_products[max_details:]:
                    all_products.append(product)
                
                logger.info(f"Category {self.get_category_name_from_url(category_url)}: {len(category_products)} products found")
                
            except Exception as e:
                logger.error(f"Error processing category {category_url}: {str(e)}")
                continue
        
        self.products = all_products
        logger.info(f"Comprehensive scraping completed. Total products: {len(self.products)}")
        return self.products
    
    def save_to_csv(self, filename: str = "hyperpure_products_comprehensive.csv"):
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
    """Main function to run the comprehensive scraper"""
    scraper = HyperpureComprehensiveScraper()
    
    try:
        # Scrape all products
        products = scraper.scrape_all_products()
        
        if products:
            # Save to CSV
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"hyperpure_products_comprehensive_{timestamp}.csv"
            scraper.save_to_csv(filename)
            
            print(f"\nComprehensive scraping completed successfully!")
            print(f"Total products scraped: {len(products)}")
            print(f"Data saved to: {filename}")
            
            # Print statistics
            categories = {}
            for product in products:
                cat = product.category
                categories[cat] = categories.get(cat, 0) + 1
            
            print(f"\nProducts by category:")
            for category, count in sorted(categories.items()):
                print(f"  - {category}: {count} products")
            
            # Print sample products
            print(f"\nSample products scraped:")
            for i, product in enumerate(products[:10]):
                print(f"{i+1}. {product.product_name[:60]} - {product.price_current}")
                
        else:
            print("No products were scraped. Please check the logs for errors.")
            
    except KeyboardInterrupt:
        logger.info("Scraping interrupted by user")
        print("\nScraping interrupted. Saving partial data...")
        if scraper.products:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"hyperpure_products_comprehensive_partial_{timestamp}.csv"
            scraper.save_to_csv(filename)
            print(f"Partial data saved to: {filename}")
            
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        print(f"An error occurred: {str(e)}")


if __name__ == "__main__":
    main()
