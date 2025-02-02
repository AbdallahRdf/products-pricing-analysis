import os
from scraping_scripts.ubuyScraper import main as ubuy_main
from scraping_scripts.ebayScraper import main as ebay_main
from scraping_scripts.reliancedigitalScraper import main as reliancedigital_main

if __name__ == "__main__":
    if not os.path.exists("./data"):
        os.mkdir("./data")

    if not os.path.exists("./cache"):
        os.mkdir("./cache")
    
    if not os.path.exists("./logs"):
        os.mkdir("./logs")
    
    # ubuy_main()
    # ebay_main()
    reliancedigital_main()