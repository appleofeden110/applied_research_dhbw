import json
import sys
import os
from csv import DictWriter
from typing import List
from amz_scrape import AmazonScraper, AmazonCredentials
from mm_scrape import MediaMarktScrapper
from review import Review


def write_review_csv(prod_name: str, reviews: List, filename=f"unnamed_source"):
    try:
        fieldnames = ['id', 'prod_name', 'price', 'country',
                      'source', 'author', 'review_txt', 'rating']
        print("Creating the CSV directory if it didn't exist before...")
        csv_dir = os.path.abspath("csv/")
        os.makedirs(csv_dir, exist_ok=True)

        sanitized_prod_name = prod_name[:25].replace(
            "/", " ").replace('"', "").replace("\\", "")
        file_path = os.path.join(csv_dir, f"{filename}_{
                                 sanitized_prod_name}.csv")

        with open(file_path, mode="a+", encoding="UTF-8", newline="") as f:
            is_empty = os.stat(file_path).st_size == 0
            writer = DictWriter(f, fieldnames=fieldnames)

            if is_empty:
                writer.writeheader()

            for i, review in enumerate(reviews, start=1):
                review_dict = review.to_dict()  # Ensure `review` has a `to_dict()` method
                review_dict['id'] = i
                writer.writerow(review_dict)

        print(f"Successfully wrote reviews to {file_path}")
    except Exception as e:
        print(f"ERROR: {e}")


def which(choices: List[str], choice_type: str) -> str:
    print(f"\n\nchoose {choice_type}?: \n")
    i = 0
    for choice in choices:
        print(f"\t{i+1}.{choice}")
        i += 1
    return choices[int(input("\npick a number to choose: "))-1]

def authJsonLookup() -> tuple[bool, AmazonCredentials]:
    try:
        authPath = os.getcwd() + "/auth/auth.json"
        print(authPath)
        print("Trying to look for ../auth/auth.json file for auth...")     
        
        with open(authPath, "r", encoding="utf-8") as f:  
            data = json.load(f) 
            return True, AmazonCredentials(data["email"], data["password"]) 
    
    except FileNotFoundError:
        print("Could not find auth, taking manual auth cred:")
        return False, AmazonCredentials("", "")
    
    except json.JSONDecodeError as e:
        print(f"Error: Invalid JSON format in {authPath}, message: {e}")
        return False, AmazonCredentials("", "")

def main():
    if len(sys.argv) < 3:
        print("Usage: python scapper.py [-a|-m] [site_url]")
        exit(4)
    reviews = ""
    prod_name = ""
    browser = which(["Firefox", "Chrome"], "browser")
    if sys.argv[1] == "-a":
        print("Credential information is not stored anywhere, as you can see by the bare inputs in the code")
        isFound, amz_cred = authJsonLookup()
        if isFound != True:
            print("Could not find auth, taking manual auth cred:")
            amz_cred.email, amz_cred.password = input("write your amazon email here (required for the scrapping): "), input("write your amazon password: ")
        
        
        
        scrapper = AmazonScraper(browser, "amazon", 700, sys.argv[2], amz_cred)
        
        reviews, prod_name = scrapper.scrape_amazon_reviews() 
        write_review_csv(prod_name, reviews, "amazon")
        print("Done!")
    elif sys.argv[1] == "-m":
        scrapper = MediaMarktScrapper(browser, "media_markt", 20, sys.argv[2])
        reviews, prod_name = scrapper.scrape_reviews_mm()
        write_review_csv(prod_name, reviews, "media_markt")


if __name__ == "__main__":
    main()
