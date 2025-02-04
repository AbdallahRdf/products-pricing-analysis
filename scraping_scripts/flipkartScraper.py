from bs4 import BeautifulSoup
import random
import time
from datetime import datetime
import logging
from concurrent.futures import ThreadPoolExecutor
import os
import re
from scraping_scripts.headers import headers
from scraping_scripts.utils import get_with_retries, load_visited_urls, save_to_csv, save_visted_url

def extract_smartphone_data(soup: BeautifulSoup) -> dict:
        processor = ram = storage = None

        pattern = re.compile(r'(\d+\s*GB)?\s*RAM\s*\|?\s*(\d+\s*GB)?\s*ROM')
        match = pattern.match(soup.select_one("li:nth-child(1)").text)
        if match:
            ram = match.group(1).strip() if match.group(1) else None
            storage = match.group(2).strip() if match.group(2) else None

        for soup in list(soup.select("li")):
            if "Processor" in soup.text:
                processor = soup.text.replace("Processor", "").strip()

        return {"processor": processor, "ram": ram, "storage": storage}


def extract_laptop_data(soup: BeautifulSoup) -> dict:
    processor = ram = storage = None

    processor = soup.select_one("li:nth-child(1)")
    processor = processor.text.strip() if processor else None

    pattern = re.compile(r'(\d+\s*GB)?')
    match = pattern.match(soup.select_one("li:nth-child(2)").text)
    if match:
        ram = match.group(1).strip() if match.group(1) else None

    match = pattern.match(soup.select_one("li:nth-child(4)").text)
    if match:
        storage = match.group(1).strip() if match.group(1) else None

    return {"processor": processor, "ram": ram, "storage": storage} 


def extract_tablet_data(soup: BeautifulSoup) -> dict:
    processor = ram = storage = None

    memories = soup.select_one("li:nth-child(1)").text.split("|")
    for memory in memories:
        if "RAM" in memory:
            ram = memory.replace("RAM", "").strip()
        elif "ROM" in memory:
            storage = memory.replace("ROM", "").strip()

    for li in list(soup.select("li")):
        if "Processor" in li.text:
            processor = li.text.replace("Processor:", "").strip()

    return {"processor": processor, "ram": ram, "storage": storage}


# extracts a single product data and saves it
def extract_data(soup: BeautifulSoup, category: str, data: list):
    
    products = soup.select("[class='DOjaWF gdgoEp'] > [class='cPHDOP col-12-12'] > div > div > div > a > [class='yKfJKb row']")

    for product in products:
        brand = model = price = discount = None

        title = product.select_one('.KzDlHZ')
        pattern = re.compile(r'^(.*?)\s+([\w\d]+\s*[\w\d]*)\s')
        match = pattern.match(title.text)
        if match:
            brand = match.group(1).strip()
            model = match.group(2).strip()

        price = product.select_one("[class='Nx9bqj _4b5DiR']")
        price = price.text.strip() if price else None

        discount = product.select_one("[class='yRaY8j ZYYwLA']")
        discount = "discount" if discount else "no discount"

        details = product.select_one(".G4BRas")

        result = dict()

        if category == "smartphones":
            result = extract_smartphone_data(soup=details)
        elif category == "laptops":
            result = extract_laptop_data(soup=details)
        else:
            result = extract_tablet_data(soup=details)

        data.append({
            "brand": brand,
            "model": model,
            "processor": result.get("processor"),
            "ram": result.get("ram"),
            "storage": result.get("storage"),
            "price": price,
            "website": "flipkart",
            "category": category,
            "scraping_date": datetime.now().date(),
            "promotion": discount,
        })


