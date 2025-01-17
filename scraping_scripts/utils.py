import requests
from dotenv import load_dotenv
import os
import time

load_dotenv()

# Access environment variable
username = os.getenv("PROXY_USERNAME")
password = os.getenv("PROXY_PASSWORD")

proxy = {
    "http": f"http://{username}:{password}@161.123.152.115:6360",
    "https": f"http://{username}:{password}@161.123.152.115:6360"
}


def get_with_retries(url: str, headers: dict, retries: int = 5, delay: int = 5):
    for attempt in range(retries):
        try:
            response = requests.get(url, headers=headers, timeout=10, proxies=proxy)
            response.raise_for_status()
            return response
        except requests.exceptions.RequestException as e:
            print(f"Attempt {attempt + 1} failed: {e}")
            time.sleep(delay)
    raise Exception(f"Failed to fetch {url} after {retries} retries.")
