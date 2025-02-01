from extract_trades import load_client_orders, parse_eml
from reconcile_trades import reconcile_trades
from generate_reports import generate_reports
import sqlite3

def main():
    """Execute full reconciliation process."""
    client_orders = load_client_orders()
    broker_trades = parse_eml()

    if broker_trades.empty:
        print("⚠️ No broker trades found! Ensure .eml files with Excel attachments are in the 'eml_files' directory.")
    else:
        print(f"✅ Successfully extracted {len(broker_trades)} broker trades.")

    # Connect to database
    conn = sqlite3.connect('trades.db')

    # Store client orders and broker trades
    client_orders.to_sql('trades', conn, if_exists='replace', index=False)
    broker_trades.to_sql('broker_trades', conn, if_exists='replace', index=False)

    conn.close()
    print("✅ Data successfully written to trades.db")

    reconcile_trades()
    generate_reports()

if __name__ == "__main__":
    main()
