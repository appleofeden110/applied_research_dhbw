from typing import Dict, Tuple
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import StaleElementReferenceException, TimeoutException
from bs4 import BeautifulSoup
import time

class Review: 
    def __init__(self, id: int, prod_name: str, price: str, country: str, source: str, author: str, review_txt: str, rating: int):
        self.id = id
        self.prod_name = prod_name
        self.price = price
        self.country = country
        self.source = source
        self.author = author
        self.review_txt = review_txt
        self.rating = rating
    
    def to_dict(self) -> dict: 
        return {
            'id': self.id, 
            'prod_name': self.prod_name, 
            'price': self.price,
            'country': self.country, 
            'source': self.source,
            'author': self.author, 
            'review_txt': self.review_txt,
            'rating': self.rating
        }
    
# function is just for media markt and does literally what it says
def handle_cookie_consent(driver, timeout=10):
    try:
        consent_button = WebDriverWait(driver, timeout).until(
            EC.element_to_be_clickable((
                By.CSS_SELECTOR, 
                '[data-test="pwa-consent-layer-accept-all"]'
            ))
        )
        
        driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", consent_button)
        
        driver.implicitly_wait(1)
        
        consent_button.click()
        
        WebDriverWait(driver, timeout).until_not(
            EC.presence_of_element_located((
                By.ID, 
                'pwa-consent-layer-accept-all-button'
            ))
        )
        
        return True
        
    except TimeoutException:
        print("Cookie consent button not found or not clickable")
        return False
    except Exception as e:
        print(f"Error handling cookie consent: {e}")
        return False

def scrape_reviews(url, num_pages) -> Tuple[Dict, str]:
    # init of Selenium driver for opening a chrome window
    driver = webdriver.Chrome()
    all_reviews = []
    prod_name = None
    prod_price = None
    try:
        driver.get(url)
        handle_cookie_consent(driver, 10)
        
        for page in range(num_pages):
            
            # Wait for reviews to load w/ retry 
            max_retries = 3
            for retry in range(max_retries):
                try:
                    WebDriverWait(driver, 10).until(
                        EC.presence_of_element_located((By.CSS_SELECTOR, '[data-test="single-review-card"]'))
                    )
                    break
                except TimeoutException:
                    if retry == max_retries - 1:
                        print(f"Failed to load reviews on page {page + 1}")
                        raise
                    time.sleep(2)
            
            soup = BeautifulSoup(driver.page_source, 'html.parser')
            review_cards = soup.find_all('div', attrs={'data-test': 'single-review-card'})
            if prod_name is None:
                try:
                    header_info = soup.find('div', attrs={'data-test': 'mms-select-details-header'})
                    if header_info:
                        name_element = header_info.find('h1', class_="kRkMRa")
                        if name_element:
                            prod_name = name_element.text.strip()
                        else:
                            prod_name = "Product name not found"
                    print(f"Found product name: {prod_name}")
                except Exception as e:
                    print(f"Error getting product name: {e}")
                    prod_name = "Error getting product name"

            if prod_price is None:
                try:
                    price_div = soup.find('div', attrs={"data-test": "mms-product-price"})
                    if price_div:
                        price_element = price_div.find('span', class_="bPkjPs")
                        if price_element:
                            prod_price = price_element.text.strip()
                        else:
                            prod_price = "Price not found"
                    print(f"Found product price: {prod_price}")
                except Exception as e:
                    print(f"Error getting product price: {e}")
                    prod_price = "Error getting price"
            
            page_reviews = []
            for card in review_cards:
                try:
                    
                    rating_div = card.find('div', attrs={'data-test': 'mms-customer-rating'})
                    rating = len(rating_div.find_all('div', class_='sc-155e821c-0')) if rating_div else "empty"

                    review_text = card.find('p', attrs={'data-test': 'mms-review-full'})
                    if not review_text:
                        review_text = card.find('p', attrs={'data-test': 'mms-review-truncated'})
                    review_text = review_text.text.strip() if review_text else "empty"
                    #trimming new line and replacing it with space to not corrupt the csv
                    review_text = review_text.replace("\n", " ")

                    author = card.find('span', class_='sc-8b815c14-0')
                    author = author.text.strip() if author else "empty"
                    
                    review_data = Review(
                        id = 0,
                        prod_name=prod_name,
                        price=prod_price,
                        country="DE", 
                        source="media_markt", 
                        author=author, 
                        review_txt=review_text,
                        rating=rating
                    )
                    
                    page_reviews.append(review_data)
                    
                    
                except Exception as e:
                    print(f"Error extracting review data: {e}")
                    continue
            
            print(f"Scraped {len(page_reviews)} reviews from page {page + 1}")
            all_reviews.extend(page_reviews)
            # Only try to navigate if we're not on the last page
            if page < num_pages - 1:
                try:
                    # Implement a more robust next page click with retries
                    success = click_next_page(driver, max_retries)
                    if not success:
                        print(f"Could not proceed to next page after page {page + 1}")
                        break
                except Exception as e:
                    print(f"Error during pagination: {e}")
                    break
    except Exception as e:
        print(f"An error occurred: {e}")
    
    finally:
        driver.quit()
    
    return all_reviews, prod_name

def click_next_page(driver, max_retries=3):
    """Click next page button with improved handling of intercepted clicks."""
    for attempt in range(max_retries):
        try:
            # Wait for pagination wrapper
            pagination = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, '[data-test="review-pagination-wrapper"]'))
            )
            
            # Find next button
            next_button = pagination.find_element(By.XPATH, './/button[contains(., "Nächste Seite")]')
            
            # Check if disabled
            if next_button.get_attribute('disabled') or next_button.get_attribute('aria-disabled') == 'true':
                return False
            
            # First try: scroll the button into view with a larger offset
            driver.execute_script("""
                arguments[0].scrollIntoView({block: 'center'});
                window.scrollBy(0, -150);  // Larger offset to avoid headers/overlays
            """, next_button)
            time.sleep(1)
            
            try:
                # Try regular click first
                WebDriverWait(driver, 5).until(
                    EC.element_to_be_clickable((By.XPATH, './/button[contains(., "Nächste Seite")]'))
                ).click()
            except Exception as click_error:
                print(f"Regular click failed, trying JavaScript click...")
                # If regular click fails, try JavaScript click
                driver.execute_script("arguments[0].click();", next_button)
            
            # Verify the click worked by waiting for page content to change
            old_url = driver.current_url
            WebDriverWait(driver, 5).until(lambda d: d.current_url != old_url or 
                                         len(d.find_elements(By.CSS_SELECTOR, '[data-test="single-review-card"]')) > 0)
            
            return True
            
        except StaleElementReferenceException:
            if attempt < max_retries - 1:
                print(f"Stale element on attempt {attempt + 1}, retrying...")
                time.sleep(2)
                continue
            return False
        except Exception as e:
            if attempt < max_retries - 1:
                print(f"Click failed on attempt {attempt + 1}: trying again")
                time.sleep(2)
                
                # Try to remove any overlays or interfering elements
                try:
                    driver.execute_script("""
                        // Remove potential overlays
                        document.querySelectorAll('.sc-ad0ca069-0').forEach(e => e.remove());
                        // Remove fixed position elements that might interfere
                        document.querySelectorAll('*').forEach(e => {
                            const style = window.getComputedStyle(e);
                            if (style.position === 'fixed' || style.position === 'sticky') {
                                e.remove();
                            }
                        });
                    """)
                except:
                    pass
                
                continue
            print(f"Error clicking next page: {e}")
            return False
    
    return False
