import os
from scraping_scripts.jumiaScraper import main as jumia_main
from scraping_scripts.ubuyScraper import main as ubuy_main

if __name__ == "__main__":
    if not os.path.exists("./data"):
        os.mkdir("./data")

    if not os.path.exists("./cache"):
        os.mkdir("./cache")
    
    # jumia_main()
    ubuy_main()