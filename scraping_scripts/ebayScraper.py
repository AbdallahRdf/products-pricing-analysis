from bs4 import BeautifulSoup
import random
import time
from datetime import datetime
import logging
from concurrent.futures import ThreadPoolExecutor
import os
from scraping_scripts.headers import headers, user_agents
from scraping_scripts.utils import get_with_retries, load_visited_urls, save_to_csv, save_visted_url

# extracts a single product data and saves it
def extract_data(html: str, category: str, data: list):
    soup = BeautifulSoup(html, "html.parser")

    brand = soup.select_one('[class="ux-labels-values ux-labels-values--inline col-6 ux-labels-values--brand"] > [class="ux-labels-values__values"]')
    if not brand:
        brand = soup.select_one('[class="ux-labels-values col-6 ux-labels-values--marque"] > [class="ux-labels-values__values"]')
    if not brand:
        brand = soup.select_one('[class="ux-labels-values ux-labels-values--inline col-6 ux-labels-values--marke"] > [class="ux-labels-values__values"]')
    if not brand:
        brand = soup.select_one('[class="ux-labels-values ux-labels-values--inline col-6 ux-labels-values--marca"] > [class="ux-labels-values__values"]')
    brand = brand.text.strip() if brand else None

    model = soup.select_one('[class="ux-labels-values ux-labels-values--inline col-6 ux-labels-values--model"] > [class="ux-labels-values__values"]')
    if not model:
        model = soup.select_one('[class="ux-labels-values col-6 ux-labels-values__column-last-row ux-labels-values--modèle"] > [class="ux-labels-values__values"]')
    if not model:
        model = soup.select_one('[class="ux-labels-values ux-labels-values--inline col-6 ux-labels-values--modell"] > [class="ux-labels-values__values"]')
    if not model:
        model = soup.select_one('[class="ux-labels-values ux-labels-values--inline col-6 ux-labels-values--modello"] > [class="ux-labels-values__values"]')
    model = model.text.strip() if model else None
    
    screen_size = soup.select_one('[class="ux-labels-values ux-labels-values--inline col-6 ux-labels-values--screenSize"] > [class="ux-labels-values__values"]')
    if not screen_size:
        screen_size = soup.select_one('[class="ux-labels-values ux-labels-values--inline col-6 ux-labels-values--itemWidth"] > [class="ux-labels-values__values"]')
    if not screen_size:
        screen_size = soup.select_one('[class="ux-labels-values col-6 ux-labels-values--tailleD\'écran"] > [class="ux-labels-values__values"]')
    if not screen_size:
        screen_size = soup.select_one('[class="ux-labels-values ux-labels-values--inline col-6 ux-labels-values__column-last-row ux-labels-values--bildschirmgröße"] > [class="ux-labels-values__values"]')
    if not screen_size:
        screen_size = soup.select_one('[class="ux-labels-values ux-labels-values--inline col-6 ux-labels-values--dimensioniSchermo"] > [class="ux-labels-values__values"]')
    screen_size = screen_size.text.strip() if screen_size else None

    processor = soup.select_one('[class="ux-labels-values ux-labels-values--inline col-6 ux-labels-values--processor"] > [class="ux-labels-values__values"]')
    if not processor:
        processor = soup.select_one('[class="ux-labels-values col-6 ux-labels-values--processeur"] > [class="ux-labels-values__values"]')
    if not processor:
        processor = soup.select_one('[class="ux-labels-values ux-labels-values--inline col-6 ux-labels-values--prozessor"] > [class="ux-labels-values__values"]')
    if not processor:
        processor = soup.select_one('[class="ux-labels-values ux-labels-values--inline col-6 ux-labels-values--processore"] > [class="ux-labels-values__values"]')
    processor = processor.text.strip() if processor else None

    ram = soup.select_one('[class="ux-labels-values ux-labels-values--inline col-6 ux-labels-values--ram"] > [class="ux-labels-values__values"]')
    if not ram:
        ram = soup.select_one('[class="ux-labels-values ux-labels-values--inline col-6 ux-labels-values__column-last-row ux-labels-values--ram"] > [class="ux-labels-values__values"]')
    if not ram:
        ram = soup.select_one('[class="ux-labels-values ux-labels-values--inline col-6 ux-labels-values--ramSize"] > [class="ux-labels-values__values"]')
    if not ram:
        ram = soup.select_one('[class="ux-labels-values ux-labels-values--inline col-6 ux-labels-values__column-last-row ux-labels-values--arbeitsspeichergröße"] > [class="ux-labels-values__values"]')
    if not ram:
        ram = soup.select_one('[class="ux-labels-values ux-labels-values--inline col-6 ux-labels-values--memoriaRam"] > [class="ux-labels-values__values"]')
    ram = ram.text.strip() if ram else None

    storage = soup.select_one('[class="ux-labels-values ux-labels-values--inline col-6 ux-labels-values--storageCapacity"] > [class="ux-labels-values__values"]')
    if not storage:
        storage = soup.select_one('[class="ux-labels-values ux-labels-values--inline col-6 ux-labels-values__column-last-row ux-labels-values--storageCapacity"] > [class="ux-labels-values__values"]')
    if not storage:
        storage = soup.select_one('[class="ux-labels-values ux-labels-values--inline col-6 ux-labels-values--hardDriveCapacity"] > [class="ux-labels-values__values"]')
    if not storage:
        storage = soup.select_one('[class="ux-labels-values ux-labels-values--inline col-6 ux-labels-values--ssdCapacity"] > [class="ux-labels-values__values"]')
    if not storage:
        storage = soup.select_one('[class="ux-labels-values ux-labels-values--inline col-6 ux-labels-values__column-last-row ux-labels-values--storageCapacity"] > [class="ux-labels-values__values"]')
    if not storage:
        storage = soup.select_one('[class="ux-labels-values col-6 ux-labels-values--capacitéDeStockage"] > [class="ux-labels-values__values"]')
    if not storage:
        storage = soup.select_one('[class="ux-labels-values ux-labels-values--inline col-6 ux-labels-values__column-last-row ux-labels-values--speicherkapazität"] > [class="ux-labels-values__values"]')
    if not storage:
        storage = soup.select_one('[class="ux-labels-values ux-labels-values--inline col-6 ux-labels-values--capacitàDiMemorizzazione"] > [class="ux-labels-values__values"]')
    storage = storage.text.strip() if storage else None

    price = soup.select_one('[data-testid="x-price-primary"]')
    price = price.text.strip() if price else None

    discount = soup.select_one('[class="vim d-sme-atf"]')
    discount = "discount" if discount else "no discount"

    data.append({
        "brand": brand,
        "model": model,
        "screen_size": screen_size,
        "processor": processor,
        "ram": ram,
        "storage": storage,
        "price": price,
        "website": "ebay",
        "category": category,
        "scraping_date": datetime.now().date(),
        "promotion": discount,
    })


