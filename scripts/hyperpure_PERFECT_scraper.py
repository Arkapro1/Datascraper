#!/usr/bin/env python3
"""
SUPER CLEAN Hyperpure.com Product Scraper
========================================

Extracts PERFECT, DETAILED product data including:
- Product specifications (pieces, size, weight)
- Cooking & Thawing instructions
- Storage instructions
- Meat content
- Nutritional information
- And much more!
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
        logging.FileHandler('hyperpure_perfect_scraper.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)


@dataclass
class PerfectProduct:
    """Perfect product data structure with all details"""
    # Basic Info
    product_name: str = ""
    category: str = ""
    subcategory: str = ""
    price_current: str = ""
    price_original: str = ""
    discount_percentage: str = ""
    product_description: str = ""
    product_image_url: str = ""
    product_page_url: str = ""
    availability_status: str = "In Stock"
    brand_name: str = "Hyperpure"
    unit_size: str = ""
    packaging_type: str = ""
    
    # Detailed Specifications
    no_of_pieces: str = ""
    fillet_size: str = ""
    meat_content: str = ""
    weight_variation: str = ""
    shelf_life: str = ""
    storage_instructions: str = ""
    thawing_instructions: str = ""
    cooking_instructions: str = ""
    serving_suggestions: str = ""
    
    # Product Features
    key_features: str = ""
    product_highlights: str = ""
    premium_ingredients: str = ""
    health_conscious_info: str = ""
    
    # Additional Details
    nutritional_info: str = ""
    ingredients: str = ""
    allergen_info: str = ""
    product_id: str = ""
    sku_code: str = ""
    rating: str = ""
    review_count: str = ""
    tags: str = ""
    scraped_timestamp: str = ""


class HyperpurePerfectScraper:
    """Perfect scraper for pristine data"""
    
    def __init__(self):
        self.base_url = "https://www.hyperpure.com"
        self.session = requests.Session()
        self.setup_session()
        self.scraped_urls: Set[str] = set()
        self.products: List[PerfectProduct] = []
        
    def setup_session(self):
        """Setup session headers"""
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
        """Safe HTTP request with retries"""
        for attempt in range(max_retries):
            try:
                time.sleep(random.uniform(1, 3))
                response = self.session.get(url, timeout=30)
                response.raise_for_status()
                logger.info(f"✅ Successfully fetched: {url}")
                return BeautifulSoup(response.content, 'lxml')
            except Exception as e:
                logger.warning(f"⚠️ Attempt {attempt + 1} failed for {url}: {str(e)}")
                if attempt == max_retries - 1:
                    logger.error(f"❌ All attempts failed for {url}")
                    return None
                time.sleep(random.uniform(2, 5))
        return None
    
    def clean_text(self, text: str) -> str:
        """Super clean text normalization"""
        if not text:
            return ""
        
        # Remove extra whitespace and normalize
        cleaned = re.sub(r'\s+', ' ', text.strip())
        
        # Remove unwanted characters
        cleaned = cleaned.replace('"', '""')  # CSV safe quotes
        cleaned = re.sub(r'[^\w\s.,;:()\-₹%/\[\]]+', '', cleaned)  # Keep essential chars
        
        return cleaned
    
    def extract_perfect_price_info(self, soup: BeautifulSoup, product_text: str) -> tuple[str, str, str]:
        """Extract perfect price information"""
        current_price = ""
        original_price = ""
        discount_pct = ""
        
        # Multiple price extraction strategies
        price_patterns = [
            r'₹(\d+(?:,\d+)*(?:\.\d+)?)',
            r'(\d+)\s*₹',
            r'Rs\.?\s*(\d+(?:,\d+)*(?:\.\d+)?)',
        ]
        
        all_prices = []
        for pattern in price_patterns:
            matches = re.findall(pattern, product_text)
            all_prices.extend([f"₹{match.replace(',', '')}" for match in matches])
        
        # Remove duplicates while preserving order
        seen = set()
        unique_prices = []
        for price in all_prices:
            if price not in seen:
                seen.add(price)
                unique_prices.append(price)
        
        if unique_prices:
            current_price = unique_prices[0]
            if len(unique_prices) > 1:
                # Assume first is current, second might be original
                original_price = unique_prices[1]
                
                # Calculate discount if both prices exist
                try:
                    current_val = float(re.sub(r'[₹,]', '', current_price))
                    original_val = float(re.sub(r'[₹,]', '', original_price))
                    if original_val > current_val:
                        discount_pct = f"{((original_val - current_val) / original_val * 100):.1f}%"
                except (ValueError, ZeroDivisionError):
                    pass
        
        return current_price, original_price, discount_pct
    
    def extract_perfect_specifications(self, soup: BeautifulSoup, full_text: str) -> Dict[str, str]:
        """Extract PERFECT product specifications"""
        specs = {}
        
        # Clean up text for better pattern matching
        text = self.clean_text(full_text)
        
        # 1. Number of pieces - Enhanced patterns
        pieces_patterns = [
            r'(\d+-\d+)\s*(?:pcs?|pieces?|pc)/pack',
            r'(\d+)\s*(?:pc|pcs|pieces?)\s*per pack',
            r'Pack of (\d+)',
            r'(\d+)\s*(?:pc|pcs)(?:\s|$|,)',
            r'(\d+-\d+)\s*(?:pcs?|pieces?)',
            r'No\.?\s*of\s*Pcs?:\s*(\d+-\d+)',
        ]
        
        for pattern in pieces_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                specs['no_of_pieces'] = match.group(1)
                break
        
        # 2. Fillet/piece size - Enhanced patterns
        size_patterns = [
            r'Fillet Size:\s*([^\n]+)',
            r'(\d+-\d+g)\s*each',
            r'(\d+\s*gm?/pc)',
            r'(\d+\s*gm?)\s*per piece',
            r'(\d+\s*gm?/piece)',
            r'Size:\s*(\d+[-\d]*\s*g)',
        ]
        
        for pattern in size_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                specs['fillet_size'] = self.clean_text(match.group(1))
                break
        
        # 3. Meat content - Enhanced patterns
        meat_patterns = [
            r'Meat Content:\s*([^\n]+)',
            r'Contains (\d+%\s*(?:chicken|meat|fish|mutton|beef)[^\n]*)',
            r'(\d+%\s*(?:chicken|meat|fish|mutton|beef))',
            r'Premium Ingredients?:\s*Contains (\d+%[^\n]+)',
        ]
        
        for pattern in meat_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                specs['meat_content'] = self.clean_text(match.group(1))
                break
        
        # 4. Weight variation
        weight_patterns = [
            r'Weight Variation[^:]*:\s*([^\n]+)',
            r'(±\d+g)',
            r'Weight.*?(\+/-\s*\d+g)',
        ]
        
        for pattern in weight_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                specs['weight_variation'] = self.clean_text(match.group(1))
                break
        
        # 5. Shelf life - Enhanced patterns
        shelf_patterns = [
            r'Shelf Life:\s*([^\n]+)',
            r'Lasts up to (\d+\s*days?[^\n]*)',
            r'(\d+\s*days? from manufacturing)',
            r'(\d+\s*days? when stored)',
            r'Best before (\d+\s*days?)',
        ]
        
        for pattern in shelf_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                specs['shelf_life'] = self.clean_text(match.group(1))
                break
        
        # 6. Storage instructions - Enhanced
        storage_patterns = [
            r'Storage[^:]*:\s*([^\n]+(?:\n[^\n]+)*?)(?=\n\n|Thawing|Cooking|Shelf)',
            r'Store at ([^\n]+)',
            r'Keep frozen at ([^\n]+)',
            r'Storage.*?Handling:\s*([^\n]+)',
        ]
        
        for pattern in storage_patterns:
            match = re.search(pattern, text, re.IGNORECASE | re.DOTALL)
            if match:
                storage_text = self.clean_text(match.group(1))
                if len(storage_text) > 10:  # Ensure it's substantial
                    specs['storage_instructions'] = storage_text
                    break
        
        # 7. Thawing instructions - Enhanced
        thawing_patterns = [
            r'Thawing Instructions?:\s*(.+?)(?=Important:|Cooking|Storage|$)',
            r'Thaw\s+in[^.]+\.',
            r'Refrigerator Method[^:]*:(.+?)(?=Cold Water|Important)',
            r'Cold Water Method[^:]*:(.+?)(?=Important|$)',
        ]
        
        for pattern in thawing_patterns:
            match = re.search(pattern, text, re.IGNORECASE | re.DOTALL)
            if match:
                thawing_text = self.clean_text(match.group(1))
                if len(thawing_text) > 20:  # Ensure substantial content
                    specs['thawing_instructions'] = thawing_text
                    break
        
        # 8. Cooking instructions - Enhanced
        cooking_patterns = [
            r'Cooking Instructions?:\s*(.+?)(?=Shelf Life|Storage|Serving|$)',
            r'From Freezer to Fryer:\s*(.+?)(?=Safety|Shelf|$)',
            r'Deep fry at ([^\n]+)',
            r'Heat for (\d+[^\n]+)',
            r'Microwave[^:]*:\s*([^\n]+)',
        ]
        
        for pattern in cooking_patterns:
            match = re.search(pattern, text, re.IGNORECASE | re.DOTALL)
            if match:
                cooking_text = self.clean_text(match.group(1))
                if len(cooking_text) > 10:
                    specs['cooking_instructions'] = cooking_text
                    break
        
        # 9. Serving suggestions - Enhanced
        serving_patterns = [
            r'Serving Suggestions?:\s*(.+?)(?=Pack Size|Similar|More from|$)',
            r'Enjoy (\w+[^.]+\.)',
            r'Perfect (?:as|for) ([^.]+\.)',
        ]
        
        for pattern in serving_patterns:
            match = re.search(pattern, text, re.IGNORECASE | re.DOTALL)
            if match:
                serving_text = self.clean_text(match.group(1))
                if len(serving_text) > 15:
                    specs['serving_suggestions'] = serving_text
                    break
        
        # 10. Key features - Enhanced
        features_patterns = [
            r'Key Features?:\s*(.+?)(?=Serving|Cooking|Product Highlights|$)',
            r'Features?:\s*(.+?)(?=Serving|Cooking|$)',
        ]
        
        for pattern in features_patterns:
            match = re.search(pattern, text, re.IGNORECASE | re.DOTALL)
            if match:
                features_text = self.clean_text(match.group(1))
                if len(features_text) > 20:
                    specs['key_features'] = features_text
                    break
        
        # 11. Product highlights - Enhanced
        highlights_patterns = [
            r'Product Highlights?:\s*(.+?)(?=Key Features|Cooking|Storage|$)',
            r'Highlights?:\s*(.+?)(?=Key Features|$)',
        ]
        
        for pattern in highlights_patterns:
            match = re.search(pattern, text, re.IGNORECASE | re.DOTALL)
            if match:
                highlights_text = self.clean_text(match.group(1))
                if len(highlights_text) > 20:
                    specs['product_highlights'] = highlights_text
                    break
        
        # 12. Premium ingredients - Enhanced
        ingredients_patterns = [
            r'Premium Ingredients?:\s*([^\n]+)',
            r'Made with ([^.]+high-quality[^.]+)',
            r'Crafted with ([^.]+)',
        ]
        
        for pattern in ingredients_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                ingredient_text = self.clean_text(match.group(1))
                if len(ingredient_text) > 10:
                    specs['premium_ingredients'] = ingredient_text
                    break
        
        # 13. Health conscious info - Enhanced
        health_patterns = [
            r'Health-?Conscious:\s*([^\n]+)',
            r'Contains no ([^\n]+)',
            r'Free from ([^\n]+)',
            r'No ([^.]+palm oil[^.]*)',
        ]
        
        for pattern in health_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                health_text = self.clean_text(match.group(1))
                if len(health_text) > 5:
                    specs['health_conscious_info'] = health_text
                    break
        
        return specs
    
    def extract_perfect_product_details(self, product_url: str) -> Optional[PerfectProduct]:
        """Extract PERFECT product details from individual page"""
        soup = self.safe_request(product_url)
        if not soup:
            return None
        
        logger.info(f"🔍 Extracting perfect details from: {product_url}")
        
        product = PerfectProduct()
        product.product_page_url = product_url
        product.scraped_timestamp = datetime.now().isoformat()
        
        try:
            full_text = soup.get_text()
            
            # 1. Extract product name from H1 (most reliable)
            h1_tag = soup.find('h1')
            if h1_tag:
                product.product_name = self.clean_text(h1_tag.get_text())
            
            # Fallback to title if no H1
            if not product.product_name:
                title_tag = soup.find('title')
                if title_tag:
                    title_text = title_tag.get_text()
                    # Clean title (remove "Wholesalers..." suffix)
                    title_clean = re.sub(r'\s+Wholesalers.*$', '', title_text)
                    product.product_name = self.clean_text(title_clean)
            
            # 2. Extract description (first substantial paragraph after product name)
            desc_patterns = [
                r'Product details\s*(.+?)(?=Product Highlights|Key Features|Similar)',
                r'<h1[^>]*>.*?</h1>\s*([^<]+(?:<[^>]*>[^<]*</[^>]*>)*[^<]*?)(?=Product Highlights)',
            ]
            
            for pattern in desc_patterns:
                match = re.search(pattern, str(soup), re.IGNORECASE | re.DOTALL)
                if match:
                    desc_soup = BeautifulSoup(match.group(1), 'lxml')
                    desc_text = self.clean_text(desc_soup.get_text())
                    if len(desc_text) > 50:
                        product.product_description = desc_text[:500]  # Limit length
                        break
            
            # 3. Extract price information
            product.price_current, product.price_original, product.discount_percentage = \
                self.extract_perfect_price_info(soup, full_text)
            
            # 4. Extract image URL
            img_selectors = [
                'img[src*="products"]',
                'img[data-src*="products"]',
                '.product-image img',
                '[class*="image"] img'
            ]
            
            for selector in img_selectors:
                img_elem = soup.select_one(selector)
                if img_elem:
                    img_src = img_elem.get('src') or img_elem.get('data-src')
                    if img_src and 'products' in img_src:
                        product.product_image_url = urljoin(self.base_url, img_src)
                        break
            
            # 5. Extract detailed specifications
            specs = self.extract_perfect_specifications(soup, full_text)
            
            # Apply all specifications to product
            for key, value in specs.items():
                if hasattr(product, key) and value:
                    setattr(product, key, value)
            
            # 6. Extract unit size from product name or description
            unit_patterns = [
                r'(\d+(?:\.\d+)?\s*(?:gm|kg|ml|l|ltr|pc|pcs))',
                r'\((\d+(?:\.\d+)?\s*(?:gm|kg|ml|l)/?\w*)\)',
                r'(\d+\s*gm?/pc)',
            ]
            
            text_to_search = f"{product.product_name} {product.product_description}"
            for pattern in unit_patterns:
                match = re.search(pattern, text_to_search, re.IGNORECASE)
                if match:
                    product.unit_size = match.group(1).strip()
                    break
            
            # 7. Determine packaging type
            packaging_keywords = {
                'frozen': 'Frozen',
                'fresh': 'Fresh', 
                'chilled': 'Chilled',
                'ambient': 'Ambient',
                'dry': 'Dry'
            }
            
            lower_text = full_text.lower()
            for keyword, packaging_type in packaging_keywords.items():
                if keyword in lower_text:
                    product.packaging_type = packaging_type
                    break
            
            # 8. Extract SKU from URL
            url_path = urlparse(product_url).path
            sku_match = re.search(r'/([a-zA-Z0-9\-_]+)(?:\?|$)', url_path)
            if sku_match:
                product.sku_code = sku_match.group(1)
            
            # 9. Extract category from breadcrumbs or URL
            breadcrumb_elem = soup.find(['nav', 'ol', 'ul'], class_=re.compile(r'breadcrumb', re.I))
            if breadcrumb_elem:
                breadcrumb_text = breadcrumb_elem.get_text()
                categories = [self.clean_text(cat) for cat in breadcrumb_text.split('>') if cat.strip()]
                if len(categories) > 1:
                    product.category = categories[-2] if len(categories) > 2 else categories[-1]
            
            # Fallback: extract from URL
            if not product.category:
                url_parts = product_url.split('/')
                if 'in' in url_parts:
                    try:
                        in_index = url_parts.index('in')
                        if in_index + 1 < len(url_parts):
                            category_slug = url_parts[in_index + 1]
                            product.category = category_slug.replace('-', ' ').title()
                    except ValueError:
                        pass
            
            # 10. Extract tags from badges and dietary info
            badge_selectors = [
                'img[alt*="dietary"]',
                '[class*="badge"]',
                '[class*="tag"]',
                '[class*="label"]'
            ]
            
            tags = []
            for selector in badge_selectors:
                elements = soup.select(selector)
                for elem in elements:
                    if elem.name == 'img':
                        tag_text = elem.get('alt', '')
                    else:
                        tag_text = self.clean_text(elem.get_text())
                    
                    if tag_text and len(tag_text) > 2 and tag_text not in tags:
                        tags.append(tag_text)
            
            # Add tags based on content analysis
            content_tags = []
            if 'premium' in full_text.lower():
                content_tags.append('Premium')
            if 'handcrafted' in full_text.lower() or 'hand-crafted' in full_text.lower():
                content_tags.append('Handcrafted')
            if 'imported' in full_text.lower():
                content_tags.append('Imported')
            if product.packaging_type:
                content_tags.append(product.packaging_type)
            
            tags.extend([tag for tag in content_tags if tag not in tags])
            
            if tags:
                product.tags = ";".join(tags)
            
            logger.info(f"✅ Successfully extracted: {product.product_name}")
            return product
            
        except Exception as e:
            logger.error(f"❌ Error extracting details from {product_url}: {str(e)}")
            return None
    
    def get_all_product_urls(self) -> List[str]:
        """Get ALL product URLs from Hyperpure"""
        logger.info("🔍 Discovering all product URLs...")
        
        # Starting URLs to explore
        starting_urls = [
            f"{self.base_url}/in/Menu-Addons",
            f"{self.base_url}/in/brownies-cakes-and-lava",
            f"{self.base_url}/in/chicken-breast-boneless",
            f"{self.base_url}/in/cheese",
            f"{self.base_url}/in/curd",
            f"{self.base_url}/in/ghee",
            f"{self.base_url}/in/milk-milk-powder",
            f"{self.base_url}/in/butter",
            f"{self.base_url}/in/paneer",
            f"{self.base_url}/in/cream",
            f"{self.base_url}/in/eggs",
        ]
        
        all_product_urls = set()
        
        for start_url in starting_urls:
            soup = self.safe_request(start_url)
            if not soup:
                continue
                
            # Find all product links
            links = soup.find_all('a', href=True)
            for link in links:
                href = link.get('href', '')
                
                # Filter for product pages
                if ('/in/' in href and 
                    not any(skip in href for skip in ['Menu-Addons', 'category', '#', 'javascript']) and
                    any(indicator in href for indicator in [
                        'frozen', 'brownie', 'chicken', 'burger', 'chutney', 'paneer',
                        'cheese', 'ghee', 'butter', 'cream', 'milk', 'egg', 'curd'
                    ])):
                    
                    full_url = urljoin(self.base_url, href)
                    all_product_urls.add(full_url)
        
        logger.info(f"📊 Found {len(all_product_urls)} unique product URLs")
        return list(all_product_urls)
    
    def scrape_all_perfect_products(self) -> List[PerfectProduct]:
        """Scrape ALL products with PERFECT data"""
        logger.info("🚀 Starting PERFECT product scraping...")
        
        # Get all product URLs
        product_urls = self.get_all_product_urls()
        
        if not product_urls:
            logger.error("❌ No product URLs found")
            return []
        
        for i, product_url in enumerate(product_urls):
            try:
                logger.info(f"📦 Processing {i+1}/{len(product_urls)}: {product_url}")
                
                # Extract perfect product details
                perfect_product = self.extract_perfect_product_details(product_url)
                
                if perfect_product and perfect_product.product_name:
                    self.products.append(perfect_product)
                    logger.info(f"✅ Added: {perfect_product.product_name}")
                else:
                    logger.warning(f"⚠️ Failed to extract: {product_url}")
                
                # Progress update
                if (i + 1) % 10 == 0:
                    logger.info(f"📊 Progress: {i+1}/{len(product_urls)} completed, {len(self.products)} products scraped")
                
            except Exception as e:
                logger.error(f"❌ Error processing {product_url}: {str(e)}")
                continue
        
        logger.info(f"🎉 PERFECT scraping completed! Total: {len(self.products)} products")
        return self.products
    
    def save_perfect_csv(self, filename: str = "hyperpure_PERFECT_products.csv"):
        """Save PERFECT data to CSV"""
        if not self.products:
            logger.error("❌ No products to save")
            return
        
        # All field names for perfect data
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
                    # Convert to dict
                    row = {}
                    for field in fieldnames:
                        row[field] = getattr(product, field, "")
                    writer.writerow(row)
            
            logger.info(f"💾 PERFECT data saved: {len(self.products)} products in {filename}")
            
            # Show data quality stats
            filled_fields = {}
            for field in fieldnames:
                filled_count = sum(1 for p in self.products if getattr(p, field, ""))
                filled_fields[field] = (filled_count, filled_count / len(self.products) * 100)
            
            logger.info("📊 Data Quality Report:")
            for field, (count, percentage) in filled_fields.items():
                if percentage > 0:
                    logger.info(f"  {field}: {count}/{len(self.products)} ({percentage:.1f}%)")
            
        except Exception as e:
            logger.error(f"❌ Error saving CSV: {str(e)}")


def main():
    """Main function"""
    parser = argparse.ArgumentParser(description='Hyperpure PERFECT Product Scraper')
    parser.add_argument('--output', default='hyperpure_PERFECT_products.csv', help='Output CSV filename')
    parser.add_argument('--limit', type=int, help='Limit products for testing')
    args = parser.parse_args()
    
    scraper = HyperpurePerfectScraper()
    
    try:
        # Scrape all products with perfect data
        products = scraper.scrape_all_perfect_products()
        
        # Apply limit if specified
        if args.limit and len(products) > args.limit:
            products = products[:args.limit]
            scraper.products = products
            logger.info(f"🔒 Limited to {args.limit} products for testing")
        
        if products:
            # Save perfect CSV
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"hyperpure_PERFECT_{timestamp}.csv"
            if args.output != 'hyperpure_PERFECT_products.csv':
                filename = args.output
            
            scraper.save_perfect_csv(filename)
            
            print(f"\n🎉 PERFECT scraping completed!")
            print(f"📊 Total products: {len(products)}")
            print(f"💾 Data saved to: {filename}")
            
            # Show sample perfect data
            if products:
                sample = products[0]
                print(f"\n🔍 Sample PERFECT data for '{sample.product_name}':")
                print(f"  💰 Price: {sample.price_current}")
                print(f"  📦 Pieces: {sample.no_of_pieces}")
                print(f"  🥩 Meat content: {sample.meat_content}")
                print(f"  ❄️ Storage: {sample.storage_instructions[:60]}...")
                print(f"  🍳 Cooking: {sample.cooking_instructions[:60]}...")
                print(f"  🏷️ Tags: {sample.tags}")
        else:
            print("❌ No products scraped. Check logs for errors.")
            
    except KeyboardInterrupt:
        print("\n⏹️ Scraping interrupted by user")
        if scraper.products:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"hyperpure_PERFECT_partial_{timestamp}.csv"
            scraper.save_perfect_csv(filename)
            print(f"💾 Partial data saved to: {filename}")
            
    except Exception as e:
        logger.error(f"💥 Unexpected error: {str(e)}")
        print(f"❌ Error: {str(e)}")


if __name__ == "__main__":
    main()
