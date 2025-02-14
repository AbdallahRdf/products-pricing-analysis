import pandas as pd
import re
import os

def clean_price(price):
    """ Remove currency symbols and convert various currencies to USD """
    
    # Exchange rates (update as needed)
    EXCHANGE_RATES = {
        "EUR": 1.04,  # 1 EUR = 1.04 USD
        "GBP": 1.24,  # 1 GBP = 1.24 USD
        "AU": 0.63,   # 1 AUD = 0.63 USD
        "C": 0.74,    # 1 CAD = 0.74 USD
        "₹": 0.01     # 1 INR = 0.01 USD
    }

    if not isinstance(price, str) or not price.strip():
        return None  # Return None for missing or invalid values

    # Detect currency
    coefficient = 1
    for currency, rate in EXCHANGE_RATES.items():
        if currency in price:
            coefficient = rate
            break  # Stop checking after finding the currency

    # Remove non-numeric characters (except . and , for decimals)
    cleaned_price = re.sub(r"[^\d.,]", "", price).replace(",", "")

    try:
        price_value = float(cleaned_price) * coefficient
        return round(price_value, 2)
    except ValueError:
        return None  # Return None if conversion fails


def clean_model(row):
    """Remove brand name from model if it appears at the start."""
    brand, model = row["brand"], row["model"]
    
    if isinstance(brand, str) and isinstance(model, str):
        brand = brand.strip().lower()
        model = model.split(",")[0]
        "".join(model)
        model = model.replace("(2024) with Touch screen", "").strip()
        
        
        # Remove brand if it appears at the start of the model
        if model.lower().startswith(brand):
            model = model[len(brand):].strip()
    
    return model


def clean_processor(processor):
    """Extracts and standardizes the processor name, removing extra details."""
    if not isinstance(processor, str):
        return None  # Handle missing values gracefully

    # Remove cache, frequency details, AI terms, and redundant words
    processor = re.sub(r"\(.*?\)", "", processor)  # Remove anything inside parentheses
    processor = re.sub(r"\b(up to|GHz|Turbo Frequency|Base Frequency|Cache|Threads|Cores|TOPs|AI)\b", "", processor, flags=re.IGNORECASE)
    
    # Remove surrounding quotes if present
    processor = processor.strip(".").replace(":","").strip('"').strip()

    processor = processor.split(",")
    processor = processor[0] if len(processor) == 1 or len(processor[0]) > len(processor[1]) else processor[1]
    "".join(processor)

    # Remove "Processor", "Mobile Processor", "CPU", etc.
    processor = re.sub(r"\b(Processor|Mobile Processor|CPU)\b", "", processor, flags=re.IGNORECASE)

    processor = re.sub(r"\s+", " ", processor).strip()
    processor = re.sub(r"^\d+.\d+", " ", processor).strip()

    return processor


def clean_data(df: pd.DataFrame):
    # Make a full copy to avoid SettingWithCopyWarning
    df = df.copy()

    # Clean RAM and storage by removing 'Up to' and 'GB'
    df["ram"] = df["ram"].str.replace(r"Up to|\s?GB", "", regex=True).str.strip()
    df["storage"] = df["storage"].str.replace(r"Up to|\s?GB", "", regex=True).str.strip()

    # Convert RAM and storage to numeric
    df["ram"] = pd.to_numeric(df["ram"], errors="coerce")
    df["storage"] = pd.to_numeric(df["storage"], errors="coerce")

    # Fill missing RAM and storage with mode (most common value)
    df["ram"] = df["ram"].fillna(df["ram"].mode().iloc[0])
    df["storage"] = df["storage"].fillna(df["storage"].mode().iloc[0])

    # Convert back to 'XX GB' format
    df["ram"] = df["ram"].astype(int).astype(str) + " GB"
    df["storage"] = df["storage"].astype(int).astype(str) + " GB"

    df["price"] = df["price"].apply(clean_price)
    df["model"] = df.apply(clean_model, axis=1)

    df["processor"] = df["processor"].apply(clean_processor)

    # Convert all string columns to lowercase
    df = df.map(lambda x: x.lower() if isinstance(x, str) else x)

    # Drop rows where brand, model, or price is missing
    df["model"] = df["model"].astype(str).fillna("")
    df = df.dropna(subset=["brand", "model", "price"])

    # Remove exact duplicate rows
    df = df.drop_duplicates()

    # If duplicates exist with different prices, keep the one with the minimum price
    df = df.loc[df.groupby(["brand", "model", "processor", "ram", "storage", "scraping_date"])["price"].idxmin()]

    return df


def main():

    data_files = {
        "smartphones": [
            "ebay_smartphones.csv",
            "flipkart_smartphones.csv",
            "reliancedigital_smartphones.csv"
        ],
        "laptops": [
            "ebay_laptops.csv",
            "flipkart_laptops.csv",
            "reliancedigital_laptops.csv"
        ],
        "tablets": [
            "ebay_tablets.csv",
            "flipkart_tablets.csv",
            "reliancedigital_tablets.csv"
        ]
    }

    # Create cleaned_data directory if it doesn’t exist
    os.makedirs("cleaned_data", exist_ok=True)

    for category, file_list in data_files.items():
        header = True
        for file in file_list:
            df = pd.read_csv(f"data/{file}")
            df = clean_data(df)    
            df.to_csv(f"cleaned_data/{category}.csv", index=False, header=header, mode=("w" if header else "a"))  # Save cleaned file
            header = False
        print(f"Saved cleaned file: cleaned_data/{category}.csv")

if __name__ == "__main__":
    main()
