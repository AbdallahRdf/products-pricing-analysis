import requests
from dotenv import load_dotenv
import os
import time

load_dotenv()

# Access environment variable
proxy_ip = os.getenv("PROXY_IP")
proxy_port = os.getenv("PROXY_PORT")

proxy = {
    "http": f"http://{proxy_ip}:{proxy_port}",
    "https": f"http://{proxy_ip}:{proxy_port}"
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
