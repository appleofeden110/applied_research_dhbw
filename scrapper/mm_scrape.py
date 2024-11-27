from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.firefox.service import Service
from selenium.common.exceptions import TimeoutException
from bs4 import BeautifulSoup
import time

from review import Review


class MediaMarktScrapper:
    def __init__(self, browser: str, source: str, num_reviews: int, url: str):
        self.browser = browser
        self.source = source
        self.num_reviews = num_reviews
        self.url = url
        self.driver = None

    def _setup_driver(self):
        """Initialize the WebDriver."""
        if self.browser.lower() == "firefox":
            self.driver = webdriver.Firefox(
                service=Service("/snap/bin/geckodriver"))
        else:
            raise ValueError(f"Unsupported browser: {self.browser}")

    def _teardown_driver(self):
        """Quit the WebDriver."""
        if self.driver:
            self.driver.quit()

    def _handle_cookie_consent(self, timeout=10):
        """Handle cookie consent pop-ups."""
        try:
            consent_button = WebDriverWait(self.driver, timeout).until(
                EC.element_to_be_clickable(
                    (By.CSS_SELECTOR, '[data-test="pwa-consent-layer-accept-all"]'))
            )
            self.driver.execute_script(
                "arguments[0].scrollIntoView({block: 'center'});", consent_button)
            time.sleep(1)
            consent_button.click()

            WebDriverWait(self.driver, timeout).until_not(
                EC.presence_of_element_located(
                    (By.ID, 'pwa-consent-layer-accept-all-button'))
            )
            return True
        except TimeoutException:
            print("Cookie consent buttsafasfon not found or not clickable")
        except Exception as e:
            print(f"Error handling cookie consent: {e}")
        return False

    def scrape_reviews_mm(self):
        """Scrape reviews from MediaMarkt."""
        self._setup_driver()
        all_reviews = []
        prod_name = None
        prod_price = None
        idx: int = 0
        try:
            self.driver.get(self.url)
            self._handle_cookie_consent()

            for page in range(round(self.num_reviews / 10) if self.num_reviews >= 10 else 1):
                # Wait for reviews to load
                WebDriverWait(self.driver, 10).until(
                    EC.presence_of_element_located(
                        (By.CSS_SELECTOR, '[data-test="single-review-card"]'))
                )
                soup = BeautifulSoup(self.driver.page_source, 'html.parser')
                
                review_cards = soup.find_all(
                    'div', attrs={'data-test': 'single-review-card'})
                if idx ==0:
                    idx = 1
                else: 
                    idx+=len(review_cards)

                if not prod_name:
                    prod_name = self._extract_product_name(soup)
                if not prod_price:
                    prod_price = self._extract_product_price(soup)

                # Extract reviews
                all_reviews.extend(self._parse_reviews_mm(review_cards, prod_name, prod_price, idx))

                # Pagination
                if not self._click_next_page_mm():
                    break

        except Exception as e:
            print(f"An error occurred during MediaMarkt scraping: {e}")
        finally:
            self._teardown_driver()

        return all_reviews, prod_name

    def _extract_product_name(self, soup):
        """Extract product name from the page."""
        try:
            header_info = soup.find(
                'div', attrs={'data-test': 'mms-select-details-header'})
            if header_info:
                name_element = header_info.find("h1", class_="kRkMRa")
                return name_element.text.strip() if name_element else "Product name not found"
        except Exception as e:
            print(f"Error extracting product name: {e}")
        return "Error getting product name"

    def _extract_product_price(self, soup):
        """Extract product price from the page."""
        try:
            price_div = soup.find(
                'div', attrs={"data-test": "mms-product-price"})
            if price_div:
                price_element = price_div.find('span', class_="bPkjPs")
                return price_element.text.strip() if price_element else "Price not found"
        except Exception as e:
            print(f"Error extracting product price: {e}")
        return "Error getting price"

    def _parse_reviews_mm(self, review_cards, prod_name, prod_price, last_idx):
        """Parse reviews from the MediaMarkt review cards."""
        page_reviews = []
        for card in review_cards:
            try:
                rating_div = card.find(
                    'div', attrs={'data-test': 'mms-customer-rating'})
                rating = len(rating_div.find_all(
                    'div', class_='sc-155e821c-0')) if rating_div else "empty"

                review_text = card.find(
                    'p', attrs={'data-test': 'mms-review-full'})
                if not review_text:
                    review_text = card.find(
                        'p', attrs={'data-test': 'mms-review-truncated'})
                review_text = review_text.text.strip().replace("\n", " ") if review_text else "empty"
                author = card.find('span', class_='sc-8b815c14-0')
                author = author.text.strip() if author else "empty"
                last_idx+=1
                print(last_idx)
                # Replace with your Review data structure
                review_data = Review(
                    id=last_idx+1,
                    prod_name=prod_name,
                    price=prod_price, 
                    country="Germany",
                    source=self.source, 
                    author=author,
                    review_txt=review_text,
                    rating=rating
                )
                page_reviews.append(review_data)
            except Exception as e:
                print(f"Error parsing review card: {e}")
        return page_reviews

    def _click_next_page_mm(self):
        """Navigate to the next page of MediaMarkt reviews."""
        try:
            pagination = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located(
                    (By.CSS_SELECTOR, '[data-test="review-pagination-wrapper"]'))
            )
            next_button = pagination.find_element(
                By.XPATH, './/button[contains(., "Nächste Seite")]')
            if next_button.get_attribute('disabled') or next_button.get_attribute('aria-disabled') == 'true':
                return False
            self.driver.execute_script(
                "arguments[0].scrollIntoView({block: 'center'});", next_button)
            next_button.click()
            time.sleep(3)
            return True
        except Exception as e:
            print(f"Error navigating to next page: {e}")
        return False
