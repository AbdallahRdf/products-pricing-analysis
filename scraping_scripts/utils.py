import requests
from dotenv import load_dotenv
import os
import time
import random
import pandas as pd

def get_with_retries(url: str, headers: dict, proxies: list = [], withProxy: bool = True, retries: int = 5, delay: int = 5):
    proxy = {}
    if withProxy:
        load_dotenv()

        if len(proxies) > 0:
            proxy_username = os.getenv("PROXY_USERNAME")
            proxy_password = os.getenv("PROXY_PASSWORD")
            proxy_address = random.choice(proxies)
        else:
            rotating_proxy_domain_name = os.getenv("ROTATING_PROXY_DOMAINE_NAME")
            rotating_proxy_port = os.getenv("ROTATING_PROXY_PORT")
            proxy_address = f"{rotating_proxy_domain_name}:{rotating_proxy_port}"
            proxy_username = os.getenv("ROTATING_PROXY_USERNAME")
            proxy_password = os.getenv("ROTATING_PROXY_PASSWORD")

        proxy = {
            "http": f"http://{proxy_username}:{proxy_password}@{proxy_address}",
            "https": f"http://{proxy_username}:{proxy_password}@{proxy_address}"
        }

    print(f"Using proxy: {proxy}")

    for attempt in range(retries):
        try:
            if withProxy:
                response = requests.get(url, headers=headers, timeout=10, proxies=proxy)
            else:
                response = requests.get(url, headers=headers, timeout=10)
            response.raise_for_status()
            return response
        except requests.exceptions.RequestException as e:
            print(f"Attempt {attempt + 1} failed: {e}")
            time.sleep(delay)
    raise Exception(f"Failed to fetch {url} after {retries} retries.")


def load_visited_urls(file_path: str) -> set:
    # Load previously visited URLs (if available)
    try:
        with open(file_path, "r") as f:
            return set(map(lambda url: url.strip("\n"), f.readlines()))
    except FileNotFoundError:
        return set()
    

def save_to_csv(file_path: str, data: list, category: str, processed_categories: set) -> None:
    if len(data) > 0:
        df = pd.DataFrame(data)
        header = not (category in processed_categories)
        df.to_csv(file_path, index=False, mode="a", header=header)
        processed_categories.add(category) # ensure headers are only written once
        data.clear()


def save_visted_url(file_path: str, visited_urls: set):
    # Save visited URL
    with open(file_path, "a") as f:
        f.writelines(f"{url}\n" for url in visited_urls)
    visited_urls.clear()

