from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
import time

# Setup Chrome
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))

try:
    all_links = []
    page = 1
    max_pages = 50  # Change this number to scrape more/fewer pages
    
    # Go to Myntra
    driver.get("https://www.myntra.com/women-kurtas-kurtis-suits")
    
    for page_num in range(1, max_pages + 1):
        print(f"\n📄 Scraping page {page_num}...")
        time.sleep(10)
        
        try:
            # Get product links from current page (fresh elements each time)
            links = driver.find_elements(By.CSS_SELECTOR, ".product-base a")
            page_links = [link.get_attribute("href") for link in links if link.get_attribute("href")]
            
            if page_links:
                all_links.extend(page_links)
                print(f"✅ Found {len(page_links)} links on page {page_num}")
            else:
                print(f"❌ No links found on page {page_num}")
                break
            
            # Don't try to go to next page if this is the last page we want
            if page_num >= max_pages:
                break
                
            # Try to click Next button (find fresh element each time)
            next_selectors = [
                ".pagination-next",
                "li.pagination-next a", 
                "a[aria-label='Next']"
            ]
            
            next_clicked = False
            for selector in next_selectors:
                try:
                    # Find fresh next button element
                    next_button = driver.find_element(By.CSS_SELECTOR, selector)
                    if next_button.is_enabled() and next_button.is_displayed():
                        # Scroll to button first
                        driver.execute_script("arguments[0].scrollIntoView();", next_button)
                        time.sleep(1)
                        # Click using JavaScript
                        driver.execute_script("arguments[0].click();", next_button)
                        print(f"🔄 Clicked Next button (selector: {selector})")
                        time.sleep(3)  # Wait for page to load
                        next_clicked = True
                        break
                except Exception as e:
                    continue
            
            if not next_clicked:
                print("❌ Next button not found or disabled - reached last page")
                break
                
        except Exception as e:
            print(f"❌ Error on page {page_num}: {e}")
            break
    
    # Remove duplicates
    unique_links = list(dict.fromkeys(all_links))
    
    # Save to file
    if unique_links:
        with open("myntra_products.txt", "w") as f:  # Use 'w' to overwrite
            for link in unique_links:
                f.write(link + "\n")
        
        print(f"\n🎉 FINAL RESULTS:")
        print(f"📊 Total pages scraped: {page_num}")
        print(f"🔗 Total links found: {len(all_links)}")
        print(f"✨ Unique links saved: {len(unique_links)}")
        print(f"💾 Saved to: myntra_products.txt")
    else:
        print("❌ No links found at all")

except Exception as e:
    print(f"Error: {e}")
finally:
    driver.quit()