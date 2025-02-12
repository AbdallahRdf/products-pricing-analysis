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
        model = model.strip()
        
        # Remove brand if it appears at the start of the model
        if model.lower().startswith(brand):
            model = model[len(brand):].strip()
    
    return model


def clean_data(df: pd.DataFrame):
    # Make a full copy to avoid SettingWithCopyWarning
    df = df.copy()

    # Drop rows where brand, model, or price is missing
    df = df.dropna(subset=["brand", "model", "price"])

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

    # Remove exact duplicate rows
    df = df.drop_duplicates()

    # If duplicates exist with different prices, keep the one with the minimum price
    df = df.loc[df.groupby(["brand", "model", "processor", "ram", "storage", "scraping_date"])["price"].idxmin()]

    return df


def main():
    data_files = [
        "ebay_laptops.csv",
        "ebay_smartphones.csv",
        "ebay_tablets.csv",
        "flipkart_laptops.csv",
        "flipkart_smartphones.csv",
        "flipkart_tablets.csv",
        "reliancedigital_laptops.csv",
        "reliancedigital_smartphones.csv",
        "reliancedigital_tablets.csv"
    ]

    # Create cleaned_data directory if it doesn’t exist
    os.makedirs("cleaned_data", exist_ok=True)

    for file in data_files:
        df = pd.read_csv(f"data/{file}")
        df = clean_data(df)    
        df.to_csv(f"cleaned_data/{file}", index=False)  # Save cleaned file
        print(f"Saved cleaned file: cleaned_data/{file}")

if __name__ == "__main__":
    main()
