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

base_url = "https://www.jumia.ma"

#Tracks categories to prevent redundant CSV headers.
processed_categories = set()

is_error = False

# extracts a single product data and saves it
def extract_and_save_data(html: str, category: str):
    global processed_categories
    soup = BeautifulSoup(html, "html.parser")
    title = soup.select_one("h1[class='-fs20 -pts -pbxs']")
    title = title.text.strip() if title else None

    # Exclude irrelevant products in the "tablets" category
    if title and not (category == "tablets" and not re.search("pad|tab", title, re.IGNORECASE)):
        price = soup.select_one("[class='-b -ubpt -tal -fs24 -prxs']")
        price = price.text.strip() if price else None

        discount = soup.select_one("[class='bdg _dsct _dyn -mls']")
        discount = "discount" if discount else "no discount"

        df = pd.DataFrame([{
            "name": title,
            "price": price,
            "website": "jumia",
            "category": category,
            "scraping_date": datetime.now().date(),
            "promotion": discount,
        }])
        header = not (category in processed_categories)
        df.to_csv(f"data/jumia_{category}.csv", index=False, mode="a", header=header)
        processed_categories.add(category) # ensure headers are only written once


def scrape_data(url: str, headers: dict, category: str):
    global is_error

    page_number = 1
    visited_urls = set()

    # Load previously visited URLs (if available)
    if os.path.exists("cache/jumia_visited_urls.txt"):
        with open("cache/jumia_visited_urls.txt", "r") as f:
            visited_urls = set(map(lambda url: url.strip("\n"), f.readlines()))

    while True:
        try:
            response = get_with_retries(url, headers=headers)
            if response.status_code != 200:
                is_error = True
                print(f"Error fetching {url}: Status code {response.status_code}")
                break
            
            soup = BeautifulSoup(response.text, "html.parser")
            products_list = soup.select_one('section[class="card -fh"]')
            products_list = products_list if products_list else soup.select_one("[class='prd-w col8 row _2c -paxs']")
            if not products_list:
                # logging.error(soup.prettify())  # Print the first 1000 characters of the response
                print(f"No products found on page {page_number} for {category} - {url=}")
                break

            a_tags = products_list.select('a')
            headers["Referer"] = url  # Update Referer header
            
            for a_tag in a_tags:
                a_tag_href = a_tag.get("href").strip() if a_tag.get("href") else ""
                if not a_tag_href.endswith((".html", ".htm")):
                    continue

                current_url = f"{base_url}/{a_tag_href}"
                if current_url in visited_urls:
                    print(f"Skipping already visited page: {url}")
                    continue

                time.sleep(random.uniform(4, 8))
                headers["User-Agent"] = random.choice(user_agents)
                page = get_with_retries(current_url, headers=headers)
                if page.status_code == 200:
                    visited_urls.add(current_url)
                    extract_and_save_data(html=page.text, category=category)

            # Move to the next page
            page_number += 1
            url = url.replace(f"?page={page_number-1}", f"?page={page_number}")

        except Exception as e:
            is_error = True
            current_time = datetime.now()
            print(f"Error while scraping jumia, page {page_number} of {category}:")
            print(e)
            logging.error(f"{current_time} : Error on page {page_number} of {category}: {url}:")
            logging.error(e)
            break

    # Save visited URL
    with open("cache/jumia_visited_urls.txt", "a") as f:
        f.writelines(f"{url}\n" for url in visited_urls)


def main():
    logging.basicConfig(filename="logs/jumia_scraping_errors.log", level=logging.ERROR)

    categories = {
        "smartphones": "https://www.jumia.ma/telephones-smartphones/?page=1#catalog-listing",
        "laptops": "https://www.jumia.ma/pc-portables/?page=1#catalog-listing",
        "tablets": "https://www.jumia.ma/tablettes-tactiles/?page=1#catalog-listing",
    }

    for category, url in categories.items():
        if os.path.exists(f"data/jumia_{category}.csv"): # if file exists:
            with open(f"data/jumia_{category}.csv", mode="r") as file:
                if file.read(1): # if file is not empty
                    # ensure that the headers are not written to the csv file as it is not empty
                    processed_categories.add(category)

        scrape_data(url, headers=headers, category=category)
        print(f"scraping data finished for category '{category}' in jumia")

    print("scraping data finished for jumia")
    
    # if no error, then the scraping finished successfully, truncate the cache/jumia_visited_urls.txt
    if not is_error:
        with open("cache/jumia_visited_urls.txt", "w") as f:
            pass

if __name__ == "__main__":
    if not os.path.exists("./data"):
        os.mkdir("./data")

    if not os.path.exists("./cache"):
        os.mkdir("./cache")

    main()
