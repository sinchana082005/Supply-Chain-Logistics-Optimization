import pandas as pd
from sqlalchemy import create_engine
import urllib.parse  # 👈 Added to safely handle special characters like '@'

# ⚙️ MIGRATION CREDENTIALS CONFIGURATION
USERNAME = "root"
RAW_PASSWORD = "maniNK@2005"  # Your password is perfectly fine here now!
HOST = "localhost"
PORT = "3306"
DATABASE = "supply_chain_db"

# Safely encode the password string so the '@' symbol doesn't break the connection URL
PASSWORD = urllib.parse.quote_plus(RAW_PASSWORD)

CLEAN_DATA_PATH = "output/cleaned_supply_chain.csv"

def migrate_data():
    print("=" * 60)
    print("🗄️ STARTING STEP 3: DATA MIGRATION TO MYSQL (STAR SCHEMA)")
    print("=" * 60)
    
    try:
        # Build connection url cleanly using the encoded password variable
        conn_url = f"mysql+mysqlconnector://{USERNAME}:{PASSWORD}@{HOST}:{PORT}/{DATABASE}"
        engine = create_engine(conn_url)
        
        print("📥 Reading cleaned pipeline data...")
        df = pd.read_csv(CLEAN_DATA_PATH)
        
        # Create a unique key for shipping dimensions
        df['shipping_id'] = df.groupby(['Shipping Mode', 'Days for shipping (real)', 'Days for shipment (scheduled)']).ngroup() + 1

        print("📐 Splitting data into Star Schema Dimension Tables...")
        dim_customer = df[[
            'Customer Id', 'Customer Fname', 'Customer Lname', 
            'Customer Segment', 'Customer City', 'Customer State'
        ]].drop_duplicates(subset=['Customer Id'])
        
        dim_product = df[[
            'Product Card Id', 'Category Name', 'Product Name', 'Product Price'
        ]].drop_duplicates(subset=['Product Card Id'])
        
        dim_shipping = df[[
            'shipping_id', 'Shipping Mode', 'Days for shipping (real)', 
            'Days for shipment (scheduled)'
        ]].drop_duplicates(subset=['shipping_id'])

        print("📊 Extracting Central Fact Table...")
        fact_orders = df[[
            'Order Id', 'Order Item Id', 'Customer Id', 'Product Card Id', 'shipping_id',
            'order date', 'shipping date', 'Order Region', 'Sales', 'Order Profit Per Order',
            'late_flag', 'delay_gap'
        ]]

        print("\n🚀 Streaming datasets directly into MySQL tables...")
        print("👉 Writing table: dim_customer...")
        dim_customer.to_sql('dim_customer', con=engine, if_exists='replace', index=False)
        
        print("👉 Writing table: dim_product...")
        dim_product.to_sql('dim_product', con=engine, if_exists='replace', index=False)
        
        print("👉 Writing table: dim_shipping...")
        dim_shipping.to_sql('dim_shipping', con=engine, if_exists='replace', index=False)
        
        print("👉 Writing table: fact_orders (Streaming 180k+ records)...")
        fact_orders.to_sql('fact_orders', con=engine, if_exists='replace', index=False)
        
        print("\n🎉 SUCCESS: Data pipeline has built your relational model inside MySQL!")
        print("=" * 60)
        
    except Exception as e:
        print(f"❌ Migration failed: {e}")

if __name__ == "__main__":
    migrate_data()