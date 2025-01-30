import os
from scraping_scripts.ubuyScraper import main as ubuy_main
from scraping_scripts.ebayScraper import main as ebay_main

if __name__ == "__main__":
    if not os.path.exists("./data"):
        os.mkdir("./data")

    if not os.path.exists("./cache"):
        os.mkdir("./cache")
    
    ubuy_main()
    # ebay_main()