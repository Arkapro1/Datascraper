#!/usr/bin/env python3
"""
Enhanced Hyperpure.com Product Scraper
====================================

An improved web scraper with specific selectors and Selenium support for JS-heavy content.

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
from urllib.parse import urljoin, urlparse, parse_qs
from datetime import datetime
import json
from typing import List, Dict, Optional, Set
import random
from dataclasses import dataclass
import sys
import argparse

# Optional Selenium imports
try:
    from selenium import webdriver
    from selenium.webdriver.common.by import By
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC
    from selenium.webdriver.chrome.options import Options
    from selenium.webdriver.chrome.service import Service
    from webdriver_manager.chrome import ChromeDriverManager
    SELENIUM_AVAILABLE = True
except ImportError:
    SELENIUM_AVAILABLE = False
    print("Selenium not available. Install with: pip install selenium webdriver-manager")


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


class HyperpureScraperEnhanced:
    """Enhanced scraper class for Hyperpure.com with Selenium support"""
    
    def __init__(self, use_selenium: bool = False):
        self.base_url = "https://www.hyperpure.com"
        self.use_selenium = use_selenium and SELENIUM_AVAILABLE
        self.session = requests.Session()
        self.driver = None
        self.setup_session()
        self.scraped_urls: Set[str] = set()
        self.products: List[Product] = []
        
        if self.use_selenium:
            self.setup_selenium()
        
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
        
    def setup_selenium(self):
        """Setup Selenium WebDriver"""
        try:
            chrome_options = Options()
            chrome_options.add_argument('--headless')
            chrome_options.add_argument('--no-sandbox')
            chrome_options.add_argument('--disable-dev-shm-usage')
            chrome_options.add_argument('--disable-gpu')
            chrome_options.add_argument('--window-size=1920,1080')
            chrome_options.add_argument('--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36')
            
            service = Service(ChromeDriverManager().install())
            self.driver = webdriver.Chrome(service=service, options=chrome_options)
            logger.info("Selenium WebDriver initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize Selenium: {str(e)}")
            self.use_selenium = False
    
    def get_page_content(self, url: str) -> Optional[BeautifulSoup]:
        """Get page content using either requests or Selenium"""
        if self.use_selenium:
            return self.get_page_selenium(url)
        else:
            return self.safe_request(url)
    
    def get_page_selenium(self, url: str) -> Optional[BeautifulSoup]:
        """Get page content using Selenium"""
        try:
            self.driver.get(url)
            
            # Wait for page to load
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.TAG_NAME, "body"))
            )
            
            # Additional wait for dynamic content
            time.sleep(2)
            
            html = self.driver.page_source
            return BeautifulSoup(html, 'lxml')
            
        except Exception as e:
            logger.error(f"Selenium error for {url}: {str(e)}")
            return None
    
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
        """Extract current price, original price, and discount percentage from price element"""
        current_price = ""
        original_price = ""
        discount_pct = ""
        
        if not element:
            return current_price, original_price, discount_pct
        
        price_text = self.clean_text(element.get_text())
        
        # Extract current price - look for ₹ followed by numbers
        current_matches = re.findall(r'₹(\d+(?:,\d+)*(?:\.\d+)?)', price_text)
        if current_matches:
            current_price = f"₹{current_matches[0]}"
        
        # Look for strikethrough or crossed prices (original price)
        strikethrough_elem = element.find(['s', 'del', 'strike']) or \
                           element.find(attrs={'style': re.compile(r'text-decoration:\s*line-through', re.I)})
        
        if strikethrough_elem:
            original_text = strikethrough_elem.get_text()
            original_match = re.search(r'₹(\d+(?:,\d+)*(?:\.\d+)?)', original_text)
            if original_match:
                original_price = f"₹{original_match.group(1)}"
        
        # Calculate discount if both prices available
        if current_price and original_price:
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
            r'(\d+(?:\.\d+)?\s*(?:gm|kg|ml|ltr|litre|pc|pcs|piece|pieces|pack|packs)(?:\s*/\s*\w+)?)',
            r'(\d+(?:\.\d+)?\s*(?:gram|kilogram|milliliter|liter))',
            r'\((\d+(?:\.\d+)?\s*(?:gm|kg|ml|ltr|pc|pcs)/?\w*)\)',
            r'(\d+(?:\.\d+)?\s*(?:g|kg|ml|l)\b)'
        ]
        
        for pattern in size_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                return match.group(1).strip()
        
        return ""
    
    def get_category_links(self, soup: BeautifulSoup) -> List[tuple[str, str]]:
        """Extract all category and subcategory links from the main page"""
        category_links = []
        
        # Look for category navigation elements
        # Based on the HTML structure observed, categories appear as links with images
        
        # Try multiple selectors for category links
        selectors = [
            'a[href*="/in/"]',  # General pattern for category links
            'a[href*="Menu-Addons"]',  # Specific menu addon links
            'div img[alt] + a',  # Image with alt text followed by link
            'a img[alt]'  # Links containing images with alt text
        ]
        
        found_links = set()
        
        for selector in selectors:
            try:
                elements = soup.select(selector)
                for element in elements:
                    href = element.get('href', '')
                    
                    # Get text from alt attribute or element text
                    text = ""
                    img = element.find('img')
                    if img and img.get('alt'):
                        text = img['alt']
                    else:
                        text = self.clean_text(element.get_text())
                    
                    if href and text:
                        # Skip certain non-category links
                        skip_patterns = ['home', 'cart', 'login', 'register', 'contact', 'about']
                        if any(pattern in href.lower() or pattern in text.lower() for pattern in skip_patterns):
                            continue
                        
                        full_url = urljoin(self.base_url, href)
                        if (text, full_url) not in found_links:
                            found_links.add((text, full_url))
                            category_links.append((text, full_url))
                            
            except Exception as e:
                logger.warning(f"Error with selector {selector}: {str(e)}")
                continue
        
        # Remove duplicates and filter
        category_links = list(set(category_links))
        
        # Filter out non-product category URLs
        filtered_links = []
        for name, url in category_links:
            # Keep URLs that look like product categories
            if any(keyword in url.lower() for keyword in ['/in/', 'menu', 'category', 'products']):
                if name and len(name.strip()) > 2:  # Skip very short names
                    filtered_links.append((name, url))
        
        logger.info(f"Found {len(filtered_links)} category links")
        return filtered_links
    
    def extract_product_from_listing(self, product_element, category: str = "") -> Optional[Product]:
        """Extract product information from a product listing element"""
        product = Product()
        product.scraped_timestamp = datetime.now().isoformat()
        product.category = category
        
        try:
            # Product name - try multiple selectors
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
            
            # Price information - look for price containers
            price_selectors = ['[class*="price"]', '[class*="cost"]', '[class*="amount"]', 'span:contains("₹")']
            for selector in price_selectors:
                price_elem = product_element.select_one(selector)
                if price_elem:
                    product.price_current, product.price_original, product.discount_percentage = self.extract_price_info(price_elem)
                    if product.price_current:
                        break
            
            # If no price found, try searching in text
            if not product.price_current:
                element_text = product_element.get_text()
                price_match = re.search(r'₹(\d+(?:,\d+)*(?:\.\d+)?)', element_text)
                if price_match:
                    product.price_current = f"₹{price_match.group(1)}"
            
            # Product image
            img_elem = product_element.find('img')
            if img_elem:
                img_src = img_elem.get('src') or img_elem.get('data-src') or img_elem.get('data-original')
                if img_src:
                    product.product_image_url = urljoin(self.base_url, img_src)
            
            # Unit size
            product.unit_size = self.extract_unit_size(product.product_name)
            
            # Availability status
            out_of_stock_indicators = ['out of stock', 'unavailable', 'sold out', 'notify me']
            element_text = product_element.get_text().lower()
            if any(indicator in element_text for indicator in out_of_stock_indicators):
                product.availability_status = "Out of Stock"
            else:
                # Look for "ADD" button or similar
                if 'add' in element_text and ('cart' in element_text or 'bag' in element_text or '+' in element_text):
                    product.availability_status = "In Stock"
                else:
                    product.availability_status = "In Stock"  # Default assumption
            
            # Tags (dietary badges, features)
            badge_selectors = ['[class*="badge"]', '[class*="tag"]', '[class*="dietary"]', 'img[alt*="dietary"]']
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
            
            if product.product_name:  # Only return if we got at least a name
                return product
                
        except Exception as e:
            logger.error(f"Error extracting product: {str(e)}")
            
        return None
    
    def scrape_product_details(self, product: Product) -> Product:
        """Scrape detailed information from individual product page"""
        if not product.product_page_url or product.product_page_url in self.scraped_urls:
            return product
        
        soup = self.get_page_content(product.product_page_url)
        if not soup:
            return product
        
        self.scraped_urls.add(product.product_page_url)
        
        try:
            # Product description - look for detailed description
            desc_selectors = [
                '[class*="description"]',
                '[class*="detail"]',
                '[class*="about"]',
                'div p',
                'section p'
            ]
            
            for selector in desc_selectors:
                desc_elem = soup.select_one(selector)
                if desc_elem:
                    desc_text = self.clean_text(desc_elem.get_text())
                    if len(desc_text) > 50:  # Ensure it's substantial description
                        product.product_description = desc_text
                        break
            
            # Look for key features, ingredients, nutritional info in text
            full_text = soup.get_text()
            
            # Ingredients
            ingredients_match = re.search(r'ingredients?[:\s]+(.*?)(?:\n|\.|\|)', full_text, re.IGNORECASE | re.DOTALL)
            if ingredients_match:
                product.ingredients = self.clean_text(ingredients_match.group(1))
            
            # Nutritional information
            nutrition_keywords = ['nutrition', 'nutritional', 'calories', 'protein', 'carb']
            for keyword in nutrition_keywords:
                nutrition_match = re.search(rf'{keyword}[:\s]+(.*?)(?:\n|\.)', full_text, re.IGNORECASE)
                if nutrition_match:
                    product.nutritional_info = self.clean_text(nutrition_match.group(1))
                    break
            
            # Product ID/SKU - look in URL or page
            url_path = urlparse(product.product_page_url).path
            sku_match = re.search(r'/([a-zA-Z0-9\-_]+)(?:\?|$)', url_path)
            if sku_match:
                product.sku_code = sku_match.group(1)
            
            # Packaging type - infer from content
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
            
            # Update unit size if we find more detailed info
            if not product.unit_size:
                product.unit_size = self.extract_unit_size(full_text)
            
        except Exception as e:
            logger.error(f"Error scraping product details for {product.product_page_url}: {str(e)}")
        
        return product
    
    def scrape_category_page(self, category_name: str, category_url: str) -> List[Product]:
        """Scrape all products from a category page with pagination support"""
        products = []
        page_num = 1
        max_pages = 20  # Safety limit
        
        logger.info(f"Scraping category: {category_name} from {category_url}")
        
        while page_num <= max_pages:
            # Handle pagination
            if page_num > 1:
                if '?' in category_url:
                    paginated_url = f"{category_url}&page={page_num}"
                else:
                    paginated_url = f"{category_url}?page={page_num}"
            else:
                paginated_url = category_url
            
            soup = self.get_page_content(paginated_url)
            if not soup:
                break
            
            # Look for product containers
            product_selectors = [
                '[class*="product"]',
                '[class*="item"]',
                '[class*="card"]',
                'div:has(img):has(a)',
                'article'
            ]
            
            product_elements = []
            for selector in product_selectors:
                try:
                    elements = soup.select(selector)
                    if elements:
                        product_elements = elements
                        break
                except Exception as e:
                    logger.warning(f"Selector {selector} failed: {str(e)}")
                    continue
            
            if not product_elements:
                logger.info(f"No products found on page {page_num} for {category_name}")
                break
            
            page_products = []
            for elem in product_elements:
                # Check if this element actually contains product info
                if elem.find('img') and (elem.find('a') or '₹' in elem.get_text()):
                    product = self.extract_product_from_listing(elem, category_name)
                    if product and product.product_name:
                        # Get detailed information from product page
                        detailed_product = self.scrape_product_details(product)
                        page_products.append(detailed_product)
                        logger.info(f"Scraped: {detailed_product.product_name}")
                        
            products.extend(page_products)
            logger.info(f"Scraped {len(page_products)} products from {category_name} page {page_num}")
            
            # Check for next page
            has_next = soup.find('a', text=re.compile(r'next|more', re.IGNORECASE)) or \
                      soup.find('a', class_=re.compile(r'next|pagination')) or \
                      soup.find('[class*="next"]') or \
                      soup.find('[class*="pagination"]')
            
            if not has_next or len(page_products) == 0:
                break
                
            page_num += 1
        
        logger.info(f"Total products scraped from {category_name}: {len(products)}")
        return products
    
    def scrape_all_products(self) -> List[Product]:
        """Main method to scrape all products from all categories"""
        logger.info("Starting Hyperpure scraping process...")
        
        # Start from the main Menu Add-ons page
        main_url = f"{self.base_url}/in/Menu-Addons"
        soup = self.get_page_content(main_url)
        
        if not soup:
            logger.error("Failed to fetch main page")
            return []
        
        # First, try to scrape products directly from main page
        main_products = self.scrape_category_page("Menu Add-ons", main_url)
        self.products.extend(main_products)
        
        # Get category links for additional scraping
        category_links = self.get_category_links(soup)
        
        # Scrape each category
        for category_name, category_url in category_links:
            try:
                logger.info(f"Processing category: {category_name}")
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
    
    def cleanup(self):
        """Cleanup resources"""
        if self.driver:
            self.driver.quit()


def main():
    """Main function to run the scraper"""
    parser = argparse.ArgumentParser(description='Hyperpure.com Product Scraper')
    parser.add_argument('--selenium', action='store_true', help='Use Selenium for JavaScript-heavy content')
    parser.add_argument('--output', default='hyperpure_products.csv', help='Output CSV filename')
    args = parser.parse_args()
    
    scraper = HyperpureScraperEnhanced(use_selenium=args.selenium)
    
    try:
        # Scrape all products
        products = scraper.scrape_all_products()
        
        if products:
            # Save to CSV
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"hyperpure_products_{timestamp}.csv"
            if args.output != 'hyperpure_products.csv':
                filename = args.output
            
            scraper.save_to_csv(filename)
            
            print(f"\nScraping completed successfully!")
            print(f"Total products scraped: {len(products)}")
            print(f"Data saved to: {filename}")
            
            # Print statistics
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
        
    finally:
        scraper.cleanup()


if __name__ == "__main__":
    main()