def scrape_data(url: str, headers: dict, category: str, max_pages: int, processed_categories: set) -> bool: 
    is_error = False
    data = []   

    base_url = "https://www.flipkart.com"
    headers["Referer"] = base_url  # Update Referer header

    page_number = 1
    visited_urls = load_visited_urls(file_path=f"cache/flipkart_visited_{category}_urls.txt")

    user_agents = [
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/94.0.4606.81 Safari/537.36",
    ]

    while page_number <= max_pages:
        try:
            headers["User-Agent"] = random.choice(user_agents)
            response = get_with_retries(url, headers=headers, withProxy=False)
            if response.status_code != 200:
                is_error = True
                print(f"Error fetching {url}: Status code {response.status_code}")
                break
            
            soup = BeautifulSoup(response.text, "html.parser")
            products_list = soup.select_one("[class='DOjaWF gdgoEp']")

            if not products_list:
                print(f"No products found on page {page_number} for {category} - {url=}")
                break

            extract_data(soup=soup, category=category, data=data)

            save_to_csv(file_path=f"data/flipkart_{category}.csv", data=data, category=category, processed_categories=processed_categories)
            save_visted_url(file_path=f"cache/flipkart_visited_{category}_urls.txt", visited_urls=visited_urls)

            # Move to the next page
            page_number += 1
            headers["Referer"] = url  # Update Referer header
            url = url.replace(f"&page={page_number-1}", f"&page={page_number}")
            time.sleep(random.uniform(4, 8))

        except Exception as e:
            save_to_csv(file_path=f"data/flipkart_{category}.csv", data=data, category=category, processed_categories=processed_categories)
            save_visted_url(file_path=f"cache/flipkart_visited_{category}_urls.txt", visited_urls=visited_urls)
            is_error = True
            current_time = datetime.now()
            print(f"Error while scraping flipkart, page {page_number} of {category}:")
            print(e)
            logging.error(f"{current_time} : Error on page {page_number} of {category}: {url}:")
            logging.error(e)
            break
            
    return is_error


def scrape_wrapper(target: dict, processed_categories: set) -> bool:
    print(f"scraping data started for category {target['category']} in flipkart")

    error = scrape_data(
        url=target["url"], 
        headers=headers, 
        category=target['category'], 
        max_pages=target["max_pages"], 
        processed_categories=processed_categories
    )

    if not error:
        print(f"scraping data finished for category {target['category']} in flipkart")
    else:
        print(f"something went worng when scraping data for category {target['category']} in flipkart, please check log and cache files")

    return error


def main():
    #Tracks categories to prevent redundant CSV headers.
    processed_categories = set()

    errors = []

    logging.basicConfig(filename="logs/flipkart_scraping_errors.log", level=logging.ERROR)

    targets = [
        {
            "category": "smartphones",
            "url": "https://www.flipkart.com/search?q=smartphones&otracker=search&otracker1=search&marketplace=FLIPKART&as-show=off&as=off&page=1",
            "max_pages": 8,
        },
        {
            "category": "laptops",
            "url": "https://www.flipkart.com/search?q=laptops&otracker=search&otracker1=search&marketplace=FLIPKART&as-show=on&as=off&page=1",
            "max_pages": 10,
        },
        {
            "category": "tablets",
            "url": "https://www.flipkart.com/search?q=tablets&otracker=search&otracker1=search&marketplace=FLIPKART&as-show=on&as=off&page=1",
            "max_pages": 8,
        }
    ]

    for target in targets:
        if os.path.exists(f"data/flipkart_{target['category']}.csv"): # if file exists:
            with open(f"data/flipkart_{target['category']}.csv", mode="r") as file:
                if file.read(1): # if file is not empty
                    # ensure that the headers are not written to the csv file as it is not empty
                    processed_categories.add(target['category'])

    # Use ThreadPoolExecutor to run scraping in parallel
    with ThreadPoolExecutor(max_workers=3) as executer:
        futures = [executer.submit(scrape_wrapper, target, processed_categories) for target in targets]

        for future in futures:
            errors.append(future.result())

        
    # if no error, then the scraping finished successfully, truncate the cache/flipkart_visited_urls.txt
    if not any(errors):
        for target in targets:
            cache_file = f"cache/flipkart_visited_{target['category']}_urls.txt"
            if os.path.exists(cache_file):
                os.remove(cache_file)
    
    print("scraping data finished for flipkart")


if __name__ == "__main__":
    if not os.path.exists("./data"):
        os.mkdir("./data")

    if not os.path.exists("./cache"):
        os.mkdir("./cache")
        
    if not os.path.exists("./logs"):
            os.mkdir("./logs")
    main()
