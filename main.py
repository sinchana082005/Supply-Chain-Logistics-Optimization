import pandas as pd
import numpy as np

FILE_PATH = "data/DataCoSupplyChainDataset.csv"
OUTPUT_PATH = "output/cleaned_supply_chain.csv"

def run_cleaning_pipeline():
    print("=" * 60)
    print("🧹 STARTING STEP 2: DATA CLEANING & FEATURE ENGINEERING")
    print("=" * 60)
    
    try:
        # Load the raw dataset
        df = pd.read_csv(FILE_PATH, encoding="latin1")
        print("📥 Raw data loaded successfully.")
        
        # 1. Deduplication
        initial_rows = len(df)
        df.drop_duplicates(inplace=True)
        print(f"✨ Step 1/5: Checked for duplicates. Dropped {initial_rows - len(df)} duplicate rows.")
        
        # 2. Date Standardization (Using the exact matched headers)
        print("📅 Step 2/5: Converting date features to proper datetime formatting...")
        df['order date'] = pd.to_datetime(df['order date (DateOrders)'], errors='coerce')
        df['shipping date'] = pd.to_datetime(df['shipping date (DateOrders)'], errors='coerce')
        
        # 3. Feature Engineering - Calculate Delivery Delay Gap
        print("⚙️ Step 3/5: Engineering 'delay_gap' operational metric...")
        df['delay_gap'] = df['Days for shipping (real)'] - df['Days for shipment (scheduled)']
        
        # 4. Feature Engineering - Create Late Delivery Flag
        print("🚩 Step 4/5: Flagging late deliveries (1 = Late, 0 = On Time)...")
        df['late_flag'] = np.where(df['delay_gap'] > 0, 1, 0)
        
        # 5. Handle Critical Missing Values contextually
        print("🩹 Step 5/5: Resolving operational missing text values...")
        df['Customer Lname'] = df['Customer Lname'].fillna('')
        df['Product Description'] = df['Product Description'].fillna('No Description')
        
        # Validation Checks
        print("\n" + "-" * 40)
        print("🔬 PIPELINE VALIDATION CHECKS")
        print("-" * 40)
        late_counts = df['late_flag'].value_counts(normalize=True) * 100
        print(f"On-Time Deliveries (0): {late_counts.get(0, 0):.2f}%")
        print(f"Late Deliveries (1):    {late_counts.get(1, 0):.2f}%")
        print(f"Average Shipping Delay: {df['delay_gap'].mean():.2f} days")
        
        # Exporting data to the output directory
        print("-" * 40)
        print(f"💾 Saving cleaned data to: {OUTPUT_PATH}")
        df.to_csv(OUTPUT_PATH, index=False)
        print("🎉 STEP 2 PIPELINE RUN SUCCESSFUL!")
        print("=" * 60)
        
    except Exception as e:
        print(f"❌ Pipeline broke during processing: {e}")

if __name__ == "__main__":
    run_cleaning_pipeline()