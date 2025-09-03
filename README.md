# Hyperpure.com Product Scraper

A comprehensive Python web scraper to extract product listings from Hyperpure.com Menu Add-ons and export them to a detailed CSV file.

## Features

- **Comprehensive Data Extraction**: Scrapes 20+ product fields including name, price, description, ingredients, nutritional info, and more
- **Multi-Category Support**: Automatically discovers and scrapes all product categories and subcategories
- **Pagination Handling**: Automatically handles multi-page category listings
- **Dual Scraping Modes**: 
  - Standard mode using requests + BeautifulSoup (faster)
  - Selenium mode for JavaScript-heavy content (more reliable)
- **Ethical Scraping**: Implements delays, respects robots.txt, and uses proper headers
- **Error Recovery**: Robust error handling with retries and graceful failure recovery
- **Progress Tracking**: Detailed logging and progress reporting
- **CSV Export**: Clean, UTF-8 encoded CSV output with all required fields

## Requirements

Install the required packages:

```bash
pip install -r requirements.txt
```

### Required Packages
- requests==2.31.0
- beautifulsoup4==4.12.2
- lxml==4.9.3
- pandas==2.0.3

### Optional Packages (for Selenium mode)
- selenium==4.15.0
- webdriver-manager==4.0.1

## Usage

### Basic Usage (Recommended)

```bash
python hyperpure_scraper_enhanced.py
```

### Advanced Usage

```bash
# Use Selenium for JavaScript-heavy content
python hyperpure_scraper_enhanced.py --selenium

# Specify output filename
python hyperpure_scraper_enhanced.py --output my_products.csv

# Use Selenium with custom output
python hyperpure_scraper_enhanced.py --selenium --output hyperpure_selenium.csv
```

### Test Connectivity

Before running the full scraper, test your connection:

```bash
python test_scraper.py
```

## Output CSV Columns

The scraper exports a CSV file with the following columns:

| Column | Description | Example |
|--------|-------------|---------|
| `product_name` | Product name | "Premium Guacamole" |
| `category` | Product category | "Dips, Chutneys & Sauces" |
| `subcategory` | Subcategory (if available) | "" |
| `price_current` | Current price | "₹199" |
| `price_original` | Original price (if discounted) | "₹220" |
| `discount_percentage` | Calculated discount | "9.5%" |
| `product_description` | Detailed description | "Add a fiesta of flavor..." |
| `product_image_url` | Main product image URL | "https://assets.hyperpure.com/..." |
| `product_page_url` | Product detail page URL | "https://www.hyperpure.com/in/..." |
| `availability_status` | Stock status | "In Stock" |
| `brand_name` | Brand name | "Hyperpure" |
| `unit_size` | Package size | "500 gm" |
| `packaging_type` | Packaging type | "Frozen" |
| `nutritional_info` | Nutritional information | "" |
| `ingredients` | Ingredient list | "100% imported avocados..." |
| `product_id` | Product ID/SKU | "" |
| `sku_code` | SKU code | "" |
| `rating` | Product rating | "" |
| `review_count` | Number of reviews | "" |
| `tags` | Product tags/features | "Premium;Chunky;Imported" |
| `scraped_timestamp` | Scraping timestamp | "2025-09-04T01:13:00" |

## Example Output

```csv
product_name,category,subcategory,price_current,price_original,discount_percentage,product_description,product_image_url,product_page_url,availability_status,brand_name,unit_size,packaging_type,nutritional_info,ingredients,product_id,sku_code,rating,review_count,tags,scraped_timestamp
"Walnut Brownie (80 gm/pc), 720 gm (Frozen)","Brownies, Lavas and Desserts","","₹220","","","Premium Walnut Brownies: Indulge in our rich, fudgy, and moist brownies...","https://assets.hyperpure.com/data/images/products/ca4c85429e5b97a24e3826933b8f023c.jpg","https://www.hyperpure.com/in/walnut-brownie-80-gm-pc-pack-of-9-frozen","In Stock","Hyperpure","720 gm","Frozen","","","","walnut-brownie-80-gm-pc-pack-of-9-frozen","","","","2025-09-03T15:30:00"
```

## Scraper Architecture

### 1. Main Scraper Class (`HyperpureScraperEnhanced`)
- Handles session management and configuration
- Provides both requests and Selenium backends
- Manages rate limiting and ethical scraping practices

### 2. Product Data Class (`Product`)
- Structured data representation with all required fields
- Built-in CSV export functionality
- Data validation and cleaning

### 3. Core Scraping Methods
- `get_category_links()`: Discovers all product categories
- `scrape_category_page()`: Handles category-level scraping with pagination
- `extract_product_from_listing()`: Extracts data from product listing pages
- `scrape_product_details()`: Fetches detailed info from individual product pages

### 4. Data Processing
- Text cleaning and normalization
- Price extraction and discount calculation
- Unit size parsing with regex patterns
- Image URL resolution

## Configuration

### Ethical Scraping Settings
- Random delays between requests (1-3 seconds)
- Proper User-Agent headers
- Respects robots.txt
- Maximum retry attempts with exponential backoff
- Session persistence for efficiency

### Selenium Configuration (Optional)
- Headless Chrome browser
- Optimized for performance
- Automatic WebDriver management
- Wait conditions for dynamic content

## Logging

The scraper creates detailed logs in `hyperpure_scraper.log` including:
- Request success/failure status
- Product extraction progress
- Category processing status
- Error details and retry attempts
- Final statistics

## Error Handling

- **Network Issues**: Automatic retry with exponential backoff
- **Parsing Errors**: Graceful degradation with partial data
- **Missing Elements**: Default values for missing fields
- **Rate Limiting**: Automatic delay adjustment
- **Interruption**: Saves partial data on Ctrl+C

## Performance

### Standard Mode (requests + BeautifulSoup)
- **Speed**: ~2-3 seconds per product page
- **Memory**: Low memory usage
- **Reliability**: Good for static content

### Selenium Mode
- **Speed**: ~5-7 seconds per product page
- **Memory**: Higher memory usage
- **Reliability**: Better for JavaScript-heavy content

## Troubleshooting

### Common Issues

1. **Connection Errors**
   ```bash
   # Test connectivity first
   python test_scraper.py
   ```

2. **No Products Found**
   - Try Selenium mode: `--selenium`
   - Check if website structure changed
   - Verify robots.txt compliance

3. **Selenium Issues**
   ```bash
   # Install Chrome dependencies on Linux
   sudo apt-get update
   sudo apt-get install -y google-chrome-stable
   ```

4. **Memory Issues**
   - Use standard mode instead of Selenium
   - Process categories individually
   - Implement data streaming for large datasets

### Debug Mode

Enable debug logging by modifying the logging level:

```python
logging.basicConfig(level=logging.DEBUG)
```

## Legal Considerations

- This scraper respects robots.txt
- Implements ethical scraping practices
- For educational and research purposes
- Users responsible for compliance with terms of service
- Consider reaching out to Hyperpure for API access for commercial use

## Contributing

1. Fork the repository
2. Create a feature branch
3. Add tests for new functionality
4. Submit a pull request

## License

This project is for educational purposes. Please respect the website's terms of service and implement appropriate delays and limits for production use.

## Changelog

### v1.0.0 (2025-09-03)
- Initial release
- Comprehensive product data extraction
- Dual scraping modes (requests/Selenium)
- CSV export functionality
- Ethical scraping implementation