def scrape_data(url: str, headers: dict, category: str, max_pages: int, processed_categories: set) -> bool:
    is_error = False
    data = []   

    page_number = 1
    visited_urls = load_visited_urls(file_path=f"cache/ebay_visited_{category}_urls.txt")

    while True:
        try:
            response = get_with_retries(url, headers=headers)
            if response.status_code != 200:
                is_error = True
                print(f"Error fetching {url}: Status code {response.status_code}")
                break
            
            soup = BeautifulSoup(response.text, "html.parser")
            products_list = soup.select_one('[class="srp-results srp-list clearfix"]')

            if not products_list:
                print(f"No products found on page {page_number} for {category} - {url=}")
                break

            a_tags = products_list.select('ul a[class="s-item__link"]')
            headers["Referer"] = url  # Update Referer header
            
            for a_tag in a_tags:
                a_tag_href = a_tag.get("href").strip()

                if a_tag_href in visited_urls:
                    print(f"Skipping already visited page: {a_tag_href}")
                    continue

                time.sleep(random.uniform(4, 8))
                headers["User-Agent"] = random.choice(user_agents)
                page = get_with_retries(a_tag_href, headers=headers)
                if page.status_code == 200:
                    visited_urls.add(a_tag_href)
                    extract_data(html=page.text, category=category, data=data)

            save_to_csv(file_path=f"data/ebay_{category}.csv", data=data, category=category, processed_categories=processed_categories)
            save_visted_url(file_path=f"cache/ebay_visited_{category}_urls.txt", visited_urls=visited_urls)

            # Move to the next page
            page_number += 1
            if page_number > max_pages:
                break
            url = url.replace(f"_pgn={page_number-1}", f"_pgn={page_number}")

        except Exception as e:
            save_to_csv(file_path=f"data/ebay_{category}.csv", data=data, category=category, processed_categories=processed_categories)
            save_visted_url(file_path=f"cache/ebay_visited_{category}_urls.txt", visited_urls=visited_urls)
            is_error = True
            current_time = datetime.now()
            print(f"Error while scraping ebay, page {page_number} of {category}:")
            print(e)
            logging.error(f"{current_time} : Error on page {page_number} of {category}: {url}:")
            logging.error(e)
            break
            
    return is_error


