import sys
import os
from csv import DictWriter
from typing import List
from crawler import scrape_reviews


def write_review_csv(prod_name: str, reviews: List, filename=f"unnamed_source"):
    try:
        fieldnames = ['id', 'prod_name', 'price', 'country', 'source', 'author', 'review_txt', 'rating']
        print("Creating the CSV directory if it didn't exist before...")
        os.makedirs("../csv/", exist_ok=True)

        sanitized_prod_name = prod_name[:25].replace("/", " ").replace('"', "").replace("\\", "")
        file_path = f"../csv/{filename}_{sanitized_prod_name}.csv"
        
        with open(file_path, mode="a+", encoding="UTF-8", newline="") as f:
            writer = DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            i=0
            for review in reviews:
                i+=1
                review.id = i
                writer.writerow(review.to_dict())
    except Exception as e:
        print(f"ERROR: {e}")
    finally:
        return 

def main():
    reviews = ""
    
    if len(sys.argv) < 2:
        print("Usage: python scapper.py [site_url]");
        exit(4);
    else:
        reviews, prod_name = scrape_reviews(sys.argv[1], 50)
        write_review_csv(prod_name, reviews, "media_markt")
    
if __name__ == "__main__":
    main()