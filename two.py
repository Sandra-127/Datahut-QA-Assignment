import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
import time
import re

class SimpleMyntraScraper:
    def __init__(self):
        # Setup Chrome options for better reliability
        options = Options()
        options.add_argument('--disable-blink-features=AutomationControlled')
        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        options.add_experimental_option('useAutomationExtension', False)
        options.add_argument('--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')
        
        self.driver = webdriver.Chrome(options=options)
        self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        self.wait = WebDriverWait(self.driver, 15)
        
    def scrape_product(self, url):
        """Scrape a single product from Myntra URL"""
        try:
            print(f"Scraping: {url}")
            self.driver.get(url)
            time.sleep(5)
            
            product = {}
            
            # Brand (usually first line)
            try:
                brand = self.wait.until(EC.presence_of_element_located(
                    (By.CSS_SELECTOR, "h1.pdp-title"))).text.strip()
                product['Brand'] = brand
            except:
                product['Brand'] = ""
            
            # Product Name
            try:
                name = self.driver.find_element(By.CSS_SELECTOR, "h1.pdp-name").text.strip()
                product['Product_Name'] = name
            except:
                product['Product_Name'] = ""
            
            # Price (discounted)
            try:
                price = self.driver.find_element(By.CSS_SELECTOR, ".pdp-price strong").text
                price_num = re.findall(r'\d+', price)
                product['Price'] = price_num[0] if price_num else ""
            except:
                product['Price'] = ""
            
            # MRP (original price)
            try:
                mrp = self.driver.find_element(By.CSS_SELECTOR, ".pdp-mrp s").text
                mrp_num = re.findall(r'\d+', mrp)
                product['MRP'] = mrp_num[0] if mrp_num else ""
            except:
                product['MRP'] = ""
            
            # Rating
            try:
                rating = self.driver.find_element(By.CSS_SELECTOR, ".index-overallRating div").text
                product['Rating'] = rating
            except:
                product['Rating'] = ""
            
            # Number of reviews
            try:
                reviews = self.driver.find_element(By.CSS_SELECTOR, ".index-ratingsCount").text
                review_num = re.findall(r'\d+', reviews)
                product['Reviews'] = review_num[0] if review_num else ""
            except:
                product['Reviews'] = ""
            
            # Category from breadcrumbs
            try:
                breadcrumbs = self.driver.find_elements(By.CSS_SELECTOR, ".breadcrumbs-link")
                if len(breadcrumbs) >= 3:
                    product['Category'] = breadcrumbs[2].text
                else:
                    product['Category'] = ""
            except:
                product['Category'] = ""
            
            product['URL'] = url
            print(f"✓ Successfully scraped: {product.get('Brand', 'Unknown')} - {product.get('Product_Name', 'Unknown')}")
            return product
            
        except Exception as e:
            print(f"✗ Error scraping {url}: {e}")
            return {
                'Brand': '', 'Product_Name': '', 'Price': '', 'MRP': '',
                'Rating': '', 'Reviews': '', 'Category': '', 'URL': url
            }
    
    def scrape_multiple(self, urls, save_file="myntra_products.csv", save_every=5):
        """Scrape multiple URLs and return DataFrame"""
        products = []
        
        for i, url in enumerate(urls, 1):
            print(f"\nProgress: {i}/{len(urls)}")
            product = self.scrape_product(url)
            products.append(product)
            
            # Save every N links
            if i % save_every == 0 or i == len(urls):
                df_temp = pd.DataFrame(products)
                df_temp.to_csv(save_file, index=False)
                print(f"💾 Saved progress: {i}/{len(urls)} products to {save_file}")
            
            # Delay between requests
            if i < len(urls):
                time.sleep(2)
        
        return pd.DataFrame(products)
    
    def close(self):
        """Close browser"""
        self.driver.quit()

# Simple usage function
def scrape_myntra(urls, save_file="myntra_products.csv", save_every=5):
    """
    Simple function to scrape Myntra products
    
    Args:
        urls (list): List of Myntra product URLs
        save_file (str): CSV filename to save results
        save_every (int): Save DataFrame every N links (default: 5)
    
    Returns:
        pandas.DataFrame: Scraped product data
    """
    scraper = SimpleMyntraScraper()
    
    try:
        # Scrape products with auto-save
        df = scraper.scrape_multiple(urls, save_file, save_every)
        
        print(f"\n✅ Final results saved to {save_file}")
        print(f"✅ Total products scraped: {len(df)}")
        
        # Show summary
        print("\nSample data:")
        print(df[['Brand', 'Product_Name', 'Price', 'Rating']].head())
        
        return df
    
    finally:
        scraper.close()

# Example usage
if __name__ == "__main__":
    # Example URLs (replace with actual Myntra product URLs)

    # Optional: Load URLs from file
    with open('myntra_products.txt', 'r') as f:   
        urls = [line.strip() for line in f.readlines() if line.strip()]
    df = scrape_myntra(urls)