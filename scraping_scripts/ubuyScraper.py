from bs4 import BeautifulSoup
import random
import time
from datetime import datetime
import pandas as pd
import re
import logging
import os
from scraping_scripts.headers import headers, user_agents
from scraping_scripts.utils import get_with_retries

# base_url = "https://www.ubuy.ma"

#Tracks categories to prevent redundant CSV headers.
processed_categories = set()

is_error = False

# extracts a single product data and saves it
def extract_and_save_data(html: str, category: str):
    print("new product to extract")
    global processed_categories
    soup = BeautifulSoup(html, "html.parser")
    title = soup.select_one("h1[class='title']")
    title = title.text.strip() if title else None

    # Exclude irrelevant products in the "tablets" category
    if title and not (category == "tablets" and not re.search("pad|tab", title, re.IGNORECASE)):
        price = soup.select_one("[class='-b -ubpt -tal -fs24 -prxs']")
        price = price.text.strip() if price else None

        # discount = soup.select_one("[class='price-box'] > h2[class='me-3']")
        discount = None
        discount = "discount" if discount else "no discount"

        df = pd.DataFrame([{
            "name": title,
            "price": price,
            "website": "ubuy",
            "category": category,
            "scraping_date": datetime.now().date(),
            "promotion": discount,
        }])
        header = not (category in processed_categories)
        df.to_csv(f"data/ubuy_{category}.csv", index=False, mode="a", header=header)
        processed_categories.add(category) # ensure headers are only written once


def scrape_data(url: str, headers: dict, category: str):
    global is_error

    page_number = 1
    visited_urls = set()

    # Load previously visited URLs (if available)
    if os.path.exists("cache/ubuy_visited_urls.txt"):
        with open("cache/ubuy_visited_urls.txt", "r") as f:
            visited_urls = set(map(lambda url: url.strip("\n"), f.readlines()))

    while True:
        try:
            response = get_with_retries(url, headers=headers)
            if response.status_code != 200:
                is_error = True
                print(f"Error fetching {url}: Status code {response.status_code}")
                break
            
            soup = BeautifulSoup(response.text, "html.parser")

            products_list = soup.select_one('[id="usstore-products"]')
            # products_list = products_list if products_list else soup.select_one("[class='prd-w col8 row _2c -paxs']")
            if not products_list:
                # logging.error(soup.prettify())  # Print the first 1000 characters of the response
                print(f"No products found on page {page_number} for {category} - {url=}")
                break

            products_cards = products_list.select('[class="product-card mb-0 rounded-0 h-100 d-flex d-sm-block"]')

            # a_tags = products_list.select('a')
            headers["Referer"] = url  # Update Referer header
            
            for product_card in products_cards:
                a_tag = product_card.select_one("a")
                a_tag_href = a_tag.get("href") if a_tag else None
                a_tag_href = a_tag_href.strip() if a_tag_href else ""

                if not a_tag_href.startswith("https://www.ubuy.ma/en/product"):
                    continue

                if a_tag_href in visited_urls:
                    print(f"Skipping already visited page: {url}")
                    continue

                time.sleep(random.uniform(4, 8))
                headers["User-Agent"] = random.choice(user_agents)
                page = get_with_retries(a_tag_href, headers=headers)
                if page.status_code == 200:
                    visited_urls.add(a_tag_href)
                    extract_and_save_data(html=page.text, category=category)

            # Move to the next page
            page_number += 1
            url = url.replace(f"?page={page_number-1}", f"?page={page_number}")

        except Exception as e:
            is_error = True
            current_time = datetime.now()
            print(f"Error while scraping ubuy, page {page_number} of {category}:")
            print(e)
            logging.error(f"{current_time} : Error on page {page_number} of {category}: {url}:")
            logging.error(e)
            break

    # Save visited URL
    with open("cache/ubuy_visited_urls.txt", "a") as f:
        f.writelines(f"{url}\n" for url in visited_urls)


def main():
    logging.basicConfig(filename="logs/ubuy_scraping_errors.log", level=logging.ERROR)

    categories = {
        "smartphones": "https://www.ubuy.ma/en/category/mobile-phones-21453?ref=hm-explore-category&page=1",
        # "laptops": "https://www.ubuy.ma/pc-portables/?page=1#catalog-listing",
        # "tablets": "https://www.ubuy.ma/tablettes-tactiles/?page=1#catalog-listing",
    }

    for category, url in categories.items():
        if os.path.exists(f"data/ubuy_{category}.csv"): # if file exists:
            with open(f"data/ubuy_{category}.csv", mode="r") as file:
                if file.read(1): # if file is not empty
                    # ensure that the headers are not written to the csv file as it is not empty
                    processed_categories.add(category)

        scrape_data(url, headers=headers, category=category)
        print(f"scraping data finished for category '{category}' in ubuy")

    print("scraping data finished for ubuy")
    
    # if no error, then the scraping finished successfully, truncate the cache/ubuy_visited_urls.txt
    if not is_error:
        with open("cache/ubuy_visited_urls.txt", "w") as f:
            pass

if __name__ == "__main__":
    if not os.path.exists("./data"):
        os.mkdir("./data")

    if not os.path.exists("./cache"):
        os.mkdir("./cache")

    main()
