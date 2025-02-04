from selenium import webdriver
from bs4 import BeautifulSoup
import random
import time
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime
import logging
from dotenv import load_dotenv
import os
from scraping_scripts.headers import headers
from scraping_scripts.utils import load_visited_urls, save_to_csv, save_visted_url, get_with_retries

# extracts a single product data and saves it
def extract_data(html: str, category: str, data: list):
    soup = BeautifulSoup(html, "html.parser")

    rows = soup.select("#pdp__specification > section > ul > div")

    # Initialize variables with default values
    brand = model = processor = ram = storage = None    

    columns = {}
    for row in rows:
        cols = list(row.children)
        if len(cols) == 2:
            key = cols[0].text.strip()
            value = cols[1].text.strip()
            columns[key] = value

    brand = columns.get("Brand")
    model = columns.get("Model") or columns.get("Series")
    if columns.get("Series") and columns.get("Model"):
        model = f"{columns.get('Series')} {columns.get('Model')}"
    ram = columns.get("Memory (RAM)")
    storage = columns.get("Hard Drive") or columns.get("Internal Storage")
    processor = columns.get("Processor")

    discount = soup.select_one("li[class='pdp__priceSection__priceListText']:nth-child(2) > .TextWeb__Text-sc-1cyx778-0")
    if not discount:
        discount = soup.select_one("li[class='pdp__priceSection__priceListText']:nth-child(3) > .TextWeb__Text-sc-1cyx778-0")


    price = soup.select_one("li[class='pdp__priceSection__priceListText']:nth-child(1) > .TextWeb__Text-sc-1cyx778-0")
    price = price.text.strip() if price else None

    data.append({
        "brand": brand,
        "model": model,
        "processor": processor,
        "ram": ram,
        "storage": storage,
        "price": price,
        "website": "reliancedigital",
        "category": category,
        "scraping_date": datetime.now().date(),
        "promotion": "discount" if discount else "no discount"
    })


def scrape_data(driver: object, url: str, category: str, proxies: list, max_pages: int, processed_categories: set) -> bool:
    data = []
    is_error = False
    page_number = 0
    visited_urls = load_visited_urls(file_path=f"cache/reliancedigital_visited_{category}_urls.txt")

    base_url = "https://www.reliancedigital.in"

    while page_number < max_pages:
        try:
            driver.get(url)
            time.sleep(5)

            soup = BeautifulSoup(driver.page_source, "html.parser")

            products_links = soup.select(".pl__container > ul > li > div > a")

            for product_link in products_links:
                link = f"{base_url}{product_link.get('href').strip()}" if product_link.get("href") else None
                # retry 5 times to get the product details
                if link in visited_urls:
                    continue
                
                headers["Referer"] = base_url  # Update Referer header
                for _ in range(5):
                    try:
                        response = get_with_retries(url=link, headers=headers, proxies=proxies, withProxy=True)
                        time.sleep(random.uniform(2, 4))
                        visited_urls.add(link)
                        extract_data(html=response.text, category=category, data=data)
                        break
                    except Exception as e:
                        pass

            save_to_csv(file_path=f"data/reliancedigital_{category}.csv", data=data, category=category, processed_categories=processed_categories)
            save_visted_url(file_path=f"cache/reliancedigital_visited_{category}_urls.txt", visited_urls=visited_urls)
            
            # Move to the next page
            page_number += 1
            url = url.replace(f"&page={page_number-1}", f"&page={page_number}")
        
        except Exception as e:
            save_to_csv(file_path=f"data/reliancedigital_{category}.csv", data=data, category=category, processed_categories=processed_categories)
            save_visted_url(file_path=f"cache/reliancedigital_visited_{category}_urls.txt", visited_urls=visited_urls)
            is_error = True
            current_time = datetime.now()
            print(f"Error while scraping reliancedigital, page {page_number} of {category}:")
            print(e)
            logging.error(f"{current_time} : Error on page {page_number} of {category}: {url}:")
            logging.error(e)
            break 
    
    return is_error


def scrape_wrapper(target: dict, proxies: list, processed_categories: set) -> bool:
    options = webdriver.ChromeOptions()
    options.add_argument("--headless=new")
    driver = webdriver.Chrome(options=options)

    print(f"scraping data started for category '{target['category']}' in reliance digital")

    error = scrape_data(
        driver=driver, 
        url=target["url"], 
        category=target["category"], 
        proxies=proxies, 
        max_pages=target["max_pages"], 
        processed_categories=processed_categories
    )

    driver.quit()

    if error:
        print(f"something went worng when scraping data for category {target['category']} in reliance digital, please check log and cache files")
    else:
        print(f"scraping data finished for category {target['category']} in reliance digital")

    return error


def main():
    #Tracks categories to prevent redundant CSV headers.
    processed_categories = set()

    errors = []

    load_dotenv()

    # Access environment variable
    proxies = [
        os.getenv("PROXY_1"),
        os.getenv("PROXY_2"),
        os.getenv("PROXY_3"),
        os.getenv("PROXY_4"),
        os.getenv("PROXY_5"),
        os.getenv("PROXY_6"),
        os.getenv("PROXY_7"),
        os.getenv("PROXY_8"),
    ]

    logging.basicConfig(filename="logs/reliancedigital_scraping_errors.log", level=logging.ERROR)

    targets = [
        {
            "category": "smartphones",
            "url": "https://www.reliancedigital.in/smartphones/c/S101711?searchQuery=:relevance&page=0",
            "max_pages": 9
        },
        {
            "category": "laptops",
            "url": "https://www.reliancedigital.in/laptops/c/S101210?searchQuery=:relevance:availability:Exclude%20out%20of%20Stock&page=0",
            "max_pages": 9
        },
        {
            "category": "tablets",
            "url": "https://www.reliancedigital.in/tablets/c/S101712?searchQuery=:relevance&page=0",
            "max_pages": 9
        }
    ]

    for target in targets:
        if os.path.exists(f"data/reliancedigital_{target['category']}.csv"): # if file exists:
            with open(f"data/reliancedigital_{target['category']}.csv", mode="r") as file:
                if file.read(1): # if file is not empty
                    # ensure that the headers are not written to the csv file as it is not empty
                    processed_categories.add(target["category"])

    # Use ThreadPoolExecutor to run scraping in parallel
    with ThreadPoolExecutor(max_workers=3) as executer:
        futures = [executer.submit(scrape_wrapper, target, proxies, processed_categories) for target in targets]

        for future in futures:
            errors.append(future.result())
        
    # if no error, then the scraping finished successfully, truncate the cache/reliancedigital_visited_urls.txt
    if not any(errors):
        for target in targets:
            if os.path.exists(f"cache/reliancedigital_visited_{target['category']}_urls.txt"):
                with open(f"cache/reliancedigital_visited_{target['category']}_urls.txt", "w") as f:
                    pass
    
    print("scraping data finished for reliance digital")


if __name__ == "__main__":
    if not os.path.exists("./data"):
        os.mkdir("./data")

    if not os.path.exists("./cache"):
        os.mkdir("./cache")

    if not os.path.exists("./logs"):
        os.mkdir("./logs")

    main()