def scrape_wrapper(target: dict, processed_categories: set) -> bool:
    print(f"scraping data started for category {target['category']} in ebay")

    error = scrape_data(
        url=target["url"], 
        headers=headers, 
        category=target['category'], 
        max_pages=target["max_pages"], 
        processed_categories=processed_categories
    )

    if not error:
        print(f"scraping data finished for category {target['category']} in ebay")
    else:
        print(f"something went worng when scraping data for category {target['category']} in ebay, please check log and cache files")

    return error


def main():
    #Tracks categories to prevent redundant CSV headers.
    processed_categories = set()

    errors = []

    logging.basicConfig(filename="logs/ebay_scraping_errors.log", level=logging.ERROR)

    targets = [
        {
            "category": "smartphones",
            "url": "https://www.ebay.com/sch/i.html?_nkw=smartphones&_sacat=0&_from=R40&_pgn=1",
            "max_pages": 6,
        },
        {
            "category": "laptops",
            "url": "https://www.ebay.com/sch/i.html?_nkw=laptops&_sacat=0&_from=R40&_pgn=1",
            "max_pages": 6,
        },
        {
            "category": "tablets",
            "url": "https://www.ebay.com/sch/i.html?_nkw=tablets&_sacat=0&_from=R40&_pgn=1",
            "max_pages": 6,
        }
    ]

    for target in targets:
        if os.path.exists(f"data/ebay_{target['category']}.csv"): # if file exists:
            with open(f"data/ebay_{target['category']}.csv", mode="r") as file:
                if file.read(1): # if file is not empty
                    # ensure that the headers are not written to the csv file as it is not empty
                    processed_categories.add(target['category'])

    # Use ThreadPoolExecutor to run scraping in parallel
    with ThreadPoolExecutor(max_workers=3) as executer:
        futures = [executer.submit(scrape_wrapper, target, processed_categories) for target in targets]

        for future in futures:
            errors.append(future.result())

        
    # if no error, then the scraping finished successfully, truncate the cache/ebay_visited_urls.txt
    if not any(errors):
        for target in targets:
            if os.path.exists(f"cache/ebay_visited_{target['category']}_urls.txt"):
                with open(f"cache/ebay_visited_{target['category']}_urls.txt", "w") as f:
                    pass
    
    print("scraping data finished for ebay")


if __name__ == "__main__":
    if not os.path.exists("./data"):
        os.mkdir("./data")

    if not os.path.exists("./cache"):
        os.mkdir("./cache")
        
    if not os.path.exists("./logs"):
            os.mkdir("./logs")
    main()
