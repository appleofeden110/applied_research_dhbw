from datetime import datetime
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.firefox.service import Service
from review import Review
import time
import random
import math

class AmazonCredentials:
    """Class to store Amazon credentials."""
    def __init__(self, email: str, password: str):
        self.email = email
        self.password = password


class AmazonScraper:
    def __init__(self, browser: str, source: str, num_reviews: int, url: str, credentials: AmazonCredentials):
        self.browser = browser
        self.source = source
        self.num_reviews = num_reviews
        self.url = url
        self.credentials = credentials
        self.driver = None

    def initialize_driver(self):
        """Initialize the WebDriver based on the browser."""
        if self.browser.lower() == "firefox":
            try:
                service = Service("/snap/bin/geckodriver")  # Update with your geckodriver path
                self.driver = webdriver.Firefox(service=service)
            except Exception as e:
                # strang ANSI in the terminal make the text red and bold
                print(f"\n\n{e}\033[31;1;4mTo use Firefox, go into ./scrapper/amz_scrape.py and please change the path to the geckodriver, otherwise use Chrome.\n\033[0m") 
        elif self.browser.lower() == "chrome":
            self.driver = webdriver.Chrome()
        else:
            raise ValueError("Currently - only Firefox and Chrome are supported. To use Firefox, go into ./scrapper/amz_scrape.py and please change the path to the geckodriver, otherwise use Chrome.")

    def humantype(self, element, text, delay=0.2):
        """Simulates human typing by sending keys with a delay."""
        for char in text:
            element.send_keys(char)
            time.sleep(delay * random.randint(1, 10) * math.pow(10, -3))

    def transform_k_notation(self, text):
        num = ''.join(c for c in text if c.isdigit() or c in 'K+.').strip()
        has_plus = '+' in num
        clean_num = num.replace('+', '')
        if 'K' in clean_num:
            result = int(float(clean_num.split('K')[0]) * 1000)
        else:
            result = int(float(clean_num))
        return f"{result:,}" + ('+' if has_plus else '')
    
    def split_date(self, date_string):
        try:
            for fmt in ['%d %B %Y', '%B %d %Y', '%Y-%m-%d']:
                try:
                    date_object = datetime.strptime(date_string, fmt)
                    return (date_object.day, date_object.month, date_object.year)
                except ValueError:
                    continue
            raise ValueError(f"Unable to parse date: {date_string}")
        except Exception as e:
            print(f"Error processing date {date_string}: {str(e)}")
            return None


    
    def scrape_amazon_reviews(self, category):
        """Scrape reviews from Amazon."""
        reviews_data = []
        prod_name = None
        current_review_count = 0




        
        try:
                self.initialize_driver()
                self.driver.get(self.url)
                self._handle_cookies()
                time.sleep(1)
                # Extract product price
                price_symbol = self.driver.find_element(By.CSS_SELECTOR, "span.a-price-symbol").text
                price_whole = self.driver.find_element(By.CSS_SELECTOR, "span.a-price-whole").text
                price_fraction = self.driver.find_element(By.CSS_SELECTOR, "span.a-price-fraction").text
                price = f"{price_symbol}{price_whole}.{price_fraction}"

                # Number of reviews
                review_num = self.driver.find_element(By.ID, "acrCustomerReviewText").text

                try:
                    element = self.driver.find_element(By.ID, "social-proofing-faceout-title-tk_bought")
                    bought_text = element.find_element(By.TAG_NAME, "span").text
                    bought_past_month = self.transform_k_notation(bought_text)                
                except Exception:
                    print("couldn't find amount bought in the past month")
                    bought_past_month = "not found"
                reveiw_link = WebDriverWait(self.driver, 10).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, "a[data-hook='see-all-reviews-link-foot']"))
                )
                reveiw_link.click()
                time.sleep(2)
                self._login()
                time.sleep(5)
                
                try:
                    translate_button = WebDriverWait(self.driver, 10).until(
                        EC.element_to_be_clickable((By.CSS_SELECTOR, '[data-hook="cr-translate-these-reviews-link"]'))
                    )
                    translate_button.click()
                except Exception:
                    print(f"Couldn't find clickable translation button")
                

                while current_review_count < self.num_reviews:
                    # Country

                    WebDriverWait(self.driver, 10).until(
                        EC.presence_of_all_elements_located((By.CSS_SELECTOR, "[data-hook='review']"))
                    )
                    reviews = self.driver.find_elements(By.CSS_SELECTOR, "[data-hook='review']")
                    time.sleep(1)
                    for review in reviews:
                        try:
                            # Product Name
                            prod_name_element = self.driver.find_element(By.CSS_SELECTOR, "[data-hook='product-link']")
                            prod_name = prod_name_element.text
                            # Country
                            # Reviewed in {country} on {date} 
                            place_date_info = review.find_element(By.CSS_SELECTOR, "span[data-hook='review-date']").text
                            print(place_date_info)
                            place_date = place_date_info.split('Reviewed in ')[1].split(' on ')
                            country = place_date[0]
                            date = place_date[1]
                            day, month, year = self.split_date(date)
                            # Author
                            author_element = review.find_element(By.CSS_SELECTOR, ".a-profile-name")
                            author = author_element.text

                            # Review Text
                            review_txt_element = review.find_element(By.CSS_SELECTOR, "[data-hook='review-body'] span")
                            review_txt = review_txt_element.text.replace("\n", " ")

                           # Alternative using XPath
                            try:
                                rating_element = review.find_element(By.XPATH, './/span[contains(@class, "a-icon-alt")] | .//i[@data-hook="review-star-rating"]//span')
                                rating_text = rating_element.get_attribute('textContent') or rating_element.text
                                rating = float(rating_text.split()[0].replace(',', '.')) if rating_text else None
                            except Exception as e:
                                print(f"Error getting rating with XPath: {e}")
                                rating = None
                            print(f"review number: {current_review_count+1}")
                            review_data = Review(
                                id = current_review_count+1,
                                prod_name = prod_name,
                                price = price,
                                category = category,
                                country = country,
                                source = self.source,
                                author = author,
                                review_txt = review_txt,
                                rating = rating,
                                nums_of_reviews = review_num,
                                bought_in_past_month=bought_past_month,
                                day = day, 
                                month = month, 
                                year = year
                            )

                            reviews_data.append(review_data)
                            current_review_count += 1

                            if current_review_count >= self.num_reviews:
                                break

                        except Exception as e:
                            print(f"Error parsing review: {e}")

                    # Move to the next page
                    try:
                        next_button = self.driver.find_element(By.CSS_SELECTOR, ".a-last a")
                        next_button.click()
                        time.sleep(3)  # Wait for the next page to load
                    except Exception:
                        print("No more pages available.")
                        break
        except Exception as e:
            print(f"An error occurred: {e}")
        finally:
            if self.driver:
                self.driver.quit()

        return reviews_data
    
    # def filter_reviews(self):
    #     url = self.url
    #     url = self._get_reviews_url(url)
        
    #     base_url, _, _ = url.partition("&sortBy")
    #     base_url, _, _ = base_url.partition("&pageNumber")
        
    #     if "&pageNumber" not in url:
    #         base_url += "&pageNumber=1"
        
    #     return [
    #         base_url+"&sortBy=helpful", 
    #         base_url+"&sortBy=recent"
    #     ]

    def _login(self): 
        # Login Workflow
        WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((By.ID, "ap_email")))
        email_input = self.driver.find_element(By.ID, "ap_email")
        self.humantype(email_input, self.credentials.email)
        email_input.submit()

        WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((By.ID, "ap_password")))
        password_input = self.driver.find_element(By.ID, "ap_password")
        self.humantype(password_input, self.credentials.password)
        password_input.submit()
    def _handle_cookies(self): 
        acpt_btn = WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.ID, "sp-cc-accept"))
        )
        acpt_btn.click()
    #data-hook="see-all-reviews-link-foot"
    # def _get_reviews_url(self, url) -> str:
    #     cur_url = ""
    #     try:
    #         self.initialize_driver()
    #         self.driver.get(url)
    #         self._handle_cookies()
    #         reveiw_link = WebDriverWait(self.driver, 10).until(
    #             EC.presence_of_element_located((By.CSS_SELECTOR, "a[data-hook='see-all-reviews-link-foot']"))
    #         )
    #         reveiw_link.click()
    #         time.sleep(2)
    #         self._login()
    #         time.sleep(15)
    #         cur_url = self.driver.current_url
    #     except Exception as e:
    #         # strang ANSI in the terminal make the text red and bold
    #             print(f"\n\n{e}\n\033[31;1;4mTo use Firefox, go into ./scrapper/amz_scrape.py and please change the path to the geckodriver, otherwise use Chrome.\n\033[0m") 
    #     finally:
    #         if self.driver:
    #             self.driver.quit()
    #     if cur_url:
    #         return cur_url
    #     return ""

        

    
        
