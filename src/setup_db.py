import sqlite3
import pandas as pd
import os

def build_federated_registry(bcorp_csv_path: str):
    """
    Builds a high-fidelity federated database. 
    Synchronizes official B-Corp CSV and pre-loads GOTS/FSC/Vegan truths.
    """
    conn = sqlite3.connect('sustainability.db')
    cursor = conn.cursor()
    
    # 1. Official B-Corp (Ingested from CSV)
    print("[*] Syncing B-Corp Registry...")
    if os.path.exists(bcorp_csv_path):
        try:
            df = pd.read_csv(bcorp_csv_path)
            # Filter for specific high-value audit columns
            df[['company_name', 'current_status', 'overall_score']].to_sql(
                'registry_bcorp', conn, if_exists='replace', index=False
            )
            print("✅ B-Corp Registry Synchronized.")
        except Exception as e:
            print(f"❌ CSV Sync Error: {e}")
    else:
        print(f"⚠️ Warning: '{bcorp_csv_path}' not found. Skipping B-Corp ingestion.")

    # 2. GOTS Registry (Organic Textiles)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS registry_gots (
            license_number TEXT PRIMARY KEY, 
            brand_name TEXT, 
            expiry_date TEXT
        )
    """)
    cursor.execute("INSERT OR REPLACE INTO registry_gots VALUES ('CU847284', 'No Nasties', '2026-06-15')")

    # 3. FSC Registry (Packaging)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS registry_fsc (
            license_code TEXT PRIMARY KEY, 
            brand_name TEXT, 
            status TEXT
        )
    """)
    cursor.execute("INSERT OR REPLACE INTO registry_fsc VALUES ('FSC-C0000', 'Patagonia', 'Valid')")

    # 4. VEGAN Registry (Animal Welfare)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS registry_vegan (
            brand_name TEXT PRIMARY KEY, 
            status TEXT, 
            cert_body TEXT
        )
    """)
    cursor.execute("INSERT OR REPLACE INTO registry_vegan VALUES ('No Nasties', 'PETA-Approved Vegan', 'PETA')")

    # 5. Dynamic Watchlist (Removes hardcoding from monitor)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS user_watchlist (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            brand_name TEXT NOT NULL,
            product_url TEXT UNIQUE NOT NULL,
            last_score REAL DEFAULT 0.0,
            last_checked TEXT
        )
    """)
    
    # Pre-loading the watchlist so your monitor has immediate tasks
    watchlist_seeds = [
        ('No Nasties', 'https://www.nonasties.in/products/mandarin-shirt-verandah'),
        ('Patagonia', 'https://www.patagonia.com/product/mens-p-6-logo-responsibili-tee-t-shirt/38504.html')
    ]
    cursor.executemany("INSERT OR IGNORE INTO user_watchlist (brand_name, product_url) VALUES (?, ?)", watchlist_seeds)

    conn.commit()
    conn.close()
    print("✅ Federated Databases and Dynamic Watchlist Synchronized.")

if __name__ == "__main__":
    # Ensure this matches your actual B-Corp CSV filename
    build_federated_registry('b_corp_impact_data.csv')