#!/usr/bin/env python3
"""
Enhanced Detailed Hyperpure.com Product Scraper
=============================================

A comprehensive web scraper that extracts DETAILED product specifications
including cooking instructions, thawing instructions, meat content, etc.

Requirements:
- requests==2.31.0
- beautifulsoup4==4.12.2
- lxml==4.9.3
- pandas==2.0.3
- selenium==4.15.0 (optional)
- webdriver-manager==4.0.1 (optional)

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
import argparse

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('hyperpure_detailed_scraper.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)


@dataclass
class DetailedProduct:
    """Data class for detailed product information"""
    # Basic product info
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
    
    # Detailed specifications
    no_of_pieces: str = ""
    fillet_size: str = ""
    meat_content: str = ""
    weight_variation: str = ""
    shelf_life: str = ""
    storage_instructions: str = ""
    thawing_instructions: str = ""
    cooking_instructions: str = ""
    serving_suggestions: str = ""
    
    # Product highlights and features
    key_features: str = ""
    product_highlights: str = ""
    premium_ingredients: str = ""
    health_conscious_info: str = ""
    
    # Additional details
    nutritional_info: str = ""
    ingredients: str = ""
    allergen_info: str = ""
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
            'no_of_pieces': self.no_of_pieces,
            'fillet_size': self.fillet_size,
            'meat_content': self.meat_content,
            'weight_variation': self.weight_variation,
            'shelf_life': self.shelf_life,
            'storage_instructions': self.storage_instructions,
            'thawing_instructions': self.thawing_instructions,
            'cooking_instructions': self.cooking_instructions,
            'serving_suggestions': self.serving_suggestions,
            'key_features': self.key_features,
            'product_highlights': self.product_highlights,
            'premium_ingredients': self.premium_ingredients,
            'health_conscious_info': self.health_conscious_info,
            'nutritional_info': self.nutritional_info,
            'ingredients': self.ingredients,
            'allergen_info': self.allergen_info,
            'product_id': self.product_id,
            'sku_code': self.sku_code,
            'rating': self.rating,
            'review_count': self.review_count,
            'tags': self.tags,
            'scraped_timestamp': self.scraped_timestamp
        }


class HyperpureDetailedScraper:
    """Detailed scraper for comprehensive product information"""
    
    def __init__(self):
        self.base_url = "https://www.hyperpure.com"
        self.session = requests.Session()
        self.setup_session()
        self.scraped_urls: Set[str] = set()
        self.products: List[DetailedProduct] = []
        
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
    
    def extract_price_info(self, element) -> tuple[str, str, str]:
        """Extract current price, original price, and discount percentage"""
        current_price = ""
        original_price = ""
        discount_pct = ""
        
        if not element:
            return current_price, original_price, discount_pct
        
        price_text = self.clean_text(element.get_text())
        
        # Extract current price
        current_matches = re.findall(r'₹(\d+(?:,\d+)*(?:\.\d+)?)', price_text)
        if current_matches:
            current_price = f"₹{current_matches[0]}"
        
        # Look for strikethrough prices
        strikethrough_elem = element.find(['s', 'del', 'strike']) or \
                           element.find(attrs={'style': re.compile(r'text-decoration:\s*line-through', re.I)})
        
        if strikethrough_elem:
            original_text = strikethrough_elem.get_text()
            original_match = re.search(r'₹(\d+(?:,\d+)*(?:\.\d+)?)', original_text)
            if original_match:
                original_price = f"₹{original_match.group(1)}"
        
        # Calculate discount
        if current_price and original_price:
            try:
                current_val = float(re.sub(r'[₹,]', '', current_price))
                original_val = float(re.sub(r'[₹,]', '', original_price))
                if original_val > current_val:
                    discount_pct = f"{((original_val - current_val) / original_val * 100):.1f}%"
            except (ValueError, ZeroDivisionError):
                pass
        
        return current_price, original_price, discount_pct
    
    def extract_detailed_specifications(self, soup: BeautifulSoup, full_text: str) -> Dict[str, str]:
        """Extract detailed product specifications from the page"""
        specs = {}
        
        # Number of pieces
        pieces_patterns = [
            r'(\d+-\d+)\s*(?:pcs?|pieces?)/pack',
            r'(\d+)\s*(?:pc|pcs|pieces?)\s*per pack',
            r'Pack of (\d+)',
            r'(\d+)\s*(?:pc|pcs)',
        ]
        
        for pattern in pieces_patterns:
            match = re.search(pattern, full_text, re.IGNORECASE)
            if match:
                specs['no_of_pieces'] = match.group(1)
                break
        
        # Fillet/piece size
        size_patterns = [
            r'Fillet Size:\s*([^\\n]+)',
            r'(\d+-\d+g)\s*each',
            r'(\d+\s*gm?/pc)',
            r'(\d+\s*gm?)\s*per piece',
        ]
        
        for pattern in size_patterns:
            match = re.search(pattern, full_text, re.IGNORECASE)
            if match:
                specs['fillet_size'] = self.clean_text(match.group(1))
                break
        
        # Meat content
        meat_patterns = [
            r'Meat Content:\s*([^\\n]+)',
            r'Contains (\d+%\s*(?:chicken|meat|fish)[^\\n]*)',
            r'(\d+%\s*(?:chicken|meat|fish))',
        ]
        
        for pattern in meat_patterns:
            match = re.search(pattern, full_text, re.IGNORECASE)
            if match:
                specs['meat_content'] = self.clean_text(match.group(1))
                break
        
        # Weight variation
        weight_patterns = [
            r'Weight Variation[^:]*:\s*([^\\n]+)',
            r'(±\d+g)',
        ]
        
        for pattern in weight_patterns:
            match = re.search(pattern, full_text, re.IGNORECASE)
            if match:
                specs['weight_variation'] = self.clean_text(match.group(1))
                break
        
        # Shelf life
        shelf_patterns = [
            r'Shelf Life:\s*([^\\n]+)',
            r'Lasts up to (\d+\s*days?[^\\n]*)',
            r'(\d+\s*days? from manufacturing)',
        ]
        
        for pattern in shelf_patterns:
            match = re.search(pattern, full_text, re.IGNORECASE)
            if match:
                specs['shelf_life'] = self.clean_text(match.group(1))
                break
        
        # Storage instructions
        storage_patterns = [
            r'Storage[^:]*:\s*([^\\n]+(?:\\n[^\\n]+)*?)(?=\\n\\n|Thawing|Cooking)',
            r'Store at ([^\\n]+)',
            r'Keep frozen at ([^\\n]+)',
        ]
        
        for pattern in storage_patterns:
            match = re.search(pattern, full_text, re.IGNORECASE | re.DOTALL)
            if match:
                specs['storage_instructions'] = self.clean_text(match.group(1))
                break
        
        # Thawing instructions
        thawing_section = re.search(r'Thawing Instructions?:(.+?)(?=Important:|Cooking|$)', full_text, re.IGNORECASE | re.DOTALL)
        if thawing_section:
            specs['thawing_instructions'] = self.clean_text(thawing_section.group(1))
        
        # Cooking instructions
        cooking_patterns = [
            r'Cooking Instructions?:(.+?)(?=Shelf Life|Storage|$)',
            r'From Freezer to Fryer:(.+?)(?=Safety|$)',
            r'Deep fry at ([^\\n]+)',
        ]
        
        for pattern in cooking_patterns:
            match = re.search(pattern, full_text, re.IGNORECASE | re.DOTALL)
            if match:
                specs['cooking_instructions'] = self.clean_text(match.group(1))
                break
        
        # Serving suggestions
        serving_section = re.search(r'Serving Suggestions?:(.+?)(?=Pack Size|Similar|$)', full_text, re.IGNORECASE | re.DOTALL)
        if serving_section:
            specs['serving_suggestions'] = self.clean_text(serving_section.group(1))
        
        # Key features
        features_section = re.search(r'Key Features?:(.+?)(?=Serving|Cooking|Pack Size|$)', full_text, re.IGNORECASE | re.DOTALL)
        if features_section:
            specs['key_features'] = self.clean_text(features_section.group(1))
        
        # Product highlights
        highlights_section = re.search(r'Product Highlights?:(.+?)(?=Key Features|Cooking|$)', full_text, re.IGNORECASE | re.DOTALL)
        if highlights_section:
            specs['product_highlights'] = self.clean_text(highlights_section.group(1))
        
        # Premium ingredients
        ingredients_patterns = [
            r'Premium Ingredients?:([^\\n]+)',
            r'Made with ([^\\n]+high-quality[^\\n]+)',
        ]
        
        for pattern in ingredients_patterns:
            match = re.search(pattern, full_text, re.IGNORECASE)
            if match:
                specs['premium_ingredients'] = self.clean_text(match.group(1))
                break
        
        # Health conscious info
        health_patterns = [
            r'Health-?Conscious:([^\\n]+)',
            r'Contains no ([^\\n]+)',
            r'Free from ([^\\n]+)',
        ]
        
        for pattern in health_patterns:
            match = re.search(pattern, full_text, re.IGNORECASE)
            if match:
                specs['health_conscious_info'] = self.clean_text(match.group(1))
                break
        
        return specs
    
    def extract_product_from_listing(self, product_element, category: str = "") -> Optional[DetailedProduct]:
        """Extract basic product information from listing page"""
        product = DetailedProduct()
        product.scraped_timestamp = datetime.now().isoformat()
        product.category = category
        
        try:
            # Product name
            name_selectors = ['h3', 'h4', 'h2', '[class*="title"]', '[class*="name"]', 'a[title]']
            for selector in name_selectors:
                name_elem = product_element.select_one(selector)
                if name_elem:
                    text = name_elem.get('title') or self.clean_text(name_elem.get_text())
                    if text and len(text.strip()) > 3:
                        product.product_name = text
                        break
            
            # Product URL
            link_elem = product_element.find('a', href=True)
            if link_elem:
                product.product_page_url = urljoin(self.base_url, link_elem['href'])
            
            # Price information
            price_selectors = ['[class*="price"]', '[class*="cost"]', '[class*="amount"]']
            for selector in price_selectors:
                price_elem = product_element.select_one(selector)
                if price_elem:
                    product.price_current, product.price_original, product.discount_percentage = self.extract_price_info(price_elem)
                    if product.price_current:
                        break
            
            # If no price found, search in text
            if not product.price_current:
                element_text = product_element.get_text()
                price_match = re.search(r'₹(\d+(?:,\d+)*(?:\.\d+)?)', element_text)
                if price_match:
                    product.price_current = f"₹{price_match.group(1)}"
            
            # Product image
            img_elem = product_element.find('img')
            if img_elem:
                img_src = img_elem.get('src') or img_elem.get('data-src')
                if img_src:
                    product.product_image_url = urljoin(self.base_url, img_src)
            
            # Basic unit size from name
            product.unit_size = self.extract_unit_size(product.product_name)
            
            # Availability status
            element_text = product_element.get_text().lower()
            if any(indicator in element_text for indicator in ['out of stock', 'unavailable']):
                product.availability_status = "Out of Stock"
            else:
                product.availability_status = "In Stock"
            
            # Tags from badges
            badge_selectors = ['[class*="badge"]', '[class*="tag"]', 'img[alt*="dietary"]']
            tags = []
            for selector in badge_selectors:
                badges = product_element.select(selector)
                for badge in badges:
                    if badge.name == 'img':
                        tag_text = badge.get('alt', '')
                    else:
                        tag_text = self.clean_text(badge.get_text())
                    
                    if tag_text and tag_text not in tags:
                        tags.append(tag_text)
            
            if tags:
                product.tags = ";".join(tags)
            
            return product if product.product_name else None
                
        except Exception as e:
            logger.error(f"Error extracting product: {str(e)}")
            return None
    
    def extract_unit_size(self, text: str) -> str:
        """Extract unit size from text"""
        if not text:
            return ""
        
        patterns = [
            r'(\d+(?:\.\d+)?\s*(?:gm|kg|ml|ltr|pc|pcs|pack))',
            r'\((\d+(?:\.\d+)?\s*(?:gm|kg|ml|ltr|pc)/?\w*)\)'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                return match.group(1).strip()
        
        return ""
    
    def scrape_detailed_product_info(self, product: DetailedProduct) -> DetailedProduct:
        """Scrape detailed information from individual product page"""
        if not product.product_page_url or product.product_page_url in self.scraped_urls:
            return product
        
        soup = self.safe_request(product.product_page_url)
        if not soup:
            return product
        
        self.scraped_urls.add(product.product_page_url)
        logger.info(f"Extracting detailed info for: {product.product_name}")
        
        try:
            full_text = soup.get_text()
            
            # Extract product name from H1 tag first
            h1_tag = soup.find('h1')
            if h1_tag:
                product.product_name = self.clean_text(h1_tag.get_text())
            
            # If no H1, try title tag
            if not product.product_name:
                title_tag = soup.find('title')
                if title_tag:
                    title_text = title_tag.get_text()
                    # Clean up title (remove "Wholesalers with best prices..." part)
                    title_clean = re.sub(r'\s+Wholesalers.*$', '', title_text)
                    product.product_name = self.clean_text(title_clean)
            
            # Extract main product description
            desc_patterns = [
                r'Product details\s*(.+?)(?=Product Highlights|Key Features|Similar items)',
                r'<h1[^>]*>.*?</h1>\s*(.+?)(?=Product Highlights|Key Features|Similar)',
            ]
            
            for pattern in desc_patterns:
                match = re.search(pattern, str(soup), re.IGNORECASE | re.DOTALL)
                if match:
                    desc_soup = BeautifulSoup(match.group(1), 'lxml')
                    desc_text = self.clean_text(desc_soup.get_text())
                    if len(desc_text) > 50:
                        product.product_description = desc_text[:500]  # Limit length
                        break
            
            # Extract all detailed specifications
            specs = self.extract_detailed_specifications(soup, full_text)
            
            # Update product with detailed specs
            for key, value in specs.items():
                if hasattr(product, key) and value:
                    setattr(product, key, value)
            
            # Extract packaging type
            packaging_keywords = {
                'frozen': 'Frozen',
                'fresh': 'Fresh',
                'chilled': 'Chilled',
                'ambient': 'Ambient'
            }
            
            lower_text = full_text.lower()
            for keyword, packaging_type in packaging_keywords.items():
                if keyword in lower_text:
                    product.packaging_type = packaging_type
                    break
            
            # Extract SKU from URL
            url_path = urlparse(product.product_page_url).path
            sku_match = re.search(r'/([a-zA-Z0-9\-_]+)(?:\?|$)', url_path)
            if sku_match:
                product.sku_code = sku_match.group(1)
            
            # Update unit size if better info found
            if not product.unit_size:
                product.unit_size = self.extract_unit_size(full_text)
            
        except Exception as e:
            logger.error(f"Error scraping detailed info for {product.product_page_url}: {str(e)}")
        
        return product
    
    def get_product_links_from_main_page(self) -> List[str]:
        """Get all product links from the main Menu Add-ons page"""
        main_url = f"{self.base_url}/in/Menu-Addons"
        soup = self.safe_request(main_url)
        
        if not soup:
            logger.error("Failed to fetch main page")
            return []
        
        product_links = []
        
        # Find all product links
        links = soup.find_all('a', href=True)
        for link in links:
            href = link.get('href', '')
            if '/in/' in href and any(keyword in href for keyword in ['frozen', 'brownie', 'chicken', 'burger', 'chutney']):
                full_url = urljoin(self.base_url, href)
                if full_url not in product_links:
                    product_links.append(full_url)
        
        logger.info(f"Found {len(product_links)} product links")
        return product_links
    
    def scrape_all_detailed_products(self) -> List[DetailedProduct]:
        """Main method to scrape all products with detailed information"""
        logger.info("Starting detailed Hyperpure scraping process...")
        
        # Get all product links
        product_links = self.get_product_links_from_main_page()
        
        if not product_links:
            logger.error("No product links found")
            return []
        
        for i, product_url in enumerate(product_links):
            try:
                logger.info(f"Processing product {i+1}/{len(product_links)}: {product_url}")
                
                # Create basic product from URL
                product = DetailedProduct()
                product.product_page_url = product_url
                product.scraped_timestamp = datetime.now().isoformat()
                
                # Extract detailed information
                detailed_product = self.scrape_detailed_product_info(product)
                
                if detailed_product.product_name:
                    self.products.append(detailed_product)
                    logger.info(f"Successfully scraped: {detailed_product.product_name}")
                else:
                    logger.warning(f"Failed to extract product name from {product_url}")
                
                # Progress update
                if (i + 1) % 5 == 0:
                    logger.info(f"Progress: {i+1}/{len(product_links)} products processed")
                
            except Exception as e:
                logger.error(f"Error processing {product_url}: {str(e)}")
                continue
        
        logger.info(f"Detailed scraping completed. Total products: {len(self.products)}")
        return self.products
    
    def save_to_csv(self, filename: str = "hyperpure_detailed_products.csv"):
        """Save scraped products to CSV file with all detailed fields"""
        if not self.products:
            logger.error("No products to save")
            return
        
        fieldnames = [
            'product_name', 'category', 'subcategory', 'price_current', 'price_original',
            'discount_percentage', 'product_description', 'product_image_url', 'product_page_url',
            'availability_status', 'brand_name', 'unit_size', 'packaging_type',
            'no_of_pieces', 'fillet_size', 'meat_content', 'weight_variation', 'shelf_life',
            'storage_instructions', 'thawing_instructions', 'cooking_instructions', 'serving_suggestions',
            'key_features', 'product_highlights', 'premium_ingredients', 'health_conscious_info',
            'nutritional_info', 'ingredients', 'allergen_info', 'product_id', 'sku_code',
            'rating', 'review_count', 'tags', 'scraped_timestamp'
        ]
        
        try:
            with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                writer.writeheader()
                
                for product in self.products:
                    writer.writerow(product.to_dict())
            
            logger.info(f"Successfully saved {len(self.products)} detailed products to {filename}")
            
        except Exception as e:
            logger.error(f"Error saving to CSV: {str(e)}")


def main():
    """Main function to run the detailed scraper"""
    parser = argparse.ArgumentParser(description='Hyperpure.com Detailed Product Scraper')
    parser.add_argument('--output', default='hyperpure_detailed_products.csv', help='Output CSV filename')
    parser.add_argument('--limit', type=int, help='Limit number of products to scrape (for testing)')
    args = parser.parse_args()
    
    scraper = HyperpureDetailedScraper()
    
    try:
        # Scrape all products with detailed information
        products = scraper.scrape_all_detailed_products()
        
        # Apply limit if specified
        if args.limit and len(products) > args.limit:
            products = products[:args.limit]
            logger.info(f"Limited output to {args.limit} products")
        
        if products:
            # Save to CSV
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"hyperpure_detailed_{timestamp}.csv"
            if args.output != 'hyperpure_detailed_products.csv':
                filename = args.output
            
            scraper.save_to_csv(filename)
            
            print(f"\nDetailed scraping completed successfully!")
            print(f"Total products scraped: {len(products)}")
            print(f"Data saved to: {filename}")
            
            # Show sample of detailed fields extracted
            if products:
                sample = products[0]
                print(f"\nSample detailed fields for '{sample.product_name}':")
                print(f"  - No. of pieces: {sample.no_of_pieces}")
                print(f"  - Meat content: {sample.meat_content}")
                print(f"  - Shelf life: {sample.shelf_life}")
                print(f"  - Storage: {sample.storage_instructions[:50]}...")
                print(f"  - Cooking instructions: {sample.cooking_instructions[:50]}...")
                
        else:
            print("No products were scraped. Please check the logs for errors.")
            
    except KeyboardInterrupt:
        logger.info("Scraping interrupted by user")
        print("\nScraping interrupted. Saving partial data...")
        if scraper.products:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"hyperpure_detailed_partial_{timestamp}.csv"
            scraper.save_to_csv(filename)
            print(f"Partial data saved to: {filename}")
            
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        print(f"An error occurred: {str(e)}")


if __name__ == "__main__":
    main()
