# 📊 E-Commerce Price Analysis & Web Scraping
## 📌 Project Overview
This project automates the **scraping, cleaning, and analysis of product prices** from multiple e-commerce platforms (**eBay, Flipkart, and Reliance Digital**). The goal is to compare prices for **laptops, smartphones, and tablets**, identify trends, and visualize pricing differences.
## 🛠 Features
✅ **Multi-threaded Web Scraping**: Extracts product data from multiple websites in parallel.  
✅ **Data Cleaning & Standardization**: Converts prices to USD, removes duplicates, and formats model names.  
✅ **Price Analysis & Visualization**: Generates histograms, bar charts, and line charts to explore pricing trends. 
## 📂 Project Structure
```
📦 project-root
 ┣ 📂 data                  # Raw scraped data
 ┣ 📂 cache                  # Stores visited URLs if the data scraping process was interrupted 
 ┣ 📂 cleaned_data           # Processed & cleaned datasets
 ┣ 📂 scraping_scripts       # Web scraping scripts
 ┣ 📂 visualization          # Jupyter notebooks for analysis
 ┣ 📂 logs                   # Error logs
 ┣ 📂 cleaning_data_script   # Cleans & standardizes scraped data
 ┣ 📜 main.py                # Runs all scrapers in parallel
 ┣ 📜 requirements.txt       # Dependencies
 ┣ 📜 README.md              # Project documentation
 ┣ 📜 .env.example           # Example configuration for environment variables
 ┣ 📜 .env                   # Configuration file for environment variables (to be created)
```
## 🚀 Installation & Setup
### 1️⃣ Clone the Repository
```bash
git clone https://github.com/your-repo-url.git
cd project-root
```

### 2️⃣ Create a Virtual Environment & Activate It
#### On Windows
```bash
python -m venv venv
venv\Scripts\activate
```
#### On macOS/Linux
```bash
python3 -m venv venv
source venv/bin/activate
```

### 3️⃣ Install Dependencies
```bash
pip install -r requirements.txt
```

### 4️⃣ Set Up the `.env` File
Before running the scraper, you need to configure the `.env` file with your proxy credentials. This project uses environment variables for sensitive information such as proxy settings.

1. Copy the `.env.example` file to create a new `.env` file:
   ```bash
   cp .env.example .env
   ```

2. Open the `.env` file in a text editor and update the values with your actual proxy credentials:
   ```
   # Proxy for eBay
   ROTATING_PROXY_DOMAINE_NAME_EBAY=your_rotating_proxy_domain_for_ebay_scraping
   ROTATING_PROXY_PORT_EBAY=your_rotating_proxy_port_for_ebay_scraping
   ROTATING_PROXY_USERNAME_EBAY=your_rotating_proxy_username_for_ebay_scraping
   ROTATING_PROXY_PASSWORD_EBAY=your_rotating_proxy_password_for_ebay_scraping

   # Proxy for Reliance Digital
   PROXY_USERNAME_RELIANCE_DIGITAL=your_proxy_username_for_reliance_digital_scraping
   PROXY_PASSWORD_RELIANCE_DIGITAL=your_proxy_password_for_reliance_digital_scraping

   # A list of proxies to be used when scraping Reliance Digital
   PROXY_LIST=proxy1:port1,proxy2:port2,proxy3:port3
   ```

   Replace the placeholder values (`your_*`) with your actual proxy credentials.

### 5️⃣ Run the Scraper
Once the `.env` file is configured, you can start the scraping process:
```bash
python main.py
```
This will start scraping data from eBay, Flipkart, and Reliance Digital simultaneously.

### 6️⃣ Clean & Process Data
After the scraping is complete, clean and standardize the data:
```bash
python ./cleaning_data_scripts/cleaning_data_script.py
```
This script converts currency, removes duplicates, and standardizes model names.

### 7️⃣ Run Analysis & Visualization
Open the Jupyter Notebook in `visualization/` and run the provided analysis code to generate visualizations.

## 📊 Example Visualizations
- **Price Distribution:** Compare how prices vary between platforms.
- **Average Prices:** See which platform offers the best deals.
- **Price Trends:** Track price changes over time.

## 🛠 Technologies Used
- **Python** 🐍
- **Selenium & Requests** 🌐 (for web scraping)
- **Pandas & NumPy** 📊 (for data processing)
- **Seaborn & Matplotlib** 📈 (for visualizations)
- **Threading** ⚡ (for parallel execution)

---
📝 **Feel free to suggest improvements or contribute to the project!** 🚀
