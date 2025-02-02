from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.proxy import Proxy, ProxyType
from bs4 import BeautifulSoup
import random
import time
from datetime import datetime
import logging
from dotenv import load_dotenv
import os
from scraping_scripts.headers import headers
from scraping_scripts.utils import load_visited_urls, save_to_csv, save_visted_url

# extracts a single product data and saves it
def extract_data(html: str, category: str, data: list):
    soup = BeautifulSoup(html, "html.parser")

    details_table = soup.select_one("#additional-info") 

    rows = details_table.select("tr")

    # Initialize variables with default values
    brand = model = screen_size = processor = ram = storage = None

    for row in rows:
        cols = row.find_all("td")
        if len(cols) == 2:
            key = cols[0].text.strip()
            value = cols[1].text.strip()
            match key:
                case "Brand":
                    brand = value
                case "Model Name":
                    model = value
                case "Screen Size":
                    screen_size = value
                case "RAM":
                    ram = value
                case "Ram Memory Installed Size":
                    ram = value
                case "Memory Storage Capacity": # for smartphones
                    storage = value
                case "Hard Disk Size": # for laptops
                    storage = value
                case "Processor":
                    processor = value
                case "CPU Model":
                    processor = value
    
    discount = soup.select_one('[class="product-old-price"]')

    price = soup.select_one('[class="price-box"] > h2')
    price = price.text.strip() if price else None
    
    data.append({
        "brand": brand,
        "model": model,
        "screen_size": screen_size,
        "processor": processor,
        "ram": ram,
        "storage": storage,
        "price": price,
        "website": "ubuy",
        "category": category,
        "scraping_date": datetime.now().date(),
        "promotion": "discount" if discount else "no discount"
    })


def scrape_data(driver: object, url: str, category: str, max_pages: int, processed_categories: set) -> bool:
    data = []
    is_error = False
    page_number = 1
    visited_urls = load_visited_urls(file_path=f"cache/ubuy_visited_{category}_urls.txt")

    while True:
        try:
            driver.get(url)

            wait = WebDriverWait(driver, 30)

            wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, "div[class='col-lg-3 col-md-4 col-sm-6 col-12 p-0 listing-product'] > div[class='product-card mb-0 rounded-0 h-100 d-flex d-sm-block'] > div[class='product-detail'] > a")))

            soup = BeautifulSoup(driver.page_source, "html.parser")

            products_links = soup.select("div[class='col-lg-3 col-md-4 col-sm-6 col-12 p-0 listing-product'] > div[class='product-card mb-0 rounded-0 h-100 d-flex d-sm-block'] > div[class='product-detail'] > a")

            for product_link in products_links:
                link = product_link.get("href").strip() if product_link.get("href") else None
                # retry 5 times to get the product details
                if link in visited_urls:
                    continue

                for _ in range(5):
                    try:
                        driver.get(link)
                        time.sleep(random.uniform(2, 4))
                        visited_urls.add(link)
                        wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "#additional-info tr > td")))
                        extract_data(html=driver.page_source, category=category, data=data)
                        break
                    except Exception as e:
                        print("retrying to get product details")
                        # print(e, end="\n\n")
        
            save_to_csv(file_path=f"data/ubuy_{category}.csv", data=data, category=category, processed_categories=processed_categories)
            save_visted_url(file_path=f"cache/ubuy_visited_{category}_urls.txt", visited_urls=visited_urls)
            
            # Move to the next page
            page_number += 1
            if page_number > max_pages:
                break
            url = url.replace(f"&page={page_number-1}", f"&page={page_number}")
        
        except Exception as e:
            save_to_csv(file_path=f"data/ubuy_{category}.csv", data=data, category=category, processed_categories=processed_categories)
            save_visted_url(file_path=f"cache/ubuy_visited_{category}_urls.txt", visited_urls=visited_urls)
            is_error = True
            current_time = datetime.now()
            print(f"Error while scraping ubuy, page {page_number} of {category}:")
            print(e)
            logging.error(f"{current_time} : Error on page {page_number} of {category}: {url}:")
            logging.error(e)
            break 
    
    return is_error


def main():
    #Tracks categories to prevent redundant CSV headers.
    processed_categories = set()

    errors = []

    load_dotenv()

    # Access environment variable
    rotating_proxy_domain_name = os.getenv("ROTATING_PROXY_DOMAINE_NAME_2")
    rotating_proxy_port = os.getenv("ROTATING_PROXY_PORT_2")

    logging.basicConfig(filename="logs/ubuy_scraping_errors.log", level=logging.ERROR)

    proxy = Proxy({
        "proxyType": ProxyType.MANUAL,
        "httpProxy": f"http://{rotating_proxy_domain_name}:{rotating_proxy_port}",
        "sslProxy": f"http://{rotating_proxy_domain_name}:{rotating_proxy_port}"
    })

    options = webdriver.ChromeOptions()
    options.add_argument("--headless=new")
    options.proxy = proxy
    driver = webdriver.Chrome(options=options)

    targets = [
        {
            "category": "smartphones",
            "url": "https://www.ubuy.ma/en/category/mobile-phones-21453?ref=hm-explore-category&page=1",
            "max_pages": 5
        },
        {
            "category": "laptops",
            "url": "https://www.ubuy.ma/en/search/?ref_p=ser_tp&q=laptops&page=1",
            "max_pages": 5
        },
        {
            "category": "tablets",
            "url": "https://www.ubuy.ma/en/search/?ref_p=ser_tp&q=tablets&page=1",
            "max_pages": 5
        }
    ]

    for target in targets:
        if os.path.exists(f"data/ubuy_{target['category']}.csv"): # if file exists:
            with open(f"data/ubuy_{target['category']}.csv", mode="r") as file:
                if file.read(1): # if file is not empty
                    # ensure that the headers are not written to the csv file as it is not empty
                    processed_categories.add(target["category"])

        print(f"scraping data started for category '{target['category']}' in ubuy")
        error = scrape_data(driver=driver, url=target["url"], category=target["category"], max_pages=target["max_pages"], processed_categories=processed_categories)
        errors.append(error)

        # if no error, then the scraping finished successfully, truncate the cache/ubuy_visited_urls.txt
        if not error:
            print(f"scraping data finished for category {target['category']} in ubuy")
        else:
            print(f"something went worng when scraping data for category {target['category']} in ubuy, please check log and cache files")

    # if no error, then the scraping finished successfully, truncate the cache/ubuy_visited_urls.txt
    if True not in errors:
        for target in targets:
            if os.path.exists(f"cache/ubuy_visited_{target['category']}_urls.txt"):
                with open(f"cache/ubuy_visited_{target['category']}_urls.txt", "w") as f:
                    pass
    
    driver.quit()
    print("scraping data finished for ubuy")


if __name__ == "__main__":
    if not os.path.exists("./data"):
        os.mkdir("./data")

    if not os.path.exists("./cache"):
        os.mkdir("./cache")
        
    if not os.path.exists("./logs"):
        os.mkdir("./logs")

    main()
