import os
import threading
from datetime import datetime
from scraping_scripts.ebayScraper import main as ebay_main
from scraping_scripts.reliancedigitalScraper import main as reliancedigital_main
from scraping_scripts.flipkartScraper import main as flipkart_main

if __name__ == "__main__":
    start = datetime.now()

    if not os.path.exists("./data"):
        os.mkdir("./data")

    if not os.path.exists("./cache"):
        os.mkdir("./cache")

    if not os.path.exists("./logs"):
        os.mkdir("./logs")

    scraper_threads = [
        threading.Thread(target=flipkart_main),
        threading.Thread(target=ebay_main),
        threading.Thread(target=reliancedigital_main),
    ]

    for thread in scraper_threads:
        try:
            thread.start()
        except Exception as e:
            print(f"Error starting thread {thread.name}: {e}")

    for thread in scraper_threads:
        try:
            thread.join()
        except Exception as e:
            print(f"Error joining thread {thread.name}: {e}")

    print("All scraping threads have finished.")
    print("\n that took:")
    print(datetime.now() - start)
