import pandas as pd
from sqlalchemy import create_engine
import urllib.parse

USERNAME = "root"
RAW_PASSWORD = "maniNK@2005"
HOST = "localhost"
PORT = "3306"
DATABASE = "supply_chain_db"

PASSWORD = urllib.parse.quote_plus(RAW_PASSWORD)

def run_portfolio_queries():
    print("=" * 60)
    print("📊 RUNNING SUPPLY CHAIN STRATEGIC BI QUERIES")
    print("=" * 60)
    
    try:
        conn_url = f"mysql+mysqlconnector://{USERNAME}:{PASSWORD}@{HOST}:{PORT}/{DATABASE}"
        engine = create_engine(conn_url)
        
        # 📌 Query 1: Shipping Mode Performance Breakdown
        query_1 = """
        SELECT 
            s.`Shipping Mode`,
            COUNT(*) as total_orders,
            SUM(f.late_flag) as late_orders,
            ROUND((SUM(f.late_flag) / COUNT(*)) * 100, 2) as late_delivery_rate,
            ROUND(AVG(f.delay_gap), 2) as avg_delay_days,
            ROUND(SUM(f.`Order Profit Per Order`), 2) as total_profit
        FROM fact_orders f
        JOIN dim_shipping s ON f.shipping_id = s.shipping_id
        GROUP BY s.`Shipping Mode`
        ORDER BY late_delivery_rate DESC;
        """
        
        print("\n📈 METRIC 1: SHIPPING MODE EFFICIENCY & PROFITABILITY")
        print("-" * 60)
        df_shipping = pd.read_sql(query_1, con=engine)
        print(df_shipping.to_string(index=False))
        
        # 📌 Query 2: Fixed spacing column format using backticks `Product Card Id`
        query_2 = """
        SELECT 
            p.`Category Name`,
            COUNT(*) as total_shipped,
            ROUND((SUM(f.late_flag) / COUNT(*)) * 100, 2) as late_rate_percentage,
            ROUND(SUM(f.`Order Profit Per Order`), 2) as net_profit
        FROM fact_orders f
        JOIN dim_product p ON f.`Product Card Id` = p.`Product Card Id`
        GROUP BY p.`Category Name`
        HAVING total_shipped > 1000
        ORDER BY late_rate_percentage DESC
        LIMIT 5;
        """
        
        print("\n\n🚨 METRIC 2: TOP 5 HIGH-RISK PRODUCT CATEGORIES (MIN 1000 SHIPPED)")
        print("-" * 60)
        df_products = pd.read_sql(query_2, con=engine)
        print(df_products.to_string(index=False))
        
        print("\n" + "=" * 60)
        print("🎉 ALL PORTFOLIO QUERIES EXECUTED SUCCESSFULLY IN MYSQL!")
        print("=" * 60)

    except Exception as e:
        print(f"❌ Query execution failed: {e}")

if __name__ == "__main__":
    run_portfolio_queries()